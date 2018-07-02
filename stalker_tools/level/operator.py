
import time

import bpy
from bpy_extras import io_utils

from . import read


class OpImportStalkerLevel(bpy.types.Operator, io_utils.ImportHelper):
    bl_idname = 'xray_import.stalker_level'
    bl_label = 'Import Level'
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(
        subtype="FILE_PATH", options={'SKIP_SAVE'}
        )
    filter_glob = bpy.props.StringProperty(default='level', options={'HIDDEN'})

    def execute(self, context):

        io_scene_xray_addon = bpy.context.user_preferences.addons.get('io_scene_xray')

        try:
            import io_scene_xray
            has_io_scene_xray = True
        except ImportError:
            has_io_scene_xray = False

        if not io_scene_xray_addon or not has_io_scene_xray:
            self.report({'WARNING'}, 'Cannot find "io_scene_xray" addon')
            return {'FINISHED'}

        st = time.time()
        read.file(self.filepath)
        print('total time: ', time.time() - st)
        return {'FINISHED'}

    def invoke(self, context, event):
        return super().invoke(context, event)
