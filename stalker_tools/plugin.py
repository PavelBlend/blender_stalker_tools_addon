
import bpy

from . import operators


def menu_func_import(self, _context):

    self.layout.operator(
        operators.OpImportStalkerLevel.bl_idname,
        text='X-Ray level (level)'
        )

    self.layout.operator(
        operators.OpImportStalkerOGF.bl_idname,
        text='X-Ray game object (.ogf)'
        )


def register():
    bpy.utils.register_class(operators.OpImportStalkerLevel)
    bpy.utils.register_class(operators.OpImportStalkerOGF)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(operators.OpImportStalkerOGF)
    bpy.utils.unregister_class(operators.OpImportStalkerLevel)
