import bpy

from io_scene_xray import xray_io
from ..ogf.read import s_motions, s_smparams
from ..ogf.format_ import Chunks
from ..ogf.importer import import_motions
from ..types import Visual


def file(file_path):
    file = open(file_path, 'rb')
    data = file.read()
    file.close()
    bones = []
    visual = Visual()
    arm_obj = bpy.context.object
    for bone in arm_obj.data.bones:
        if not bone.parent:
            parent = ''
        else:
            parent = bone.parent.name
        bones.append((bone.name, parent))
    chunked_reader = xray_io.ChunkedReader(data)
    motions_chunk = chunked_reader.next(Chunks.S_MOTIONS)
    visual.motions = s_motions(motions_chunk, None, bones)
    import_motions(visual, arm_obj)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == Chunks.S_SMPARAMS:
            s_smparams(chunk_data, visual)
        else:
            print('! Unknown OMF chunk: {}'.format(hex(chunk_id)))
