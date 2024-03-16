from collections import defaultdict
from typing import Any, Optional, Type, TypeVar

import bpy
from mathutils import Matrix, Quaternion, Vector

from .. import log as logging
from ..ksy.xmot import Xmot
from ..util import bone_correction_matrix_inv, find_armature, set_genomfle, write_genomfle

logger = logging.getLogger(__name__)


def _from_str(parent, data: str) -> Xmot.LmaString:
    lma_str = parent.cst(Xmot.LmaString)
    lma_str.data = data
    return lma_str


_C = TypeVar('_C')


def _add_chunk(chunks: Xmot.Chunks, id: Xmot.LmaChunkId, version: int, type: Type[_C]) -> _C:
    chunk = chunks.cst(Xmot.Chunk)
    chunk.chunk_id = id
    chunk.version = version
    chunk.content = chunk.cst(type)
    chunks.chunks.append(chunk)
    return chunk.content


def _from_blend_quat(parent, quat: Quaternion) -> Xmot.Quaternion:
    xquat = parent.cst(Xmot.Quaternion)
    xquat.x = quat.x
    xquat.y = quat.y
    xquat.z = quat.z
    xquat.w = quat.w
    return xquat


def _from_blend_vec(parent, vector: Vector) -> Xmot.Vector:
    xvector = parent.cst(Xmot.Vector)
    xvector.x = vector.x
    xvector.y = vector.y
    xvector.z = vector.z
    return xvector


def save_xmot(context: bpy.types.Context, filepath: str, global_scale: float, global_matrix: Matrix):
    xmot = Xmot()
    xmot.version = 5
    xmot.resource_size = 0
    xmot.resource_priority = 0.0
    xmot.native_file_time = 0  # TODO?
    xmot.native_file_size = 0
    xmot.unk_file_time = 0
    xmot.frame_effects = []

    motion = xmot.motion = xmot.cst(Xmot.Emfx2Motion)
    chunks = motion.chunks = motion.cst(Xmot.Chunks)
    chunks.chunks = []

    # 1. Find armature
    arm_obj = find_armature(context)
    if arm_obj is None:
        raise ValueError('No selected armature found.')

    # 2. Figure out keyframe/animation data for each bone
    action = arm_obj.animation_data.action

    # Action animated values are relative to rest pose, so exactly what we need.
    grouped_curves: dict[str, list[bpy.types.FCurve]] = defaultdict(list)
    for curve in action.fcurves:
        grouped_curves[curve.data_path].append(curve)

    frames_per_bone = {}

    # TODO: Ensure only one track per bone!
    for data_path, curves in grouped_curves.items():
        bone_path, prop_name = data_path.rsplit('.', maxsplit=1)
        pose_bone: bpy.types.PoseBone = arm_obj.path_resolve(bone_path)

        # TODO: Consider rotation mode of object?
        if prop_name == 'location':
            interpolation, frames = _extract_frames_from_curves(curves, 3, Vector)
            animation_type = 'P'
        elif prop_name == 'rotation_quaternion':
            interpolation, frames = _extract_frames_from_curves(curves, 4, Quaternion)
            animation_type = 'R'
        elif prop_name == 'scale':
            interpolation, frames = _extract_frames_from_curves(curves, 3, Vector)
            animation_type = 'S'
        else:
            logger.warning('Unsupported property {} for bone {}.', prop_name, pose_bone.name)
            continue
        # elif prop_name == 'rotation_axis_angle':
        # elif prop_name == 'rotation_euler':

        key = (pose_bone.name, animation_type)
        if key not in frames_per_bone:
            frames_per_bone[key] = (interpolation, frames)
        else:
            logger.warning('More than one track for {}.', key)

        # TODO: Might want to use sampling as an alternative for complex animations with constraints and stuff.

    old_scene_frame_current = context.scene.frame_current
    # TODO: Use scene.frame_start instead?
    # Have to jump to first frame of animation so that pose_bone.matrix_basis is set to value of the first frame.
    context.scene.frame_current = 0

    # 3. Collect all bones in armature
    for pose_bone in reversed(arm_obj.pose.bones):
        bone_obj = pose_bone.bone

        rest_matrix = bone_obj.matrix_local
        # We need the parent relative rest matrix.
        if bone_obj.parent:
            rest_matrix = (bone_obj.parent.matrix_local @ bone_correction_matrix_inv).inverted_safe() @ rest_matrix

        # This derives from the calculation in import_xmot:
        # O = (B @ C)^-1 * (P * C^-1 * X) * C -> X = (P)^-1 * (B @ C) * O * C^-1
        pre_matrix = rest_matrix
        post_matrix = bone_correction_matrix_inv

        # pose position = rest position (edit bone) @ pose base matrix (pose_bone.matrix_basis)
        pose_matrix = pre_matrix @ pose_bone.matrix_basis @ post_matrix

        # matrix_basis = last_motion_part_rest_matrix_inv @ parent_correction_matrix_inv @ last_motion_part_rest_matrix @ bone_correction_matrix

        loc, rot, scale = pose_matrix.decompose()

        motion_part = _add_chunk(chunks, Xmot.LmaChunkId.motionpart, 3, Xmot.CnkMotionPart)
        motion_part.name = _from_str(motion_part, pose_bone.name)
        motion_part.pose_position = _from_blend_vec(motion_part, loc)
        motion_part.pose_rotation = _from_blend_quat(motion_part, rot)
        motion_part.pose_scale = _from_blend_vec(motion_part, scale)
        motion_part.bind_pose_position = _from_blend_vec(motion_part, loc)
        motion_part.bind_pose_rotation = _from_blend_quat(motion_part, rot)
        motion_part.bind_pose_scale = _from_blend_vec(motion_part, scale)

        for animation_type in ['P', 'R', 'S']:
            key = (pose_bone.name, animation_type)
            if key not in frames_per_bone:
                continue

            interpolation, frames = frames_per_bone[key]
            match interpolation:
                # Linear
                case 'LINEAR':
                    interpolation_type = 'L'
                # Bezier
                case 'BEZIER':
                    interpolation_type = 'B'
                case _:
                    logger.warning('Unsupported interpolation: {}', interpolation)
                    continue

            key_frame = _add_chunk(chunks, Xmot.LmaChunkId.anim, 1, Xmot.CnkKeyFrame)
            key_frame.interpolation_type = interpolation_type
            key_frame.animation_type = animation_type
            key_frame.reserverd = 0
            key_frame.frames = []

            match animation_type:
                # Position
                case 'P':
                    value_map = lambda p, v: _from_blend_vec(p, (
                            pre_matrix @ Matrix.Translation(v) @ post_matrix).to_translation())
                    frame_type = Xmot.VectorKeyFrame
                # Rotation
                case 'R':
                    value_map = lambda p, v: _from_blend_quat(p, (
                            pre_matrix @ v.to_matrix().to_4x4() @ post_matrix).to_quaternion())
                    frame_type = Xmot.QuaternionKeyFrame
                # Scaling
                case 'S':
                    value_map = lambda p, v: _from_blend_vec(p, (
                            pre_matrix @ Matrix.LocRotScale(None, None, v) @ post_matrix).to_scale().to_3d())
                    frame_type = Xmot.VectorKeyFrame
                case _:
                    continue

            for time, value in frames:
                xframe = key_frame.cst(frame_type)
                # TODO: Proper time/FPS scaling
                xframe.time = time / 25
                xframe.value = value_map(xframe, value)
                key_frame.frames.append(xframe)

    # Write frame effects.
    strtbl = []
    for frame, effect in _extract_frame_effects(action).items():
        key_frame = int(frame)
        if effect in strtbl:
            strbl_index = strtbl.index(effect)
        else:
            strbl_index = len(strtbl)
            strtbl.append(effect)

        frame_effect = xmot.cst(Xmot.FrameEffect)
        frame_effect.key_frame = key_frame
        frame_effect.effect_name = frame_effect.cst(Xmot.String)
        frame_effect.effect_name.strtab_index = strbl_index
        xmot.frame_effects.append(frame_effect)

    set_genomfle(xmot, strtbl)
    write_genomfle(xmot, filepath)

    # From FBX:
    # For meshes, when armature export is enabled, disable Armature modifiers here!
    # XXX Temp hacks here since currently we only have access to a viewport depsgraph...
    #
    # NOTE: We put armature to the rest pose instead of disabling it so we still
    # have vertex groups in the evaluated mesh.

    # 3. Figure out keyframe/animation data for each bone
    # 4. Export bones with pose position + bind position (both as rest, stored in Bone.matrix_local)
    # 5. Export keyframes, make absolute by multiplying with rest pose.

    # TODO: Two export modes:
    #   - If keyframes have compatible format, directly export the keyframes.
    #     Problem is that this only works for the current action of the object, actions that are not current, cannot be exported like that...
    #   - Otherwise sample the scene for each frame.
    # (see the different variants in `fbx_animations(scene_data):`)

    # Restore scene frame selection
    context.scene.frame_current = old_scene_frame_current


