import bpy
from bpy.props import BoolProperty, CollectionProperty, StringProperty
from bpy_extras.io_utils import ImportHelper

from .helper import AbstractFileTransformPanel, AxisHelper
from .. import log as logging
from ..operators.io_import_xmot import load_xmot

logger = logging.getLogger(__name__)


class ImportXmot(bpy.types.Operator, ImportHelper, AxisHelper):
    """Import from xmot file format (.xmot)"""
    bl_idname = 'g3blend.io_import_xmot'
    bl_label = 'Import Motion (xmot)'
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = '.xmot'
    filter_glob: StringProperty(default='*.xmot', options={'HIDDEN'})

    files: CollectionProperty(
        name='File Path',
        type=bpy.types.OperatorFileListElement,
    )

    ignore_transform: BoolProperty(
        name='Ignore transform',
        description='Ignore transform set on the armature object',
        default=False,
    )

    def draw(self, context):
        pass

    def execute(self, context):
        try:
            global_scale, global_matrix = self._global_transform(context)
            load_xmot(context, self.filepath, global_scale, global_matrix, self.ignore_transform)
        except Exception as e:
            self.report({'ERROR'}, f'Error while importing {self.filepath}: {e}')
            logger.exception('Error while importing {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


class G3BLEND_PT_import_xmot_transform(AbstractFileTransformPanel):
    TARGET_OPERATOR = ImportXmot

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'ignore_transform')
        self.draw_transform(layout, operator)


classes = (
    ImportXmot,
    G3BLEND_PT_import_xmot_transform,
)
