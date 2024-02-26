from pathlib import Path
from typing import Optional

import bpy
from mathutils import Vector, Matrix, Quaternion

import g3blend.log as logging
from g3blend.ksy.xact import Xact
from g3blend.util import read_genomfle, get_chunks_by_type, get_chunk_by_type, similar_values_iter, get_child_nodes

logger = logging.getLogger(__name__)


def _to_blend_quat(quat: Xact.Quaternion) -> Quaternion:
    return Quaternion((quat.w, quat.x, quat.y, quat.z))


def _to_blend_vec_tuple(vector: Xact.Vector) -> tuple[float, float, float]:
    return vector.x, vector.y, vector.z


def _to_blend_vec_tuple_transform(vector: Xact.Vector, transform: Matrix) -> tuple[float, float, float]:
    vec = _to_blend_vec(vector)
    vec = transform @ vec
    return vec.x, vec.y, vec.z


def _to_blend_vec(vector: Xact.Vector) -> Vector:
    return Vector((vector.x, vector.y, vector.z))


def _to_blend_vec2_tuple(vector: Xact.Vector2) -> tuple[float, float]:
    return vector.x, vector.y


def load_xact(context: bpy.types.Context, filepath: str, global_scale: float, global_matrix: Matrix):
    name = Path(filepath).stem
    xact = read_genomfle(Xact, filepath)

    # Create and select object for actor
    # TODO: With this approach meshes are not deleted properly (on reimport they get .001 prefix)
    actor_obj = bpy.data.objects.new(name, None)
    context.scene.collection.objects.link(actor_obj)
    context.view_layer.objects.active = actor_obj
    actor_obj.select_set(True)

    armature_obj = _import_armature(context, name, xact, global_matrix)
    armature_obj.parent = actor_obj
    #context.scene.collection.objects.link(armature_obj)


    for mesh_obj in _import_meshes(name, xact, armature_obj, global_matrix):
        mesh_obj.parent = actor_obj
        context.scene.collection.objects.link(mesh_obj)


def _import_meshes(name: str, xact: Xact, armature_obj: bpy.types.Object, global_matrix: Matrix) -> list[bpy.types.Object]:
    nodes = get_chunks_by_type(Xact.CnkNode, xact.actor.chunks)
    skinning = get_chunk_by_type(Xact.CnkSkinninginfo, xact.actor.chunks)

    meshes = []
    mesh_chunk = get_chunk_by_type(Xact.CnkMesh, xact.actor.chunks)
    for submesh in mesh_chunk.submeshes:
        mesh_name = f'{name}_p{mesh_chunk.submeshes.index(submesh)}'
        mesh = _import_mesh(mesh_name, submesh, global_matrix)
        if mesh is None:
            continue
        mesh_obj = bpy.data.objects.new(mesh_name, mesh)
        # # TODO: Optionally bake transform of global matrix instead?
        mesh_obj.matrix_basis = global_matrix
        _import_skinning(submesh, nodes, skinning, mesh_obj, armature_obj)
        meshes.append(mesh_obj)
    return meshes


def _import_mesh(mesh_name: str, submesh: Xact.Submesh, global_matrix: Matrix) -> bpy.types.Mesh | None:
    mesh = bpy.data.meshes.new(mesh_name)

    # Vertices and faces
    vertices = [_to_blend_vec_tuple(v.position) for v in submesh.vertices]
    # # TODO: Optionally bake transform of global matrix?
    #vertices = [_to_blend_vec_tuple_transform(v.position, global_matrix) for v in submesh.vertices]
    assert len(submesh.indices) % 3 == 0
    faces = list(zip(*([iter(submesh.indices)] * 3), strict=True))
    mesh.from_pydata(vertices, [], faces)
    if mesh.validate(verbose=True):
        # Avoid crash
        logger.error("INVALID MESH {}", mesh_name)
        return None

    # UVSets
    for uv_set in range(submesh.num_uv_sets):
        uv_layer = mesh.uv_layers.new(name=str(uv_set), do_init=False)
        assert len(submesh.indices) == len(uv_layer.uv)
        for i, vert_index in enumerate(submesh.indices):
            uv_layer.uv[i].vector = _to_blend_vec2_tuple(submesh.vertices[vert_index].uv_sets[uv_set])

    return mesh


def _import_skinning(submesh: Xact.Submesh, nodes: list[Xact.CnkNode], skinning: Xact.CnkSkinninginfo,
                     mesh_obj: bpy.types.Object, armature_obj: bpy.types.Object):
    # Skinning
    mod: bpy.types.ArmatureModifier = mesh_obj.modifiers.new(armature_obj.name, 'ARMATURE')
    mod.object = armature_obj
    mod.use_vertex_groups = True
    for vertex_index, vertex in enumerate(submesh.vertices):
        for influence in skinning.influences[vertex.org_vertex].influences:
            node = nodes[influence.node_index]
            # Vertex group names correspond to bone names
            vg = mesh_obj.vertex_groups.get(node.name.data)
            if vg is None:
                vg = mesh_obj.vertex_groups.new(name=node.name.data)
            vg.add((vertex_index,), influence.weight, 'REPLACE')


