
import time

from ... import xray_io
from ... import types
from .. import format_
from .. import read


def slide_windows_indices(data, level):
    packed_reader = xray_io.PackedReader(data)
    swi_buffers_count = packed_reader.getf('I')[0]
    for swi_buffer_index in range(swi_buffers_count):
        reserved = packed_reader.getf('4I')
        slide_windows_count = packed_reader.getf('I')[0]
        swis = []
        for slide_window_index in range(slide_windows_count):
            offset = packed_reader.getf('I')[0]
            triangles_count = packed_reader.getf('H')[0]
            vertices_count = packed_reader.getf('H')[0]

            swi = types.SlideWindowData()
            swi.offset = offset
            swi.triangles_count = triangles_count
            swi.vertices_count = vertices_count
            swis.append(swi)
        level.swis_buffers.append(swis)


def indices_buffers(data, level):
    packed_reader = xray_io.PackedReader(data)
    indices_buffers_count = packed_reader.getf('I')[0]
    for indices_buffer_index in range(indices_buffers_count):
        indices_count = packed_reader.getf('I')[0]
        indices_buffer = packed_reader.getf('{0}H'.format(indices_count))
        level.indices_buffers.append(indices_buffer)


def vertex_buffers(data, level):
    packed_reader = xray_io.PackedReader(data)
    vertex_buffers_count = packed_reader.getf('I')[0]
    for vertex_buffer_index in range(vertex_buffers_count):
        usage_list = []
        vertex_buffer = types.VertexBuffer()
        while True:
            stream = packed_reader.getf('H')[0]             # ?
            offset = packed_reader.getf('H')[0]             # ?
            type = packed_reader.getf('B')[0]               # ?
            method = packed_reader.getf('B')[0]             # ?
            usage = packed_reader.getf('B')[0]              # ?
            usage_index = packed_reader.getf('B')[0]        # ?
            if format_.types[type] == format_.UNUSED:
                break
            else:
                usage_list.append((usage, type))
        vertices_count = packed_reader.getf('I')[0]
        for vertex_index in range(vertices_count):
            texcoord = 0
            for usage, type in usage_list:
                if format_.usage[usage] == format_.POSITION:
                    coord_x, coord_y, coord_z = packed_reader.getf('3f')
                    vertex_buffer.position.append((coord_x, coord_z, coord_y))
                elif format_.usage[usage] == format_.NORMAL:
                    norm_x, norm_y, norm_z, norm_HZ = packed_reader.getf('4B')
                elif format_.usage[usage] == format_.TEXCOORD:
                    if format_.types[type] == format_.FLOAT2:
                        if texcoord == 0:
                            coord_u, coord_v = packed_reader.getf('2f')
                            vertex_buffer.uv.append((coord_u, 1 - coord_v))
                            texcoord += 1
                        else:
                            lmap_u, lmap_v = packed_reader.getf('2f')
                    elif format_.types[type] == format_.SHORT2:
                        if texcoord == 0:
                            coord_u, coord_v = packed_reader.getf('2h')
                            vertex_buffer.uv.append((coord_u / 1024, 1 - coord_v / 1024))
                            texcoord += 1
                        else:
                            lmap_u, lmap_v = packed_reader.getf('2H')
                    elif format_.types[type] == format_.SHORT4:
                        coord_u, coord_v = packed_reader.getf('2h')
                        vertex_buffer.uv.append((coord_u / 2048, 1 - coord_v / 2048))
                        lmap_u, lmap_v = packed_reader.getf('2H')
                    else:
                        print('UNKNOWN VERTEX BUFFER TYPE:', type)
                elif format_.usage[usage] == format_.TANGENT:
                    tangents = packed_reader.getf('4B')
                elif format_.usage[usage] == format_.BINORMAL:
                    binormals = packed_reader.getf('4B')
                elif format_.usage[usage] == format_.COLOR:
                    colors = packed_reader.getf('4B')
                else:
                    print('UNKNOWN VERTEX BUFFER USAGE:', usage)
        level.vertex_buffers.append(vertex_buffer)


def main(data):
    level = types.Level()
    chunked_reader = xray_io.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:

        if chunk_id == format_.Chunks.Level.HEADER:
            read.header(chunk_data)

        elif chunk_id == format_.Chunks.Geometry.VB:
            st = time.time()
            vertex_buffers(chunk_data, level)
            print('Load VB:', time.time() - st)

        elif chunk_id == format_.Chunks.Geometry.IB:
            st = time.time()
            indices_buffers(chunk_data, level)
            print('Load IB:', time.time() - st)

        elif chunk_id == format_.Chunks.Geometry.SWIS:
            st = time.time()
            slide_windows_indices(chunk_data, level)
            print('Load SWIS:', time.time() - st)

        else:
            print('UNKNOW LEVEL GEOM CHUNK: {0:#x}'.format(chunk_id))

    return level


def file(file_path):
    file = open(file_path, 'rb')
    data = file.read()
    file.close()
    level = main(data)
    return level
