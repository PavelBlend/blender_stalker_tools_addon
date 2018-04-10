
bl_info = {
    'name':     'S.T.A.L.K.E.R. Tools',
    'author':   'Pavel_Blend',
    'version':  (0, 0, 0),
    'blender':  (2, 79, 0),
    'category': 'Import-Export',
    'location': 'File > Import/Export'
}

import time

import bpy
from bpy_extras import io_utils


class OpImportLevel(bpy.types.Operator, io_utils.ImportHelper):
    bl_idname = 'xray_import.level'
    bl_label = 'Import Level'
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(
        subtype="FILE_PATH", options={'SKIP_SAVE'}
        )
    filter_glob = bpy.props.StringProperty(default='level', options={'HIDDEN'})

    def execute(self, context):
        from . import dump_level
        st = time.time()
        dump_level.read_file(self.filepath)
        print('total time: ', time.time() - st)
        return {'FINISHED'}

    def invoke(self, context, event):
        return super().invoke(context, event)


def menu_func_import(self, _context):
    self.layout.operator(OpImportLevel.bl_idname, text='X-Ray Level (level)')


def register():
    bpy.utils.register_class(OpImportLevel)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(OpImportLevel)
