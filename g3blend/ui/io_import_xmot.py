from pathlib import Path

import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, IntProperty, StringProperty
from bpy_extras.io_utils import ImportHelper

from .helper import AbstractFilePanel, AbstractFileTransformPanel, AxisHelper, get_object_for_armature_item, \
    get_target_armature_list_items
from .. import log as logging
from ..operators.io_import_xmot import load_xmot

logger = logging.getLogger(__name__)


class ImportXmot(bpy.types.Operator, ImportHelper, AxisHelper):
    """Import from xmot file format (.xmot)"""
    bl_idname = 'g3blend.io_import_xmot'
    bl_label = 'Import Motion (xmot)'
    bl_options = {'UNDO', 'PRESET'}

    directory: StringProperty(
        subtype='DIR_PATH',
        options={'HIDDEN', 'SKIP_PRESET'},
    )

    filename_ext = '.xmot'
    filter_glob: StringProperty(default='*.xmot', options={'HIDDEN'})

    files: CollectionProperty(
        name='File Path',
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_PRESET'},
    )

    ignore_transform: BoolProperty(
        name='Ignore Transform',
        description='Ignore transform set on the armature object',
        default=False,
    )

    target_armature_index: IntProperty()

    def _set_target_armature(self, item):
        self.target_armature_index = item

    def _get_target_armature(self):
        return self.target_armature_index

    target_armature: EnumProperty(
        name='Target Armature',
        description='Armature for which the animation shall be imported',
        items=get_target_armature_list_items,
        set=_set_target_armature,
        get=_get_target_armature,
    )

    def draw(self, context):
        pass

    def execute(self, context):
        try:
            global_scale, global_matrix = self._global_transform(context)
            target_armature = get_object_for_armature_item(context, self.target_armature)

            if self.files:
                directory = Path(self.directory)
                for f in self.files:
                    filepath = directory / f.name
                    load_xmot(context, filepath, target_armature, global_scale, global_matrix, self.ignore_transform)
            else:
                load_xmot(context, Path(self.filepath), target_armature, global_scale, global_matrix,
                          self.ignore_transform)

            self.target_armature_index = 0
        except Exception as e:
            self.report({'ERROR'}, f'Error while importing {self.filepath}: {e}')
            logger.exception('Error while importing {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


class G3BLEND_PT_import_xmot_import(AbstractFilePanel):
    TARGET_OPERATOR = ImportXmot
    bl_label = 'Import'

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'target_armature')


class G3BLEND_PT_import_xmot_transform(AbstractFileTransformPanel):
    TARGET_OPERATOR = ImportXmot

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'ignore_transform')
        self.draw_transform(layout, operator)


classes = (
    ImportXmot,
    G3BLEND_PT_import_xmot_import,
    G3BLEND_PT_import_xmot_transform,
)
