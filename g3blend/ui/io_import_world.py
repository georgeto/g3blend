from pathlib import Path

import bpy
from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector

from .helper import AbstractFilePanel, AbstractFileTransformPanel, AxisHelper
from .. import log as logging
from ..operators.io_import_world import load_world
from ..util import reset_scene

logger = logging.getLogger(__name__)


class ImportWorld(bpy.types.Operator, ImportHelper, AxisHelper):
    """Import world from g3dit entities.json (.json)"""
    bl_idname = 'g3blend.io_import_world'
    bl_label = 'Import World (entities.json)'
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = '.json'
    filter_glob: StringProperty(default='*.json', options={'HIDDEN'})

    # Resource dir
    resource_dir: bpy.props.StringProperty(
        name='Resource Directory',
        description='Directory containing all the Gothic 3 resources, '
                    'i.e. with the content of the unpacked *.pak files from the Gothic3 data directory.',
        # subtype='FILE_PATH',
        default='')

    position: bpy.props.FloatVectorProperty(
        name='Import Position',
        description='Base position for filtering imported entities.',
        default=(88000, 5000, -10200),
    )

    radius: bpy.props.FloatProperty(
        name='Import Radius',
        description='Radius from the base position for filtering imported entities.',
        default=5000,
        min=0,
    )

    ignore_y: BoolProperty(
        name='Ignore Y',
        description='Ignore the Y coordinate (vertical axis) during filtering.',
        default=True,
    )

    reset_scene: BoolProperty(
        name='Reset Scene',
        description='Remove everything from scene before import',
        default=False,
    )

    bake_transform: BoolProperty(
        name='Bake Transform',
        description="Bake space transform into object data, avoids getting unwanted rotations and "
                    "scale to objects because Gothic 3 space is not aligned with Blender's space",
        default=True,
    )

    def draw(self, context):
        pass

    def execute(self, context):
        try:
            global_scale, global_matrix = self._global_transform(context)
            if self.reset_scene:
                reset_scene()
            load_world(context, Path(self.filepath), Path(self.resource_dir), Vector(self.position), self.radius,
                       self.ignore_y,
                       global_scale, global_matrix, self.bake_transform)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f'Error while importing {self.filepath}: {e}')
            logger.exception('Error while importing {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


class G3BLEND_PT_import_world_transform(AbstractFileTransformPanel):
    TARGET_OPERATOR = ImportWorld
    bl_options = {'DEFAULT_CLOSED'}

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'bake_transform')
        self.draw_transform(layout, operator)


class G3BLEND_PT_import_world_filter(AbstractFilePanel):
    TARGET_OPERATOR = ImportWorld
    bl_label = 'Filter'

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'position')
        layout.prop(operator, 'radius')
        layout.prop(operator, 'ignore_y')


class G3BLEND_PT_import_world_misc(AbstractFilePanel):
    TARGET_OPERATOR = ImportWorld
    bl_label = 'Misc'

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'resource_dir')
        layout.prop(operator, 'reset_scene')


classes = (
    ImportWorld,
    G3BLEND_PT_import_world_transform,
    G3BLEND_PT_import_world_filter,
    G3BLEND_PT_import_world_misc,
)
