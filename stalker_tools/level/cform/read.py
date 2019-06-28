from io_scene_xray import xray_io


def cform_4(packed_reader, level):
    cform = level.cform
    cform.vertices_count = packed_reader.getf('I')[0]
    cform.triangles_count = packed_reader.getf('I')[0]
    cform.bbox = packed_reader.getf('6f')

    for vertex_index in range(cform.vertices_count):
        coord_x, coord_z, coord_y = packed_reader.getf('3f')
        cform.vertices.append((coord_x, coord_y, coord_z))

    sectors = set()

    for triangle_index in range(cform.triangles_count):
        vertex_1, vertex_3, vertex_2 = packed_reader.getf('3I')
        material = packed_reader.getf('H')[0]
        sector = packed_reader.getf('H')[0]
        sectors.add(sector)

        material_id = material & 0x3fff
        unknown_1 = material >> 15
        unknown_2 = material >> 14 & 1

        cform.triangles.append((vertex_1, vertex_2, vertex_3))
        cform.materials.append(material_id)
        cform.sectors.append(sector)

    sectors = list(sectors)
    sectors.sort()
    cform.sectors_ids = sectors


def main(data, level):
    packed_reader = xray_io.PackedReader(data)
    format_version = packed_reader.getf('I')[0]
    if format_version == 4:
        cform_4(packed_reader, level)
    else:
        print('Unsupported cform version: {}'.format(format_version))


def file(file_path, level):
    file = open(file_path, 'rb')
    data = file.read()
    file.close()
    main(data, level)
