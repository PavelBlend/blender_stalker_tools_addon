
import os
import time

import bpy
from bpy_extras import io_utils

from . import level
from . import ogf


class OpImportStalkerLevel(bpy.types.Operator, io_utils.ImportHelper):
    bl_idname = 'xray_import.stalker_level'
    bl_label = 'Import Level'
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(
        subtype="FILE_PATH", options={'SKIP_SAVE'}
        )
    filter_glob = bpy.props.StringProperty(default='level', options={'HIDDEN'})

    def execute(self, context):
        st = time.time()
        level.read.read_file(self.filepath)
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
        st = time.time()
        for file in self.files:
            ogf.read.read_file(os.path.join(self.directory, file.name))
        print('total time: ', time.time() - st)
        return {'FINISHED'}

    def invoke(self, context, event):
        return super().invoke(context, event)