def _extract_frame_effects(action: bpy.types.Action) -> dict[int, str]:
    frame_effects = action.get('frame_effects', None)
    if frame_effects is None:
        return {}

    items = getattr(frame_effects, "items", lambda: None)()
    if items is None:
        logger.error("The frame_effects property of action must be a dictionary.")
        return {}

    return {int(frame): effect for frame, effect in items}


def _extract_frames_from_curves(curves: list[bpy.types.FCurve], num_channels: int, combine) -> Optional[
    tuple[str, list[tuple[float, Any]]]]:
    if len(curves) != num_channels:
        logger.warning('Unexpected number of curves {} vs. {}.', num_channels, len(curves))
        return None

    channels = []
    num_keyframes = None
    curve: bpy.types.FCurve
    for i, curve in enumerate(sorted(curves, key=lambda c: c.array_index)):
        if curve.array_index != i:
            logger.warning('Unexpected curve channel {} vs. {}.', i, curve.array_index)
            return None

        if num_keyframes is None:
            num_keyframes = len(curve.keyframe_points)
        else:
            if num_keyframes != len(curve.keyframe_points):
                logger.warning('Not all channels have same number of frames {} vs. {}.', num_keyframes,
                               len(curve.keyframe_points))
                return None

        channels.append(curve.keyframe_points)

    common_interpolation = None
    key_frames = []
    for i in range(num_keyframes):
        value = combine(tuple(frames[i].co[1] for frames in channels))
        frame_time: float = _all_same((frames[i].co[0] for frames in channels))
        interpolation: str = _all_same((frames[i].interpolation for frames in channels))
        if common_interpolation is None:
            common_interpolation = interpolation
        elif common_interpolation != interpolation:
            logger.warning('Not all frames have same interpolation of frames {} vs. {}.', common_interpolation,
                           interpolation)
            return None
        key_frames.append((frame_time, value))

    return common_interpolation, key_frames


def _all_same(values):
    common = next(values)
    for value in values:
        if value != common:
            raise ValueError('Non common value')
    return common
