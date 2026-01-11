from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import bpy

from mathutils import Matrix

from .. import log as logging
from ..extension import initialize_g3blend_ext
from ..io.animation.chunks import (
    AnimationType,
    InterpolationType,
    KeyFrame,
    KeyFrameChunk,
    MotionPartChunk,
    QuaternionKeyFrame,
    VectorKeyFrame,
)
from ..io.animation.xmot import ResourceAnimationMotion as Xmot
from ..util import (
    action_new_fcurve,
    bone_correction_matrix,
    bone_correction_matrix_inv,
    calc_arm_root_transformation,
    ceil_safe,
    read_genome_file,
    to_blend_quat,
    to_blend_vec,
    trunc_safe,
)


logger = logging.getLogger(__name__)


@dataclass
class _ImportState:
    arm_obj: bpy.types.Object
    action: bpy.types.Action
    action_slot: Optional['bpy.types.ActionSlot']
    fps: float
    root_scale: float
    root_matrix_no_scale: Matrix
    min_frame_time: Optional[float] = None
    max_frame_time: Optional[float] = None

    def update_frame_time(self, frame_time: float):
        if self.min_frame_time is not None:
            self.min_frame_time = min(self.min_frame_time, frame_time)
            self.max_frame_time = max(self.max_frame_time, frame_time)
        else:
            self.min_frame_time = frame_time
            self.max_frame_time = frame_time


def _detect_frame_time(_xmot: Xmot):
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


def _group_motion_parts(xmot: Xmot) -> list[tuple[MotionPartChunk, list[KeyFrameChunk]]]:
    motion_parts = []
    cur_motion_part = None
    cur_key_frames = []

    def push_motion_part():
        if cur_motion_part is not None:
            motion_parts.append((cur_motion_part, cur_key_frames))
        elif cur_key_frames:
            raise ValueError('KeyFrame chunk must be preceded by a MotionPart chunk.')

    for chunk in xmot.motion.chunks:
        if isinstance(chunk, MotionPartChunk):
            push_motion_part()
            cur_motion_part = chunk
            cur_key_frames = []
        elif isinstance(chunk, KeyFrameChunk):
            cur_key_frames.append(chunk)

    push_motion_part()
    return motion_parts


def _import_motion_part(
    chunk: MotionPartChunk, pose_bone: bpy.types.PoseBone, state: _ImportState
) -> tuple[Matrix, Matrix]:
    # This should be the rest matrix (local to parent).
    motion_part_pose_matrix = Matrix.LocRotScale(
        to_blend_vec(chunk.pose_position) * state.root_scale,
        to_blend_quat(chunk.pose_rotation),
        to_blend_vec(chunk.pose_scale),
    )

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
        rest_matrix = state.root_matrix_no_scale.inverted_safe() @ rest_matrix
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

    return pre_matrix, post_matrix


def _import_key_frames(
    animation_type: AnimationType,
    interpolation_type: InterpolationType,
    frames: list[KeyFrame],
    pose_bone: bpy.types.PoseBone,
    pre_matrix: Matrix,
    post_matrix: Matrix,
    state: _ImportState,
    synthesized: bool,
):
    match animation_type:
        # Position
        case AnimationType.Position:
            curve_path = 'location'
            value_extract = lambda v: (
                pre_matrix @ Matrix.Translation(to_blend_vec(v) * state.root_scale) @ post_matrix
            ).to_translation()
            num_channels = 3
        # Rotation
        case AnimationType.Rotation:
            curve_path = 'rotation_quaternion'
            value_extract = lambda v: (pre_matrix @ to_blend_quat(v).to_matrix().to_4x4() @ post_matrix).to_quaternion()
            num_channels = 4
        # Scaling
        case AnimationType.Scaling:
            curve_path = 'scale'
            value_extract = (
                lambda v: (pre_matrix @ Matrix.LocRotScale(None, None, to_blend_vec(v)) @ post_matrix)
                .to_scale()
                .to_3d()
            )
            num_channels = 3
        case _:
            raise ValueError(f'Unsupported animation type: {animation_type}')

    match interpolation_type:
        # Linear
        case InterpolationType.Linear:
            interpolation = 'LINEAR'
        # Bezier
        case InterpolationType.Bezier:
            interpolation = 'BEZIER'
        case _:
            raise ValueError(f'Unsupported interpolation type: {interpolation_type}')

    prop = pose_bone.path_from_id(curve_path)
    curves = [
        action_new_fcurve(state.action, state.action_slot, prop, index=channel, group_name=pose_bone.name)
        for channel in range(num_channels)
    ]

    # TODO: Cycle vs. Extrapolation
    # Pre-allocate all keyframes
    for channel in range(num_channels):
        curves[channel].keyframe_points.add(len(frames))

    # TODO: Proper time/FPS scaling
    for i, frame in enumerate(frames):
        value = value_extract(frame.value)

        for channel in range(num_channels):
            keyframe_point = curves[channel].keyframe_points[i]
            keyframe_point.co = frame.time * state.fps, value[channel]
            keyframe_point.interpolation = interpolation
            if synthesized:
                # Just a visual highlight for synthesized frames, has no functional implication.
                keyframe_point.type = 'JITTER'

        state.update_frame_time(frame.time)

    # Usage of low level API to insert key frames requires manual update afterwards.
    for curve in curves:
        curve.update()


