import math
from pathlib import Path

import bpy
from mathutils import Matrix

from .. import log as logging
from ..io.animation.chunks import AnimationType, InterpolationType, KeyFrameChunk, MotionPartChunk
from ..io.animation.xmot import ResourceAnimationMotion as Xmot
from ..util import bone_correction_matrix, bone_correction_matrix_inv, calc_arm_root_transformation, find_armature, \
    read_genome_file, to_blend_quat, to_blend_vec

logger = logging.getLogger(__name__)


def _detect_frame_time(xmot: Xmot):
    # TODO: ...
    return 25
    """
    // Determine min and max frame
    float minFrameTime = Float.MAX_VALUE;
    float maxFrameTime = 0;
    for (KeyFrameChunk keyFrameChunk : motion.motion.<KeyFrameChunk>streamChunksByType(LMA_CHUNK.LMA_CHUNK_ANIM)) {
        var track = keyFrameChunk.track;
        Optional<Float> min = StreamEx.of(track).map(f -> f.time).findFirst(v -> v > 0);
        if (min.isPresent() && min.get() < minFrameTime)
            minFrameTime = min.get();

        if (!track.isEmpty())
            maxFrameTime = Math.max(track.get(track.size() - 1).time, maxFrameTime);
    }
    float frameSpeed = minFrameTime != Float.MAX_VALUE ? 1 / minFrameTime : 25.0f;
    if (!Misc.compareFloat(frameSpeed, Math.round(frameSpeed), FRAME_EPSILON))
        throw new IllegalStateException("Detected FrameSpeed " + frameSpeed + " is not an integral value.");
    float lastFrame = maxFrameTime / minFrameTime;
    if (!Misc.compareFloat(lastFrame, Math.round(lastFrame), FRAME_EPSILON))
        throw new IllegalStateException("Detected LastFrame " + lastFrame + " is not an integral value.");
    int numFrames = (Math.round(lastFrame)) + 1;
    """


