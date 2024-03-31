from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import bpy
from mathutils import Matrix, Vector

from .. import log as logging
from ..io.animation.chunks import MeshChunk, NodeChunk, SkinningInfoChunk, Submesh
from ..io.animation.xact import ResourceAnimationActor as Xact, eCWrapper_emfx2Actor
from ..util import bone_correction_matrix, bone_correction_matrix_inv, get_child_nodes, read_genome_file, \
    similar_values_iter, to_blend_quat, to_blend_vec, to_blend_vec2_tuple, \
    to_blend_vec_tuple, to_blend_vec_tuple_transform

logger = logging.getLogger(__name__)


@dataclass
class _ImportState:
    context: bpy.types.Context
    global_scale: float
    global_matrix: Matrix
    show_bone_names: bool
    show_bone_axes: bool
    bake_transform: bool


def load_xact(context: bpy.types.Context, filepath: Path, actor_name: str, global_scale: float, global_matrix: Matrix,
              show_bone_names: bool, show_bone_axes: bool, bake_transform: bool):
    name = actor_name if actor_name else filepath.stem
    xact = read_genome_file(filepath, Xact)

    # Create and select object for actor
    # TODO: With this approach meshes are not deleted properly (on reimport they get .001 prefix)
    actor_obj = bpy.data.objects.new(name, None)
    context.scene.collection.objects.link(actor_obj)
    context.view_layer.objects.active = actor_obj
    actor_obj.select_set(True)

    state = _ImportState(context, global_scale, global_matrix, show_bone_names, show_bone_axes, bake_transform)

    armature_obj = _import_armature(name, xact, state)
    armature_obj.parent = actor_obj
    # context.scene.collection.objects.link(armature_obj)

    for mesh_obj in _import_meshes(name, xact.actor, armature_obj, state):
        mesh_obj.parent = actor_obj
        context.scene.collection.objects.link(mesh_obj)


def _import_meshes(name: str, actor: eCWrapper_emfx2Actor, armature_obj: bpy.types.Object, state: _ImportState) \
        -> list[bpy.types.Object]:
    nodes = actor.get_chunks_by_type(NodeChunk)
    skinning = actor.get_chunk_by_type(SkinningInfoChunk)

    meshes = []
    mesh_chunk = actor.get_chunk_by_type(MeshChunk)
    for submesh in mesh_chunk.submeshes:
        mesh_name = f'{name}_p{mesh_chunk.submeshes.index(submesh)}'
        mesh = _import_mesh(mesh_name, submesh, state)
        if mesh is None:
            continue
        mesh_obj = bpy.data.objects.new(mesh_name, mesh)
        # TODO: Optionally bake transform of global matrix instead?
        if not state.bake_transform:
            mesh_obj.matrix_basis = state.global_matrix
        _import_skinning(submesh, nodes, skinning, mesh_obj, armature_obj)
        meshes.append(mesh_obj)
    return meshes


def _import_mesh(mesh_name: str, submesh: Submesh, state: _ImportState) -> bpy.types.Mesh | None:
    mesh = bpy.data.meshes.new(mesh_name)

    # Vertices and faces
    vertices = [to_blend_vec_tuple(v.position) for v in submesh.vertices]
    if state.bake_transform:
        vertices = [to_blend_vec_tuple_transform(v.position, state.global_matrix) for v in submesh.vertices]
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
            uv_layer.uv[i].vector = to_blend_vec2_tuple(submesh.vertices[vert_index].uv_sets[uv_set])

    return mesh


def _import_skinning(submesh: Submesh, nodes: list[NodeChunk], skinning: SkinningInfoChunk,
                     mesh_obj: bpy.types.Object, armature_obj: bpy.types.Object):
    # Skinning
    mod: bpy.types.ArmatureModifier = mesh_obj.modifiers.new(armature_obj.name, 'ARMATURE')
    mod.object = armature_obj
    mod.use_vertex_groups = True
    for vertex_index, vertex in enumerate(submesh.vertices):
        for influence in skinning.influences[vertex.org_vertex]:
            node = nodes[influence.node_index]
            # Vertex group names correspond to bone names
            vg = mesh_obj.vertex_groups.get(node.name)
            if vg is None:
                vg = mesh_obj.vertex_groups.new(name=node.name)
            vg.add((vertex_index,), influence.weight, 'REPLACE')


