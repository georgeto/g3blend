from pathlib import Path
from typing import Optional

import bpy
from mathutils import Matrix, Quaternion, Vector

from .. import log as logging
from ..ksy.xact import Xact
from ..util import bone_correction_matrix, bone_correction_matrix_inv, get_child_nodes, get_chunk_by_type, \
    get_chunks_by_type, read_genomfle, similar_values_iter

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


def load_xact(context: bpy.types.Context, filepath: str, global_scale: float, global_matrix: Matrix,
              show_bone_names: bool, show_bone_axes: bool):
    name = Path(filepath).stem
    xact = read_genomfle(Xact, filepath)

    # Create and select object for actor
    # TODO: With this approach meshes are not deleted properly (on reimport they get .001 prefix)
    actor_obj = bpy.data.objects.new(name, None)
    context.scene.collection.objects.link(actor_obj)
    context.view_layer.objects.active = actor_obj
    actor_obj.select_set(True)

    armature_obj = _import_armature(context, name, xact, global_matrix, show_bone_names, show_bone_axes)
    armature_obj.parent = actor_obj
    # context.scene.collection.objects.link(armature_obj)

    for mesh_obj in _import_meshes(name, xact, armature_obj, global_matrix):
        mesh_obj.parent = actor_obj
        context.scene.collection.objects.link(mesh_obj)


def _import_meshes(name: str, xact: Xact, armature_obj: bpy.types.Object, global_matrix: Matrix) -> list[
    bpy.types.Object]:
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
    # vertices = [_to_blend_vec_tuple_transform(v.position, global_matrix) for v in submesh.vertices]
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


def _import_armature(context: bpy.types.Context, name: str, xact: Xact, global_matrix: Matrix,
                     show_bone_names: bool, show_bone_axes: bool) -> bpy.types.Object:
    arm_data = bpy.data.armatures.new(name=f'{name}_armature')
    arm_data.show_names = show_bone_names
    arm_data.show_axes = show_bone_axes
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
            _import_armature_node(arm_data, Matrix(), Matrix(), None, node, nodes)

    # Exit Edit mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # TODO: Set pose matrix...

    return arm


def _is_helper_joint_root(node: Xact.CnkNode):
    return node.name.data.endswith('_ROOT')


def _is_helper_joint_end(node: Xact.CnkNode):
    return node.name.data.endswith('_END')


def _is_helper_joint_slot(node: Xact.CnkNode):
    return node.name.data.startswith('Slot_')


def _is_obsolete_joint(node: Xact.CnkNode):
    """
    Filter out all nodes which contain _ROOT or _END in their name, and have less
    or equals than two words when split with the seprator '_'. Gothic 3 does the
    same in eCWrapper_emfx2Actor::CleanUpHierachy.

    I suspect that the second condition is to preserve the root *_ROOT node (e.g. Orc_ROOT).
    """
    name = node.name.data
    return (name.endswith('_ROOT') or name.endswith('_END')) and len(name.split('_')) > 2


def _import_armature_node(arm_data: bpy.types.Armature, parent_matrix: Matrix, parent_correction_matrix_inv: Matrix,
                          parent_bone: Optional[bpy.types.EditBone], node: Xact.CnkNode, nodes: list[Xact.CnkNode]):
    # TODO: Scale...
    # Oh, the problem is that scale is all zeroes, but what is about scale_orient :/
    local_matrix = Matrix.LocRotScale(_to_blend_vec(node.position), _to_blend_quat(node.rotation), None)
    bone_matrix = parent_matrix @ parent_correction_matrix_inv @ local_matrix

    children = list(get_child_nodes(node, nodes))

    bone_size = 0.0
    num_childs = 0
    for child in children:
        # _ROOT nodes help us to figure out the length of bones that have multiple children, by ignoring the _ROOT nodes.
        # (For example Hero_Spine_Spine_1 with left and right hip _ROOTs).
        # _END nodes help us to figure out the length of bones that have no "real" children.
        if not _is_helper_joint_root(child) and not _is_helper_joint_slot(child):
            bone_size += _to_blend_vec(child.position).magnitude
            num_childs += 1

    if num_childs > 0:
        bone_size /= num_childs

    # 0-length bones are automatically collapsed into their parent when you leave edit mode,
    # so this enforces a minimum length.
    bone_tail = Vector((0.0, 1.0, 0.0)) * max(0.01, bone_size)

    # The orientation and tail of bones is irrelevant for animations, at least for the door that is the case.
    # Probably the orientation and size of bones is only relevant if we want to skin a new mesh to a skeleton.
    # Automatic or area select based skinning algorithms probably calculate skinning weights based closeness to bone.

    # Compute bone correction matrix.
    bone_matrix = bone_matrix @ bone_correction_matrix

    if not _is_obsolete_joint(node):
        edit_bone = arm_data.edit_bones.new(name=node.name.data)
        edit_bone.select = True
        edit_bone.tail = bone_tail
        edit_bone.matrix = bone_matrix
        edit_bone.parent = parent_bone
        if parent_bone is not None and similar_values_iter(edit_bone.head, parent_bone.tail, epsilon=1e-3):
            edit_bone.use_connect = True
    else:
        edit_bone = parent_bone

    for child in children:
        _import_armature_node(arm_data, bone_matrix, bone_correction_matrix_inv, edit_bone, child, nodes)

# TODO: Attach stuff (slots?) to bone, see link_skeleton_children()...
