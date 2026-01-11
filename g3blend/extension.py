import functools

import bpy

from bpy.app.handlers import persistent
from bpy.props import CollectionProperty, IntProperty, IntVectorProperty, PointerProperty
from bpy.types import Action, PropertyGroup

from .meta import get_addon_version


class FrameEffectItem(PropertyGroup):
    key_frame: bpy.props.IntProperty(name='Frame')
    effect_name: bpy.props.StringProperty(name='Effect')


class G3blendActionExt(PropertyGroup):
    version: IntVectorProperty(name='Addon version', default=(0, 0, 0), size=3)

    frame_effects: CollectionProperty(type=FrameEffectItem)
    frame_effects_index: IntProperty(default=0)


def initialize_g3blend_ext(action: bpy.types.Action):
    action.g3blend_ext.version = get_addon_version()


def _action_needs_migration(action: bpy.types.Action):
    return tuple(action.g3blend_ext.version) < get_addon_version()


def _migrate_frame_effects(action: bpy.types.Action):
    frame_effects = action.get('frame_effects', None)
    if frame_effects is None:
        return

    items = getattr(frame_effects, 'items', lambda: None)()
    if items is None:
        # The frame_effects property of action must be a dictionary.
        return

    for frame, effect in frame_effects.items():
        frame_effect = action.g3blend_ext.frame_effects.add()
        frame_effect.key_frame = int(frame)
        frame_effect.effect_name = effect

    del action['frame_effects']


def migrate(action: bpy.types.Action):
    if not _action_needs_migration(action):
        return

    version = tuple(action.g3blend_ext.version)
    if version <= (0, 2, 1):
        _migrate_frame_effects(action)

    # Update the version
    action.g3blend_ext.version = get_addon_version()


def _migrate_defer_callback(action_name: str) -> None:
    migrate(bpy.context.blend_data.actions[action_name])


def defer_migrate(action: bpy.types.Action):
    if _action_needs_migration(action):
        bpy.app.timers.register(functools.partial(_migrate_defer_callback, action.name))


def migrate_all(context: bpy.types.Context):
    for action in context.blend_data.actions:
        migrate(action)


@persistent
def _load_post(dummy):
    migrate_all(bpy.context)


@persistent
def _save_pre(dummy):
    migrate_all(bpy.context)


classes = (FrameEffectItem, G3blendActionExt)


def on_register():
    Action.g3blend_ext = PointerProperty(type=G3blendActionExt)

    bpy.app.handlers.load_post.append(_load_post)
    bpy.app.handlers.save_pre.append(_save_pre)


def on_unregister():
    bpy.app.handlers.load_post.remove(_load_post)
    bpy.app.handlers.save_pre.remove(_save_pre)
