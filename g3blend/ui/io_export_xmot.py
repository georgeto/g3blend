import bpy
from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import ExportHelper

from .helper import AbstractFileTransformPanel, AxisHelper
from .. import log as logging
from ..operators.io_export_xmot import save_xmot

logger = logging.getLogger(__name__)


class ExportXmot(bpy.types.Operator, ExportHelper, AxisHelper):
    """Export to xmot file format (.xmot)"""
    bl_idname = 'g3blend.io_export_xmot'
    bl_label = 'Export Motion (xmot)'
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = '.xmot'
    filter_glob: StringProperty(
        default='*.xmot',
        options={'HIDDEN'},
    )

    use_selection: BoolProperty(
        name='Selection Only',
        description='Export selected objects only',
        default=False,
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
            save_xmot(context, self.filepath, global_scale, global_matrix, self.ignore_transform, self.use_selection)
        except Exception as e:
            self.report({'ERROR'}, f'Error while exporting {self.filepath}: {e}')
            logger.exception('Error while exporting {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


class G3BLEND_PT_export_xmot_transform(AbstractFileTransformPanel):
    TARGET_OPERATOR = ExportXmot

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'ignore_transform')
        self.draw_transform(layout, operator)


classes = (
    ExportXmot,
    G3BLEND_PT_export_xmot_transform,
)
