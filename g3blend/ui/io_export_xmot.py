import bpy
from bpy.props import BoolProperty, EnumProperty, IntProperty, StringProperty
from bpy_extras.io_utils import ExportHelper

from .helper import AbstractFilePanel, AbstractFileTransformPanel, AxisHelper, get_object_for_armature_item, \
    get_target_armature_list_items
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

    target_armature_index: IntProperty()

    def _set_target_armature(self, item):
        self.target_armature_index = item

    def _get_target_armature(self):
        return self.target_armature_index

    target_armature: EnumProperty(
        name='Armature',
        description='Armature from which the animation shall be exported',
        items=get_target_armature_list_items,
        set=_set_target_armature,
        get=_get_target_armature,
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
            target_armature = get_object_for_armature_item(context, self.target_armature)
            save_xmot(context, self.filepath, target_armature, global_scale, global_matrix, self.ignore_transform,
                      self.use_selection)
            self.target_armature_index = 0
        except Exception as e:
            self.report({'ERROR'}, f'Error while exporting {self.filepath}: {e}')
            logger.exception('Error while exporting {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


class G3BLEND_PT_export_xmot_export(AbstractFilePanel):
    TARGET_OPERATOR = ExportXmot
    bl_label = 'Export'

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'target_armature')
        target_armature = get_object_for_armature_item(context, operator.target_armature)
        sub = layout.row()
        sub.enabled = target_armature is not None
        sub.prop(operator, "use_selection")


class G3BLEND_PT_export_xmot_transform(AbstractFileTransformPanel):
    TARGET_OPERATOR = ExportXmot

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'ignore_transform')
        self.draw_transform(layout, operator)


classes = (
    ExportXmot,
    G3BLEND_PT_export_xmot_export,
    G3BLEND_PT_export_xmot_transform,
)
