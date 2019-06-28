from io_scene_xray.xray_io import ChunkedReader, PackedReader


def parse_gamemtl(data):
    materials = {}
    for (cid, data) in ChunkedReader(data):
        if cid == 4098:
            for (_, cdata) in ChunkedReader(data):
                name, desc = None, None
                for (cccid, ccdata) in ChunkedReader(cdata):
                    if cccid == 0x1000:
                        reader = PackedReader(ccdata)
                        material_index = reader.getf('I')[0]
                        name = reader.gets()
                        materials[material_index] = name
                    if cccid == 0x1005:
                        desc = PackedReader(ccdata).gets()
    return materials