def _import_armature(name: str, xact: Xact, state: _ImportState) -> bpy.types.Object:
    arm_data = bpy.data.armatures.new(name=f'{name}_armature')
    arm_data.show_names = state.show_bone_names
    arm_data.show_axes = state.show_bone_axes
    arm = bpy.data.objects.new(name=f'{name}_armature', object_data=arm_data)
    arm.show_in_front = True

    # Apply global matrix as armature basis
    if not state.bake_transform:
        arm.matrix_basis = state.global_matrix

    state.context.scene.collection.objects.link(arm)
    arm.select_set(True)
    arm.hide_viewport = False

    # Enter Edit mode
    state.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')

    # Import root nodes and their children recursively.
    nodes = xact.actor.get_chunks_by_type(NodeChunk)
    arm_base_matrix = state.global_matrix if state.bake_transform else Matrix()
    for node in nodes:
        if not node.parent:
            _import_armature_node(arm_data, arm_base_matrix, Matrix(), None, node, nodes, state)

    # Exit Edit mode
    bpy.ops.object.mode_set(mode='OBJECT')

    return arm


def _is_helper_joint_root(node: NodeChunk):
    return node.name.endswith('_ROOT')


def _is_helper_joint_end(node: NodeChunk):
    return node.name.endswith('_END')


def _is_helper_joint_slot(node: NodeChunk):
    return node.name.startswith('Slot_')


def _is_obsolete_joint(node: NodeChunk):
    """
    Filter out all nodes which contain _ROOT or _END in their name, and have less
    or equals than two words when split with the seprator '_'. Gothic 3 does the
    same in eCWrapper_emfx2Actor::CleanUpHierachy.

    I suspect that the second condition is to preserve the root *_ROOT node (e.g. Orc_ROOT).
    """
    name = node.name
    return (name.endswith('_ROOT') or name.endswith('_END')) and len(name.split('_')) > 2


def _import_armature_node(arm_data: bpy.types.Armature, parent_matrix: Matrix, parent_correction_matrix_inv: Matrix,
                          parent_bone: Optional[bpy.types.EditBone], node: NodeChunk, nodes: list[NodeChunk],
                          state: _ImportState):
    # TODO: Scale...
    # Oh, the problem is that scale is all zeroes, but what is about scale_orient :/
    local_matrix = Matrix.LocRotScale(to_blend_vec(node.position), to_blend_quat(node.rotation), None)
    bone_matrix = parent_matrix @ parent_correction_matrix_inv @ local_matrix

    children = list(get_child_nodes(node, nodes))

    bone_size = 0.0
    num_childs = 0
    for child in children:
        # _ROOT nodes help us to figure out the length of bones that have multiple children, by ignoring the _ROOT nodes.
        # (For example Hero_Spine_Spine_1 with left and right hip _ROOTs).
        # _END nodes help us to figure out the length of bones that have no "real" children.
        if not _is_helper_joint_root(child) and not _is_helper_joint_slot(child):
            bone_size += to_blend_vec(child.position).magnitude
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
        edit_bone = arm_data.edit_bones.new(name=node.name)
        edit_bone.select = True
        edit_bone.tail = bone_tail
        edit_bone.matrix = bone_matrix
        edit_bone.parent = parent_bone
        if parent_bone is not None and similar_values_iter(edit_bone.head, parent_bone.tail, epsilon=1e-3):
            edit_bone.use_connect = True
    else:
        edit_bone = parent_bone

    for child in children:
        _import_armature_node(arm_data, bone_matrix, bone_correction_matrix_inv, edit_bone, child, nodes, state)

# TODO: Attach stuff (slots?) to bone, see link_skeleton_children()...
