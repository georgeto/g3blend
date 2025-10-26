import bpy

from . import extension, meta, ui

bl_info = {
    "name": "Gothic 3",
    "author": "georgeto",
    "version": meta.get_addon_version(),
    "description": "Gothic 3 Import/Export meshes, materials, textures, animations",
    "blender": (3, 5, 0),
    "location": "File > Import-Export",
    "warning": "",
    "doc_url": "https://github.com/georgeto/g3blend",
    "tracker_url": "https://github.com/georgeto/g3blend/issues",
    "category": "Import-Export",
}


def menu_func_export(self, context):
    self.layout.operator(ui.io_export_xact.ExportXact.bl_idname, text="Gothic 3 Actor (.xact)")
    self.layout.operator(ui.io_export_xmot.ExportXmot.bl_idname, text="Gothic 3 Motion (.xmot)")


def menu_func_import(self, context):
    self.layout.operator(ui.io_import_xact.ImportXact.bl_idname, text="Gothic 3 Actor (.xact)")
    self.layout.operator(ui.io_import_xmot.ImportXmot.bl_idname, text="Gothic 3 Motion (.xmot)")
    self.layout.operator(ui.io_import_xcmsh.ImportXcmsh.bl_idname, text="Gothic 3 Mesh (.xcmsh)")


modules = (
    ui.frame_effects,
    ui.io_import_xact,
    ui.io_import_xmot,
    ui.io_import_xcmsh,
    ui.io_export_xact,
    ui.io_export_xmot,
    extension,
)


def register():
    for module in modules:
        for cls in module.classes:
            bpy.utils.register_class(cls)

        if on_register := getattr(module, 'on_register', None):
            on_register()

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for module in modules:
        for cls in module.classes:
            bpy.utils.unregister_class(cls)

        if on_unregister := getattr(module, 'on_unregister', None):
            on_unregister()

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
