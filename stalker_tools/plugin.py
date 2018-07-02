
import bpy

from . import level
from . import ogf


def menu_func_import(self, _context):

    self.layout.operator(
        level.operator.OpImportStalkerLevel.bl_idname,
        text='X-Ray level (level)'
        )

    self.layout.operator(
        ogf.operator.OpImportStalkerOGF.bl_idname,
        text='X-Ray game object (.ogf)'
        )


def register():
    bpy.utils.register_class(level.operator.OpImportStalkerLevel)
    bpy.utils.register_class(ogf.operator.OpImportStalkerOGF)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(ogf.operator.OpImportStalkerOGF)
    bpy.utils.unregister_class(level.operator.OpImportStalkerLevel)
