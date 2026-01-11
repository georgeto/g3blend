import math

from collections.abc import Iterable
from pathlib import Path
from typing import Optional, TypeVar

import bpy

from bpy.types import Action, FCurve
from bpy_extras.io_utils import axis_conversion
from mathutils import Matrix, Quaternion, Vector

from .io import genome_file
from .io.binary import BinaryReader, BinaryWriter, TBinarySerializable
from .io.property_types.vector import bCVector
from .io.property_types.vector2 import bCVector2
from .io.types.quaternion import bCQuaternion


T = TypeVar('T')


def read_genome_file(
    file: Path, content_type: type[TBinarySerializable], allow_fallback: bool = False
) -> TBinarySerializable:
    return genome_file.read(BinaryReader(Path(file)), content_type, allow_fallback)


def write_genome_file(file: Path, content: TBinarySerializable) -> None:
    writer = BinaryWriter()
    genome_file.write(writer, content)
    file.write_bytes(writer.buf())


def to_blend_quat(quat: bCQuaternion) -> Quaternion:
    return Quaternion((-quat.w, quat.x, quat.z, quat.y))


def to_blend_vec(vector: bCVector) -> Vector:
    return Vector((vector.x, vector.z, vector.y))


def to_blend_vec_tuple(vector: bCVector) -> tuple[float, float, float]:
    return vector.x, vector.z, vector.y


def to_blend_vec_tuple_transform(vector: bCVector, transform: Matrix) -> tuple[float, float, float]:
    vec = to_blend_vec(vector)
    vec = transform @ vec
    return vec.x, vec.y, vec.z


def to_blend_vec2_tuple(vector: bCVector2) -> tuple[float, float]:
    return vector.x, vector.y


def _from_blend_quat(quat: Quaternion) -> bCQuaternion:
    return bCQuaternion(quat.x, quat.z, quat.y, -quat.w)


def _from_blend_vec(vector: Vector) -> bCVector:
    return bCVector(vector.x, vector.z, vector.y)


def get_child_nodes(node: T, nodes: list[T]) -> Iterable[T]:
    return (child for child in nodes if child.parent == node.name)


def similar_values_iter(v1, v2, epsilon=1e-4):
    """Return True if iterables v1 and v2 are nearly the same."""
    return v1 == v2 or all(math.isclose(c1, c2, abs_tol=epsilon) for c1, c2 in zip(v1, v2, strict=False))


def trunc_safe(v, epsilon=1e-4):
    return math.trunc(v + epsilon)


def ceil_safe(v, epsilon=1e-4):
    return math.ceil(v - epsilon)


# Matrix to rotate local axes of all bones for better looking of models in Blender which were created in 3ds max.
# (In 3dsmax any bone lies along its local X direction, however in Blender any bone lies along its local Y direction,
# so we can want to rotate axes around Z direction to match the directions).
bone_correction_matrix = axis_conversion(from_forward='Y', from_up='Z', to_forward='X', to_up='Y').to_4x4()
bone_correction_matrix_inv = bone_correction_matrix.inverted_safe()

toggle_yz_matrix = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))


def without_scale(matrix: Matrix) -> Matrix:
    return Matrix.LocRotScale(matrix.to_translation(), matrix.to_quaternion(), None)


def calc_arm_root_transformation(
    arm_matrix_base: Matrix, global_scale: float, global_matrix: Matrix, ignore_transform: bool
) -> tuple[float | Vector, Matrix]:
    # If the armature transform is identity (e.g. baked) ignore, does not make a difference.
    if not ignore_transform:
        # TODO: Do we care if arm_obj itself is a child of something that has transformation?
        #       Then we would have to use matrix_world.
        root_scale = arm_matrix_base.inverted_safe().to_scale() * global_scale
        root_matrix_no_scale = without_scale(arm_matrix_base).inverted_safe() @ without_scale(global_matrix)
    else:
        # Bone transformation in blender do not store scale, we have to account for that manually.
        root_scale = global_scale
        root_matrix_no_scale = without_scale(global_matrix)
    return root_scale, root_matrix_no_scale


def toogle_handness_quat(quat: Quaternion) -> Quaternion:
    return Quaternion((quat.w, quat.x, quat.z, quat.y))


def toogle_handness_vec(vec: Vector) -> Vector:
    return Vector((vec.x, vec.z, vec.y))