def _import_armature(context: bpy.types.Context, name: str, xact: Xact, global_matrix: Matrix) -> bpy.types.Object:
    arm_data = bpy.data.armatures.new(name=f'{name}_armature')
    #arm_data.show_names = True
    #arm_data.show_axes = True
    arm_data.display_type = 'STICK'
    arm = bpy.data.objects.new(name=f'{name}_armature', object_data=arm_data)
    arm.show_in_front = True

    # Apply global matrix as armature basis
    # TODO: Optionally bake transform of global matrix instead?
    arm.matrix_basis = global_matrix

    context.scene.collection.objects.link(arm)
    arm.select_set(True)
    arm.hide_viewport = False

    # Enter Edit mode
    context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')

    # Import root nodes and their children recursively.
    nodes = get_chunks_by_type(Xact.CnkNode, xact.actor.chunks)
    for node in nodes:
        if not node.parent.data:
            _import_armature_node(arm_data, Matrix(), None, node, nodes)

    # Exit Edit mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # TODO: Set pose matrix...

    return arm


def _is_obsolete_joint(node: Xact.CnkNode):
    """
    Filter out all nodes which contain _ROOT or _END in their name, and have less
    or equals than two words when split with the seprator '_'. Gothic 3 does the
    same in eCWrapper_emfx2Actor::CleanUpHierachy.

    I suspect that the second condition is to preserve the root *_ROOT node (e.g. Orc_ROOT).
    """
    name = node.name.data
    return (name.endswith('_ROOT') or name.endswith('_END')) and len(name.split('_')) > 2


def _import_armature_node(arm_data: bpy.types.Armature, parent_matrix: Matrix, parent_bone: Optional[bpy.types.EditBone],
                          node: Xact.CnkNode, nodes: list[Xact.CnkNode]):
    # TODO: Scale...
    # Oh, the problem is that scale is all zeroes, but what is about scale_orient :/
    local_matrix = Matrix.LocRotScale(_to_blend_vec(node.position), _to_blend_quat(node.rotation), None)
    bone_matrix = parent_matrix @ local_matrix

    children = list(get_child_nodes(node, nodes))

    # From FBX
    # So that our bone gets its final length, but still Y-aligned in armature space.
    # 0-length bones are automatically collapsed into their parent when you leave edit mode,
    # so this enforces a minimum length.
    # TODO: bone.tail (distance to bones, see __CalcBoneBoundBox and collect_armature_meshes)
    bone_size = 0.0
    #for child in children:
    #    bone_size += _to_blend_vec(child.position).magnitude
    #if len(children):
    #    bone_size /= len(children)

    # OHHHHHH, finally I get it!
    # TODO: _ROOT and _END are there to describe bones.

    # The algorithm to connect bones is to search in their orientation direction for intersections with other bones (see __CalcBoneBoundBox in KrxAscImp).
    # The algorith works great with Scavenger (_ROOT and _END), also for the door it is fine I guess, the bones are just not connected there...
    # Nah, the bone length is weird, for example Door_ROOT does not make much sense I guess.

    # The orientation and tail of bones is irrelevant for animations, at least for the door that is the case.
    # Probably the orientation and size of bones is only relevant if we want to skin a new mesh to a skeleton.
    # Automatic or area select based skinning algorithms probably calculate skinning weights based closeness to bone.

    # TODO: Rotate around z axis to match X direction (local bone direction in 3ds max) to Y direction (default local bone direction in blender)

    # TODO: Use FBX find_correction_matrix as inspiration?

    # From KrxImpExp bone_utils.py
    """
    # Matrix to rotate local axes of all bones for better looking of models in Blender which were created in 3ds max.
    # (In 3dsmax any bone lies along its local X direction, however in Blender any bone lies along its local Y direction,
    # so we can want to rotate axes around Z direction to match the directions).
    __bone_prep_rotation_matrix = Quaternion(Vector((0,0,1)), pi/2).to_matrix()
    #__bone_prep_rotation_matrix = Matrix.Identity(3) #test
    __bone_prep_rotation_matrix_inverted = __bone_prep_rotation_matrix.inverted()
    """

    obsolete = _is_obsolete_joint(node)

    if not obsolete:
        edit_bone = arm_data.edit_bones.new(name=node.name.data)
        edit_bone.select = True
        edit_bone.tail = Vector((0.0, 0.0, 1.0)) * max(1.0, bone_size)
        edit_bone.matrix = bone_matrix
        edit_bone.parent = parent_bone
        if parent_bone is not None and similar_values_iter(edit_bone.tail, parent_bone.head):
            edit_bone.use_connect = True
    else:
        edit_bone = parent_bone

    for child in children:
        _import_armature_node(arm_data, bone_matrix, edit_bone, child, nodes)

# TODO: Attach stuff (slots?) to bone, see link_skeleton_children()...
