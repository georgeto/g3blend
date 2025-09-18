from abc import abstractmethod
from typing import Optional

import bpy
from bpy.props import FloatProperty
from bpy_extras.io_utils import axis_conversion, orientation_helper
from mathutils import Matrix

from ..util import find_armature, units_blender_to_g3_factor


# Swap Y and Z and then flip forward direction to convert from left-handed (Gothic 3) to right-handed (Blender).
@orientation_helper(axis_forward='-Y', axis_up='Z')  # with to_forward='Y', to_up='Z' (default)
class AxisHelper:
    global_scale: FloatProperty(
        name='Scale',
        min=0.001, max=1000.0,
        default=1.0,
    )

    def _global_transform(self, context):
        global_scale = self.global_scale
        global_scale *= (1.0 / units_blender_to_g3_factor(context.scene))

        global_matrix = (Matrix.Scale(global_scale, 4) @
                         axis_conversion(from_forward=self.axis_forward, from_up=self.axis_up).to_4x4())

        return global_scale, global_matrix


class AbstractFilePanel(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_parent_id = 'FILE_PT_operator'

    @classmethod
    def poll(cls, context):
        operator = context.active_operator.bl_rna
        return operator.identifier == cls.TARGET_OPERATOR.bl_rna.identifier

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        self._draw(context, layout, context.active_operator)

    @abstractmethod
    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        pass


class AbstractFileTransformPanel(AbstractFilePanel):
    bl_label = 'Transform'

    def draw_transform(self, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'global_scale')
        layout.prop(operator, 'axis_forward')
        layout.prop(operator, 'axis_up')


def get_target_armature_list_items(_, context: bpy.types.Context):
    armature_objects = [obj for obj in context.scene.objects if obj.type == 'ARMATURE']
    selected_armature = find_armature(context)
    items = []

    if selected_armature:
        items.append((selected_armature.name, selected_armature.name, '', 'ARMATURE_DATA', 0))
    elif len(armature_objects) == 0 or len(armature_objects) > 1:
        items.append(('NO_ARMATURE_SELECTED', 'Please select...', '', 'ERROR', 0))

    for obj in armature_objects:
        if obj != selected_armature:
            items.append((obj.name, obj.name, '', 'ARMATURE_DATA', len(items)))
    return items


def get_object_for_armature_item(context: bpy.types.Context, item: str) -> Optional[bpy.types.Object]:
    if item == 'NO_ARMATURE_SELECTED':
        return None

    return context.scene.objects.get(item, None)
