from pathlib import Path

import bpy
from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import ImportHelper

from .helper import AbstractFilePanel, AbstractFileTransformPanel, AxisHelper
from .. import log as logging
from ..operators.io_import_xact import load_xact
from ..util import reset_scene

logger = logging.getLogger(__name__)


class ImportXact(bpy.types.Operator, ImportHelper, AxisHelper):
    """Import from xact file format (.xact)"""
    bl_idname = 'g3blend.io_import_xact'
    bl_label = 'Import Actor (xact)'
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = '.xact'
    filter_glob: StringProperty(default='*.xact', options={'HIDDEN'})

    reset_scene: BoolProperty(
        name='Reset Scene',
        description='Remove everything from scene before import',
        default=False,
    )

    actor_name: StringProperty(
        name='Actor Name',
        description='By default derived from xact file name, can be overwritten, for example to import an actor twice',
    )

    bake_transform: BoolProperty(
        name='Bake Transform',
        description="Bake space transform into object data, avoids getting unwanted rotations and "
                    "scale to objects because Gothic 3 space is not aligned with Blender's space",
        default=True,
    )

    show_bone_names: BoolProperty(
        name='Display Bone Names',
        description='Show bone names, can later be changed in armature properties',
        default=False,
    )

    show_bone_axes: BoolProperty(
        name='Display Bone Axes',
        description='Show bone axes, can later be changed in armature properties',
        default=False,
    )

    def draw(self, context):
        pass

    def execute(self, context):
        try:
            global_scale, global_matrix = self._global_transform(context)
            if self.reset_scene:
                reset_scene()
            load_xact(context, Path(self.filepath), self.actor_name, global_scale, global_matrix, self.show_bone_names,
                      self.show_bone_axes, self.bake_transform)
            # Reset actor name override on successful import.
            self.actor_name = ''
        except Exception as e:
            self.report({'ERROR'}, f'Error while importing {self.filepath}: {e}')
            logger.exception('Error while importing {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


class G3BLEND_PT_import_xact_transform(AbstractFileTransformPanel):
    TARGET_OPERATOR = ImportXact

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'bake_transform')
        self.draw_transform(layout, operator)


class G3BLEND_PT_import_xact_armature(AbstractFilePanel):
    TARGET_OPERATOR = ImportXact
    bl_label = 'Armature'

    def _draw(self, context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        col = layout.column(heading='Show')
        col.prop(operator, 'show_bone_names', text='Bone Names')
        col.prop(operator, 'show_bone_axes', text='Bone Axes'),


class G3BLEND_PT_import_xact_misc(AbstractFilePanel):
    TARGET_OPERATOR = ImportXact
    bl_label = 'Misc'

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'reset_scene')
        layout.prop(operator, 'actor_name')


classes = (
    ImportXact,
    G3BLEND_PT_import_xact_transform,
    G3BLEND_PT_import_xact_armature,
    G3BLEND_PT_import_xact_misc,
)