def load_xmot(context: bpy.types.Context, filepath: str, global_scale: float, global_matrix: Matrix,
              ignore_transform: bool):
    name = Path(filepath).stem
    xmot = read_genome_file(Path(filepath), Xmot)

    arm_obj = find_armature(context)
    if arm_obj is None:
        raise ValueError("No selected armature found.")

    fps = _detect_frame_time(xmot)
    min_frame_time = None
    max_frame_time = None

    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    action.use_cyclic = True
    animation_data = arm_obj.animation_data
    if animation_data is None:
        animation_data = arm_obj.animation_data_create()
    animation_data.action = action

    # Store frame effects as custom properties
    frame_effects = {str(f.key_frame): f.effect_name for f in xmot.frame_effects}
    action["frame_effects"] = frame_effects

    root_scale, root_matrix_no_scale = calc_arm_root_transformation(arm_obj.matrix_basis, global_scale,
                                                                    global_matrix, ignore_transform)

    last_motion_part = None
    for chunk in xmot.motion.chunks:
        # TODO: Should we reset pose matrix (to rest matrix) of bones for which the xmot does not specify a pose matrix?
        if isinstance(chunk, MotionPartChunk):
            last_motion_part = chunk.name
            # This should be the rest matrix (local to parent).
            motion_part_pose_matrix = Matrix.LocRotScale(to_blend_vec(chunk.pose_position) * root_scale,
                                                         to_blend_quat(chunk.pose_rotation),
                                                         to_blend_vec(chunk.pose_scale))

            if last_motion_part not in arm_obj.pose.bones:
                continue

            pose_bone = arm_obj.pose.bones[last_motion_part]
            bone = pose_bone.bone
            # Rest matrices in xact and pose matrices in the xmot are always relative to the parent bone.
            # Whereas rest matrices in Blender are absolute and pose matrices in blender are relative to the
            # rest matrix of the bone.
            # Therefore, we have to calculate the parent relative bone rest matrix,
            # and then calculate rest_matrix.inverted() * motion_part_pose_matrix.
            rest_matrix = bone.matrix_local
            if bone.parent:
                rest_matrix = (bone.parent.matrix_local @ bone_correction_matrix_inv).inverted_safe() @ rest_matrix
            else:
                rest_matrix = root_matrix_no_scale.inverted_safe() @ rest_matrix
            rest_matrix_inv = rest_matrix.inverted_safe()

            # The symmetry here is O = (B * C)^-1 * ((P * C * C^-1 * X) * C)
            # with B * C: Absolute Rest matrix (bone.matrix_local)
            #      C: Correction (bone_correct_matrix),
            #      P * C: Absolute Parent Rest matrix (bone.parent.matrix_local)
            #      X: Xmot Pose matrix (motion_part_pose_matrix)
            #      O: Pose Matrix (pose_bone.matrix_basis)
            pre_matrix = rest_matrix_inv
            post_matrix = bone_correction_matrix
            # Set pose matrix used in xmot (relative to bone's rest matrix).
            pose_bone.matrix_basis = pre_matrix @ motion_part_pose_matrix @ post_matrix
        elif isinstance(chunk, KeyFrameChunk):
            if last_motion_part is None:
                raise ValueError('KeyFrame chunk must be preceded by a MotionPart chunk.')

            if last_motion_part not in arm_obj.pose.bones:
                print('Unknown MotionPart, skipping motion:', last_motion_part)
                continue

            # Lookup bone
            pose_bone = arm_obj.pose.bones[last_motion_part]

            keyframe_chunk = chunk
            match keyframe_chunk.animation_type:
                # Position
                case AnimationType.Position:
                    curve_path = 'location'
                    value_extract = lambda v: (pre_matrix @ Matrix.Translation(
                        to_blend_vec(v) * root_scale) @ post_matrix).to_translation()
                    num_channels = 3
                # Rotation
                case AnimationType.Rotation:
                    curve_path = 'rotation_quaternion'
                    value_extract = lambda v: (
                            pre_matrix @ to_blend_quat(v).to_matrix().to_4x4() @ post_matrix).to_quaternion()
                    num_channels = 4
                # Scaling
                case AnimationType.Scaling:
                    curve_path = 'scale'
                    value_extract = lambda v: (pre_matrix @ Matrix.LocRotScale(None, None, to_blend_vec(
                        v)) @ post_matrix).to_scale().to_3d()
                    num_channels = 3
                case _:
                    print('Unsupported animation type:', keyframe_chunk.animation_type)
                    continue

            match keyframe_chunk.interpolation_type:
                # Linear
                case InterpolationType.Linear:
                    interpolation = 'LINEAR'
                # Bezier
                case InterpolationType.Bezier:
                    interpolation = 'BEZIER'
                case _:
                    print('Unsupported interpolation type:', keyframe_chunk.interpolation_type)
                    continue

            prop = pose_bone.path_from_id(curve_path)
            curves = [action.fcurves.new(prop, index=channel, action_group=pose_bone.name)
                      for channel in range(num_channels)]

            # TODO: Cycle vs. Extrapolation
            # Pre-allocate all keyframes
            for channel in range(num_channels):
                curves[channel].keyframe_points.add(len(keyframe_chunk.frames))

            # TODO: Proper time/FPS scaling
            for i, frame in enumerate(keyframe_chunk.frames):
                value = value_extract(frame.value)

                for channel in range(num_channels):
                    keyframe_point = curves[channel].keyframe_points[i]
                    keyframe_point.co = frame.time * fps, value[channel]
                    keyframe_point.interpolation = interpolation

                if min_frame_time is not None:
                    min_frame_time = min(min_frame_time, frame.time)
                    max_frame_time = max(max_frame_time, frame.time)
                else:
                    min_frame_time = frame.time
                    max_frame_time = frame.time

            # Usage of low level API to insert key frames requires manual update afterwards.
            for curve in curves:
                curve.update()

    if min_frame_time is not None:
        context.scene.frame_start = math.trunc(min_frame_time * fps)
        context.scene.frame_end = math.ceil(max_frame_time * fps)
        context.scene.frame_current = 0
