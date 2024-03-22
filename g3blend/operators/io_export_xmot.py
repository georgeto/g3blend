from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

import bpy
from mathutils import Matrix, Quaternion, Vector

from .. import log as logging
from ..io.animation.chunks import AnimationType, InterpolationType, KeyFrameChunk, MotionPartChunk, \
    QuaternionKeyFrame, \
    VectorKeyFrame
from ..io.animation.xmot import ResourceAnimationMotion as Xmot, eCWrapper_emfx2Motion, eSFrameEffect
from ..io.types.misc import bCDateTime
from ..util import _from_blend_quat, _from_blend_vec, bone_correction_matrix_inv, calc_arm_root_transformation, \
    find_armature, write_genome_file

logger = logging.getLogger(__name__)


def save_xmot(context: bpy.types.Context, filepath: str, global_scale: float, global_matrix: Matrix,
              ignore_transform: bool, use_selection: bool):
    xmot = Xmot()
    xmot.resource_size = 0
    xmot.resource_priority = 0.0
    xmot.native_file_time = bCDateTime(0)  # TODO?
    xmot.native_file_size = 0
    xmot.unk_file_time = bCDateTime(0)

    motion = xmot.motion = eCWrapper_emfx2Motion()
    motion.chunks = []

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
            animation_type = AnimationType.Position
        elif prop_name == 'rotation_quaternion':
            interpolation, frames = _extract_frames_from_curves(curves, 4, Quaternion)
            animation_type = AnimationType.Rotation
        elif prop_name == 'scale':
            interpolation, frames = _extract_frames_from_curves(curves, 3, Vector)
            animation_type = AnimationType.Scaling
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

    root_scale, root_matrix_no_scale = calc_arm_root_transformation(arm_obj.matrix_basis, global_scale,
                                                                    global_matrix, ignore_transform)
    if isinstance(root_scale, Vector):
        root_scale_inv = Vector((1 / root_scale.x, 1 / root_scale.y, 1 / root_scale.z))
    else:
        root_scale_inv = 1 / root_scale

    # 3. Collect all bones in armature
    selected_pose_bones = context.selected_pose_bones
    for pose_bone in reversed(arm_obj.pose.bones):
        if use_selection and pose_bone not in selected_pose_bones:
            continue

        bone = pose_bone.bone

        rest_matrix = bone.matrix_local
        if bone.parent:
            rest_matrix = (bone.parent.matrix_local @ bone_correction_matrix_inv).inverted_safe() @ rest_matrix
        else:
            rest_matrix = root_matrix_no_scale.inverted_safe() @ rest_matrix

        # This derives from the calculation in import_xmot:
        # O = (B * C)^-1 * ((P * C * C^-1 * X) * C)
        # -> X = (P * C)^-1 * (B * C) * O * C^-1
        # with B * C: Absolute Rest matrix (bone.matrix_local)
        #      C: Correction (bone_correct_matrix),
        #      P * C: Absolute Parent rest matrix (bone.parent.matrix_local)
        #      X: Xmot Pose Matrix (motion_part_pose_matrix)
        #      O: Pos Matrix (pose_bone.matrix_basis)
        pre_matrix = rest_matrix
        post_matrix = bone_correction_matrix_inv

        # pose position = rest position (edit bone) @ pose base matrix (pose_bone.matrix_basis)
        pose_matrix = pre_matrix @ pose_bone.matrix_basis @ post_matrix

        loc, rot, scale = pose_matrix.decompose()

        motion_part = motion.add_chunk(MotionPartChunk)
        motion_part.name = pose_bone.name
        motion_part.pose_position = _from_blend_vec(loc * root_scale_inv)
        motion_part.pose_rotation = _from_blend_quat(rot)
        motion_part.pose_scale = _from_blend_vec(scale)
        motion_part.bind_pose_position = _from_blend_vec(loc * root_scale_inv)
        motion_part.bind_pose_rotation = _from_blend_quat(rot)
        motion_part.bind_pose_scale = _from_blend_vec(scale)

        for animation_type in AnimationType:
            key = (pose_bone.name, animation_type)
            if key not in frames_per_bone:
                continue

            interpolation, frames = frames_per_bone[key]
            match interpolation:
                # Linear
                case 'LINEAR':
                    interpolation_type = InterpolationType.Linear
                # Bezier
                case 'BEZIER':
                    interpolation_type = InterpolationType.Bezier
                case _:
                    logger.warning('Unsupported interpolation: {}', interpolation)
                    continue

            key_frame = motion.add_chunk(KeyFrameChunk)
            key_frame.interpolation_type = interpolation_type
            key_frame.animation_type = animation_type
            key_frame.frames = []

            match animation_type:
                # Position
                case AnimationType.Position:
                    value_map = lambda p, v: _from_blend_vec(
                        (pre_matrix @ Matrix.Translation(v) @ post_matrix).to_translation() * root_scale_inv)
                    frame_type = VectorKeyFrame
                # Rotation
                case AnimationType.Rotation:
                    value_map = lambda p, v: _from_blend_quat(
                        (pre_matrix @ v.to_matrix().to_4x4() @ post_matrix).to_quaternion())
                    frame_type = QuaternionKeyFrame
                # Scaling
                case AnimationType.Scaling:
                    value_map = lambda p, v: _from_blend_vec(
                        (pre_matrix @ Matrix.LocRotScale(None, None, v) @ post_matrix).to_scale().to_3d())
                    frame_type = VectorKeyFrame
                case _:
                    continue

            for time, value in frames:
                xframe = frame_type()
                # TODO: Proper time/FPS scaling
                xframe.time = time / 25
                xframe.value = value_map(xframe, value)
                key_frame.frames.append(xframe)

    # Extract frame effects.
    xmot.frame_effects = [eSFrameEffect(int(frame), effect) for frame, effect in _extract_frame_effects(action).items()]

    write_genome_file(Path(filepath), xmot)

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
