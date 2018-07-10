
import time

import bpy

from .. import ogf
from .. import types
from . import importer
from . import format_
from . import geom

try:
    from io_scene_xray import xray_io
except ImportError:
    pass


def sector_root(data, sector_):
    packed_reader = xray_io.PackedReader(data)
    root = packed_reader.getf('I')[0]
    sector_.root = root


def sector_portal(data):
    packed_reader = xray_io.PackedReader(data)
    portal_count = len(data) // 2
    for portal_index in range(portal_count):
        portal = packed_reader.getf('H')[0]


def sector(data):
    chunked_reader = xray_io.ChunkedReader(data)
    sector_ = types.Sector()
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == format_.Chunks.Sector.PORTALS:
            sector_portal(chunk_data)
        elif chunk_id == format_.Chunks.Sector.ROOT:
            sector_root(chunk_data, sector_)
        else:
            print('UNKNOW LEVEL SECTOR CHUNK: {0:#x}'.format(chunk_id))
    return sector_


def sectors(data, level):
    chunked_reader = xray_io.ChunkedReader(data)
    for sector_id, sector_data in chunked_reader:
        sector_ = sector(sector_data)
        level.sectors.append(sector_)


def glows(data):
    packed_reader = xray_io.PackedReader(data)
    glows_count = len(data) // 18
    for glow_index in range(glows_count):
        position = packed_reader.getf('3f')
        radius = packed_reader.getf('f')[0]
        shader_index = packed_reader.getf('H')[0]


def light_dynamic(data):
    packed_reader = xray_io.PackedReader(data)
    light_count = len(data) // 108
    for light_index in range(light_count):
        controller_id = packed_reader.getf('I')[0] # ???
        type = packed_reader.getf('I')[0] # ???
        diffuse = packed_reader.getf('4f')
        specular = packed_reader.getf('4f')
        ambient = packed_reader.getf('4f')
        position = packed_reader.getf('3f')
        direction = packed_reader.getf('3f')
        range_ = packed_reader.getf('f')[0]
        falloff = packed_reader.getf('f')[0]
        attenuation_0 = packed_reader.getf('f')[0]
        attenuation_1 = packed_reader.getf('f')[0]
        attenuation_2 = packed_reader.getf('f')[0]
        theta = packed_reader.getf('f')[0]
        phi = packed_reader.getf('f')[0]


def portals(data):
    packed_reader = xray_io.PackedReader(data)
    portals_count = len(data) // 80
    for portal_index in range(portals_count):
        sector_front = packed_reader.getf('H')[0]
        sector_back = packed_reader.getf('H')[0]
        for vertex_index in range(6):
            coord_x, coord_y, coord_z = packed_reader.getf('fff')
        used_vertices_count = packed_reader.getf('I')[0]


def visuals(data, level):
    chunked_reader = xray_io.ChunkedReader(data)
    for visual_index, visual_data in chunked_reader:
        visual = ogf.read.main(visual_data)
        level.visuals.append(visual)


def shaders(data, level):
    packed_reader = xray_io.PackedReader(data)
    shaders_count = packed_reader.getf('I')[0]
    empty_shader = packed_reader.gets()
    for shader_index in range(shaders_count - 1):
        shader = packed_reader.gets()
        engine_shader, textures = shader.split('/')
        light_maps_count = textures.count(',')
        if not light_maps_count:
            texture = textures
            level.lmaps.append(None)
            level.lmaps_0.append(None)
            level.lmaps_1.append(None)
        elif light_maps_count == 1:
            texture, lmap = textures.split(',')
            level.lmaps.append(lmap)
            level.lmaps_0.append(None)
            level.lmaps_1.append(None)
        elif light_maps_count == 2:
            texture, lmap_0, lmap_1 = textures.split(',')
            level.lmaps.append(None)
            level.lmaps_0.append(lmap_0)
            level.lmaps_1.append(lmap_1)
        else:
            raise Exception('Shader has to many lmaps!')

        level.materials.append(texture)
        level.shaders.append(engine_shader)


def header(data):
    packed_reader = xray_io.PackedReader(data)
    xrlc_version = packed_reader.getf('H')[0]
    xrlc_quality = packed_reader.getf('H')[0]


def main(data, level):
    st = time.time()
    chunked_reader = xray_io.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:

        if chunk_id == format_.Chunks.Level.HEADER:
            header(chunk_data)

        elif chunk_id == format_.Chunks.Level.SHADERS:
            shaders(chunk_data, level)

        elif chunk_id == format_.Chunks.Level.VISUALS:
            visuals_chunk_data = chunk_data

        elif chunk_id == format_.Chunks.Level.PORTALS:
            portals(chunk_data)

        elif chunk_id == format_.Chunks.Level.LIGHT_DYNAMIC:
            light_dynamic(chunk_data)

        elif chunk_id == format_.Chunks.Level.GLOWS:
            glows(chunk_data)

        elif chunk_id == format_.Chunks.Level.SECTORS:
            sectors(chunk_data, level)

        else:
            print('UNKNOW LEVEL CHUNK: {0:#x}'.format(chunk_id))

    print('Load Level', time.time() - st)

    st = time.time()
    visuals(visuals_chunk_data, level)
    print('Load Visuals', time.time() - st)
    st = time.time()
    importer.import_visuals(level)
    print('Imported Visuals', time.time() - st)


def file(file_path):
    st = time.time()
    level = types.Level()
    geom.read.file(file_path + '.geom', level)
    geom.read.file(file_path + '.geomx', level, fastpath=True)
    level.file_path = file_path
    print('load geom:', time.time() - st)
    file = open(file_path, 'rb')
    data = file.read()
    file.close()
    main(data, level)