def load_xmot(
    context: bpy.types.Context,
    filepath: Path,
    arm_obj: bpy.types.Object,
    global_scale: float,
    global_matrix: Matrix,
    ignore_transform: bool,
):
    name = filepath.stem
    xmot = read_genome_file(filepath, Xmot)

    if arm_obj is None:
        raise ValueError('No target armature was selected.')

    fps = _detect_frame_time(xmot)

    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    action.use_cyclic = True
    initialize_g3blend_ext(action)

    if not arm_obj.animation_data:
        arm_obj.animation_data_create()

    arm_obj.animation_data.action = action
    action_slot = None
    # Support for Slotted Actions as introduced in Blender 4.4
    if hasattr(arm_obj.animation_data, 'action_slot'):
        # Create an Action Slot. Curves created via action.fcurves will automatically be assigned to it.
        action.slots.new(arm_obj.id_type, arm_obj.name)
        action_slot = action.slots[0]
        arm_obj.animation_data.action_slot = action_slot

    # Store frame effects as custom properties
    action.g3blend_ext.frame_effects.clear()
    for f in xmot.frame_effects:
        frame_effect = action.g3blend_ext.frame_effects.add()
        frame_effect.key_frame = f.key_frame
        frame_effect.effect_name = f.effect_name

    root_scale, root_matrix_no_scale = calc_arm_root_transformation(
        arm_obj.matrix_basis, global_scale, global_matrix, ignore_transform
    )

    state = _ImportState(arm_obj, action, action_slot, fps, root_scale, root_matrix_no_scale)

    for motion_part, key_frames in _group_motion_parts(xmot):
        if motion_part.name not in arm_obj.pose.bones:
            logger.warning('Unknown MotionPart, skipping motion: {}', motion_part.name)
            continue

        pose_bone = arm_obj.pose.bones[motion_part.name]
        pre_matrix, post_matrix = _import_motion_part(motion_part, pose_bone, state)
        for key_frame_chunk in key_frames:
            _import_key_frames(
                key_frame_chunk.animation_type,
                key_frame_chunk.interpolation_type,
                key_frame_chunk.frames,
                pose_bone,
                pre_matrix,
                post_matrix,
                state,
                synthesized=False,
            )

        # If the pose position/rotation/scale (separately) of a bone is constant across the entire animation,
        # there is no key frame chunk for this property. To retain the pose of such a motion part, we have to
        # synthesize a key frame for it (on export we filter out these constant key frames again).
        if not any(f.animation_type == AnimationType.Position for f in key_frames):
            _import_key_frames(
                AnimationType.Position,
                InterpolationType.Linear,
                [VectorKeyFrame(0.0, motion_part.pose_position)],
                pose_bone,
                pre_matrix,
                post_matrix,
                state,
                synthesized=True,
            )

        if not any(f.animation_type == AnimationType.Rotation for f in key_frames):
            _import_key_frames(
                AnimationType.Rotation,
                InterpolationType.Linear,
                [QuaternionKeyFrame(0.0, motion_part.pose_rotation)],
                pose_bone,
                pre_matrix,
                post_matrix,
                state,
                synthesized=True,
            )

    if state.min_frame_time is not None:
        context.scene.frame_start = trunc_safe(state.min_frame_time * fps)
        context.scene.frame_end = ceil_safe(state.max_frame_time * fps)
        context.scene.frame_current = 0