# The equivalent to switching the Y/Z components of Quaternion or Vector.
# Convert transformation matrix between left-handed and right-handed coordinate system.
# See: https://stackoverflow.com/a/12479962
def toogle_handness_matrix(matrix: Matrix) -> Matrix:
    return toggle_yz_matrix @ matrix @ toggle_yz_matrix


def find_armature(context: bpy.types.Context) -> Optional[bpy.types.Object]:
    # TODO: Find actor by name or at least check compatibility?
    actor_obj = context.active_object
    if actor_obj is None:
        return None

    if arm_obj := next((c for c in actor_obj.children if c.type == 'ARMATURE'), None):
        return arm_obj

    if actor_obj.parent:
        return next((c for c in actor_obj.parent.children if c.type == 'ARMATURE'), None)
    return None


# Note: Taken from KrxImpExp
# Reset the current scene
def reset_scene():
    # Remove scenes
    empty_scn = bpy.data.scenes.new('Scene')
    for i in range(len(bpy.data.scenes) - 1, -1, -1):
        scn = bpy.data.scenes[i]
        if scn != empty_scn:
            bpy.data.scenes.remove(scn)

    # Remove objects
    for i in range(len(bpy.data.objects) - 1, -1, -1):
        obj = bpy.data.objects[i]
        if obj.users == 0:
            bpy.data.objects.remove(obj)

    # Remove meshes
    for i in range(len(bpy.data.meshes) - 1, -1, -1):
        msh = bpy.data.meshes[i]
        if msh.users == 0:
            bpy.data.meshes.remove(msh)

    # Remove armatures
    for i in range(len(bpy.data.armatures) - 1, -1, -1):
        arm = bpy.data.armatures[i]
        if arm.users == 0:
            bpy.data.armatures.remove(arm)

    # Remove actions
    for i in range(len(bpy.data.actions) - 1, -1, -1):
        act = bpy.data.actions[i]
        if act.users == 0:
            bpy.data.actions.remove(act)

    # Remove materials
    for i in range(len(bpy.data.materials) - 1, -1, -1):
        mat = bpy.data.materials[i]
        if mat.users == 0:
            bpy.data.materials.remove(mat)

    # Remove textures
    for i in range(len(bpy.data.textures) - 1, -1, -1):
        tex = bpy.data.textures[i]
        if tex.users == 0:
            bpy.data.textures.remove(tex)

    # Remove images
    for i in range(len(bpy.data.images) - 1, -1, -1):
        img = bpy.data.images[i]
        if img.users == 0:
            bpy.data.images.remove(img)


# Note: Taken from FBX importer
# Scale/unit mess. FBX can store the 'reference' unit of a file in its UnitScaleFactor property
# (1.0 meaning centimeter, afaik). We use that to reflect user's default unit as set in Blender with scale_length.
# However, we always get values in BU (i.e. meters), so we have to reverse-apply that scale in global matrix...
# Note that when no default unit is available, we assume 'meters' (and hence scale by 100).
def units_blender_to_g3_factor(scene):
    return 100.0 if (scene.unit_settings.system == 'NONE') else (100.0 * scene.unit_settings.scale_length)


try:
    # Starting with Blender 5.0 the legacy Action API was dropped, but fortunately helper functions is provided to ease
    # transitioning to the new API.
    from bpy_extras.anim_utils import action_ensure_channelbag_for_slot, action_get_channelbag_for_slot

    def action_new_fcurve(
        action: Action, action_slot: 'bpy.types.ActionSlot', data_path: str, index: int, group_name
    ) -> FCurve:
        channelbag = action_ensure_channelbag_for_slot(action, action_slot)
        return channelbag.fcurves.new(data_path, index=index, group_name=group_name)

    def action_get_fcurves(action: Action, action_slot: 'bpy.types.ActionSlot') -> Iterable[FCurve]:
        if channelbag := action_get_channelbag_for_slot(action, action_slot):
            return channelbag.fcurves
        return []

except ImportError:
    # For older versions fall back to the legacy API.
    def action_new_fcurve(action: Action, _: 'bpy.types.ActionSlot', data_path: str, index: int, group_name) -> FCurve:
        return action.fcurves.new(data_path, index=index, action_group=group_name)

    def action_get_fcurves(action: Action, _: 'bpy.types.ActionSlot') -> Iterable[FCurve]:
        return action.fcurves
