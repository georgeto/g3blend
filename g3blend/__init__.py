import bpy
from bpy.props import BoolProperty, CollectionProperty, FloatProperty, StringProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper, axis_conversion, orientation_helper
from mathutils import Matrix, Vector

from . import log as logging
from .operators.io_export_xact import save_xact
from .operators.io_export_xmot import save_xmot
from .operators.io_import_xact import load_xact
from .operators.io_import_xmot import load_xmot
from .util import reset_scene, units_blender_to_g3_factor

logger = logging.getLogger(__name__)

bl_info = {
    "name": "Gothic 3",
    "author": "georgeto",
    "version": (0, 0, 6),
    "description": "Gothic 3 Import/Export meshes, materials, textures, animations",
    "blender": (3, 5, 0),
    "location": "File > Import-Export",
    "warning": "",
    "doc_url": "https://github.com/georgeto/g3blend",
    "tracker_url": "https://github.com/georgeto/g3blend/issues",
    "category": "Import-Export",
}


# Swap Y and Z and then flip forward direction to convert from left-handed (Gothic 3) to right-handed (Blender).
@orientation_helper(axis_forward='Z', axis_up='Y')  # defaults: to_forward='Y', to_up='Z'
class AxisHelper:
    global_scale: FloatProperty(
        name="Scale",
        min=0.001, max=1000.0,
        default=1.0,
    )

    def _global_transform(self, context):
        global_scale = self.global_scale
        global_scale *= (1.0 / units_blender_to_g3_factor(context.scene))

        flip_forward = Matrix.LocRotScale(None, None, Vector((1, -1, 1)))
        global_matrix = (Matrix.Scale(global_scale, 4) @ flip_forward @
                         axis_conversion(from_forward=self.axis_forward, from_up=self.axis_up).to_4x4())

        # TODO: Support baking of from/to Gothic 3 global transformation. Currently the global transformation
        #       is stored/applied in matrix_basis of mesh object and armature object.

        return global_scale, global_matrix


class ImportXact(bpy.types.Operator, ImportHelper, AxisHelper):
    """Import from xact file format (.xact)"""
    bl_idname = "g3blend.io_import_xact"
    bl_label = 'Import Actor (xact)'
    bl_options = {'UNDO'}

    filename_ext = ".xact"
    filter_glob: StringProperty(default="*.xact", options={'HIDDEN'})

    reset_scene: BoolProperty(
        name="Reset Scene",
        description="Remove everything from scene before import",
        default=False,
    )

    show_bone_names: BoolProperty(
        name="Display bone names",
        description="Show bone names, can later be changed in armature properties",
        default=False,
    )

    show_bone_axes: BoolProperty(
        name="Display bone axes",
        description="Show bone axes, can later be changed in armature properties",
        default=False,
    )

    def execute(self, context):
        try:
            global_scale, global_matrix = self._global_transform(context)
            if self.reset_scene:
                reset_scene()
            load_xact(context, self.filepath, global_scale, global_matrix, self.show_bone_names, self.show_bone_axes)
        except Exception as e:
            self.report({'ERROR'}, f'Error while importing {self.filepath}: {e}')
            logger.exception('Error while importing {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


class ExportXact(bpy.types.Operator, ExportHelper, AxisHelper):
    """Export to xact file format (.xact)"""
    bl_idname = "g3blend.io_export_xact"
    bl_label = 'Export Actor (xact)'

    filename_ext = ".xact"
    filter_glob: StringProperty(
        default="*.xact",
        options={'HIDDEN'},
    )

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
    )

    def execute(self, context):
        try:
            global_scale, global_matrix = self._global_transform(context)
            save_xact()
        except Exception as e:
            self.report({'ERROR'}, f'Error while exporting {self.filepath}: {e}')
            logger.exception('Error while exporting {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


class ImportXmot(bpy.types.Operator, ImportHelper, AxisHelper):
    """Import from xmot file format (.xmot)"""
    bl_idname = "g3blend.io_import_xmot"
    bl_label = 'Import Motion (xmot)'
    bl_options = {'UNDO'}

    filename_ext = ".xmot"
    filter_glob: StringProperty(default="*.xmot", options={'HIDDEN'})

    files: CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
    )

    def execute(self, context):
        try:
            global_scale, global_matrix = self._global_transform(context)
            load_xmot(context, self.filepath, global_scale, global_matrix)
        except Exception as e:
            self.report({'ERROR'}, f'Error while importing {self.filepath}: {e}')
            logger.exception('Error while importing {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


class ExportXmot(bpy.types.Operator, ExportHelper, AxisHelper):
    """Export to xmot file format (.xmot)"""
    bl_idname = "g3blend.io_export_xmot"
    bl_label = 'Export Motion (xmot)'

    filename_ext = ".xmot"
    filter_glob: StringProperty(
        default="*.xmot",
        options={'HIDDEN'},
    )

    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
    )

    def execute(self, context):
        try:
            global_scale, global_matrix = self._global_transform(context)
            save_xmot(context, self.filepath, global_scale, global_matrix)
        except Exception as e:
            self.report({'ERROR'}, f'Error while exporting {self.filepath}: {e}')
            logger.exception('Error while exporting {}', self.filepath)
            return {'CANCELLED'}

        return {'FINISHED'}


# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(ExportXact.bl_idname, text="Gothic 3 Actor (.xact)")
    self.layout.operator(ExportXmot.bl_idname, text="Gothic 3 Motion (.xmot)")


def menu_func_import(self, context):
    self.layout.operator(ImportXact.bl_idname, text="Gothic 3 Actor (.xact)")
    self.layout.operator(ImportXmot.bl_idname, text="Gothic 3 Motion (.xmot)")


def register():
    bpy.utils.register_class(ImportXact)
    bpy.utils.register_class(ImportXmot)
    bpy.utils.register_class(ExportXact)
    bpy.utils.register_class(ExportXmot)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ImportXact)
    bpy.utils.unregister_class(ImportXmot)
    bpy.utils.unregister_class(ExportXact)
    bpy.utils.unregister_class(ExportXmot)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
