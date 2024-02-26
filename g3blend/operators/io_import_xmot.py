import math
from pathlib import Path

import bpy
from mathutils import Vector, Matrix, Quaternion

import g3blend.log as logging
from g3blend.ksy.xmot import Xmot
from g3blend.util import read_genomfle, find_armature

logger = logging.getLogger(__name__)


def _to_blend_quat(quat: Xmot.Quaternion) -> Quaternion:
    return Quaternion((quat.w, quat.x, quat.y, quat.z))


def _to_blend_vec_tuple(vector: Xmot.Vector) -> tuple[float, float, float]:
    return vector.x, vector.y, vector.z


def _to_blend_vec(vector: Xmot.Vector) -> Vector:
    return Vector((vector.x, vector.y, vector.z))


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


def load_xmot(context: bpy.types.Context, filepath: str, global_scale: float, global_matrix: Matrix):
    name = Path(filepath).stem
    xmot = read_genomfle(Xmot, filepath)

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

    last_motion_part = None
    bone_matrics = {}
    for chunk in xmot.motion.chunks.chunks:
        if isinstance(chunk.content, Xmot.CnkMotionPart):
            matrix = Matrix.LocRotScale(_to_blend_vec(chunk.content.pose_position),
                                        _to_blend_quat(chunk.content.pose_rotation),
                                        _to_blend_vec(chunk.content.pose_scale))
            bone_matrics[chunk.content.name.data] = matrix

    for chunk in xmot.motion.chunks.chunks:
        if isinstance(chunk.content, Xmot.CnkMotionPart):
            last_motion_part = chunk.content.name.data
            # This should be the rest matrix (local to parent).
            last_motion_part_rest_matrix = Matrix.LocRotScale(_to_blend_vec(chunk.content.pose_position),
                                                              _to_blend_quat(chunk.content.pose_rotation),
                                                              _to_blend_vec(chunk.content.pose_scale))

            if last_motion_part not in arm_obj.pose.bones:
                continue

            pose_bone = arm_obj.pose.bones[last_motion_part]
            # Set pose matrix used in xmot (relative to bone's rest matrix)
            bone = pose_bone.bone
            rest_matrix = bone.matrix_local
            if bone.parent is not None:
                rest_matrix = bone.parent.matrix_local.inverted_safe() @ rest_matrix
            # TODO: Instead we might have to update the rest position on each animation import.
            #       Not sure how stable it is to set pose bone matrix here.
            #       Probably very inconvenient for the animator (might want to use the "Clear Transformations" feature).
            #       Or maybe just create an initial keyframe for all bones without animation?
            last_motion_part_rest_matrix_inv = rest_matrix.inverted_safe()
            pose_bone.matrix_basis = last_motion_part_rest_matrix_inv @ last_motion_part_rest_matrix
        elif isinstance(chunk.content, Xmot.CnkKeyFrame):
            if last_motion_part is None:
                raise ValueError('KeyFrame chunk must be preceded by a MotionPart chunk.')

            if last_motion_part not in arm_obj.pose.bones:
                print('Unknown MotionPart, skipping motion:', last_motion_part)
                continue

            # Lookup bone
            pose_bone = arm_obj.pose.bones[last_motion_part]
            pre_matrix = last_motion_part_rest_matrix_inv
            post_matrix = Matrix()

            keyframe_chunk = chunk.content
            match keyframe_chunk.animation_type:
                # Position
                case 'P':
                    curve_path = 'location'
                    value_extract = lambda v:  (pre_matrix @ Matrix.Translation(_to_blend_vec(v)) @ post_matrix).to_translation()
                    num_channels = 3
                # Rotation
                case 'R':
                    curve_path = 'rotation_quaternion'
                    value_extract = lambda v: (pre_matrix @ _to_blend_quat(v).to_matrix().to_4x4() @ post_matrix).to_quaternion()
                    num_channels = 4
                # Scaling
                case 'S':
                    curve_path = 'scale'
                    value_extract = lambda v: (pre_matrix @ Matrix.LocRotScale(None, None, _to_blend_vec(v)) @ post_matrix).to_translation().to_3d()
                    num_channels = 3
                case _:
                    print('Unsupported animation type:', keyframe_chunk.animation_type)
                    continue

            match keyframe_chunk.interpolation_type:
                # Linear
                case 'L':
                    interpolation = 'LINEAR'
                # Bezier
                case 'B':
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
