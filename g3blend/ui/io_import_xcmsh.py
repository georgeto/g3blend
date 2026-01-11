from pathlib import Path

import bpy

from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import ImportHelper

from .. import log as logging
from ..operators.io_import_xcmsh import load_xcmsh
from ..util import reset_scene
from .helper import AbstractFilePanel, AbstractFileTransformPanel, AxisHelper


logger = logging.getLogger(__name__)


class ImportXcmsh(bpy.types.Operator, ImportHelper, AxisHelper):
    """Import from xcmsh file format (.xcmsh)"""

    bl_idname = 'g3blend.io_import_xcmsh'
    bl_label = 'Import Mesh (xcmsh)'
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = '.xcmsh'
    filter_glob: StringProperty(default='*.xcmsh', options={'HIDDEN'})

    reset_scene: BoolProperty(
        name='Reset Scene', description='Remove everything from scene before import', default=False
    )

    mesh_name: StringProperty(
        name='Mesh Name',
        description='By default derived from xcmsh file name, can be overwritten, for example to import a mesh twice',
    )

    bake_transform: BoolProperty(
        name='Bake Transform',
        description='Bake space transform into object data, avoids getting unwanted rotations and '
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
            load_xcmsh(context, Path(self.filepath), self.mesh_name, global_scale, global_matrix, self.bake_transform)
            # Reset mesh name override on successful import.
            self.mesh_name = ''
        except Exception as e:
            self.report({'ERROR'}, f'Error while importing {self.filepath}: {e}')
            logger.exception('Error while importing {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


class G3BLEND_PT_import_xcmsh_transform(AbstractFileTransformPanel):
    TARGET_OPERATOR = ImportXcmsh

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'bake_transform')
        self.draw_transform(layout, operator)


class G3BLEND_PT_import_xcmsh_misc(AbstractFilePanel):
    TARGET_OPERATOR = ImportXcmsh
    bl_label = 'Misc'

    def _draw(self, context: bpy.types.Context, layout: bpy.types.UILayout, operator: bpy.types.Operator):
        layout.prop(operator, 'reset_scene')
        layout.prop(operator, 'mesh_name')


classes = (ImportXcmsh, G3BLEND_PT_import_xcmsh_transform, G3BLEND_PT_import_xcmsh_misc)
