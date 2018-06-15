
bl_info = {
    'name': 'S.T.A.L.K.E.R. Tools',
    'author': 'Pavel_Blend',
    'version': (0, 0, 0),
    'blender': (2, 79, 0),
    'category': 'Import-Export',
    'location': 'File > Import/Export'
}

import time
import os

import bpy
from bpy_extras import io_utils

from . import importer


class OpImportStalkerLevel(bpy.types.Operator, io_utils.ImportHelper):
    bl_idname = 'xray_import.stalker_level'
    bl_label = 'Import Level'
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(
        subtype="FILE_PATH", options={'SKIP_SAVE'}
        )
    filter_glob = bpy.props.StringProperty(default='level', options={'HIDDEN'})

    def execute(self, context):
        from . import read_level
        st = time.time()
        read_level.read_file(self.filepath)
        print('total time: ', time.time() - st)
        return {'FINISHED'}

    def invoke(self, context, event):
        return super().invoke(context, event)


class OpImportStalkerOGF(bpy.types.Operator, io_utils.ImportHelper):
    bl_idname = 'xray_import.stalker_ogf'
    bl_label = 'Import *.ogf'
    bl_options = {'REGISTER', 'UNDO'}

    directory = bpy.props.StringProperty(subtype="DIR_PATH")
    files = bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)
    filter_glob = bpy.props.StringProperty(default='*.ogf', options={'HIDDEN'})

    def execute(self, context):
        from . import read_ogf
        st = time.time()
        for file in self.files:
            read_ogf.read_file(os.path.join(self.directory, file.name))
        print('total time: ', time.time() - st)
        return {'FINISHED'}

    def invoke(self, context, event):
        return super().invoke(context, event)


def menu_func_import(self, _context):
    self.layout.operator(OpImportStalkerLevel.bl_idname, text='X-Ray Level (level)')
    self.layout.operator(OpImportStalkerOGF.bl_idname, text='X-Ray Game Object (.ogf)')


def register():
    bpy.utils.register_class(OpImportStalkerLevel)
    bpy.utils.register_class(OpImportStalkerOGF)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(OpImportStalkerOGF)
    bpy.utils.unregister_class(OpImportStalkerLevel)
