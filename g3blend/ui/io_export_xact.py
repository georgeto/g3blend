import bpy

from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import ExportHelper

from .. import log as logging
from ..operators.io_export_xact import save_xact
from .helper import AbstractFileTransformPanel, AxisHelper


logger = logging.getLogger(__name__)


class ExportXact(bpy.types.Operator, ExportHelper, AxisHelper):
    """Export to xact file format (.xact)"""

    bl_idname = 'g3blend.io_export_xact'
    bl_label = 'Export Actor (xact)'
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = '.xact'
    filter_glob: StringProperty(default='*.xact', options={'HIDDEN'})

    use_selection: BoolProperty(name='Selection Only', description='Export selected objects only', default=False)

    def draw(self, context):
        pass

    def execute(self, context):
        try:
            global_scale, global_matrix = self._global_transform(context)
            save_xact()
        except Exception as e:
            self.report({'ERROR'}, f'Error while exporting {self.filepath}: {e}')
            logger.exception('Error while exporting {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


class G3BLEND_PT_export_xact_transform(AbstractFileTransformPanel):
    TARGET_OPERATOR = ExportXact

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        self.draw_transform(layout, operator)


classes = (ExportXact, G3BLEND_PT_export_xact_transform)
