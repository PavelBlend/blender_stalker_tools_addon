
import time

import bpy

from .. import xray_io
from .. import ogf
from .. import importer
from . import format_
from . import geom


def read_sector_root(data):
    packed_reader = xray_io.PackedReader(data)
    root = packed_reader.getf('I')[0]


def read_sector_portal(data):
    packed_reader = xray_io.PackedReader(data)
    portal_count = len(data) // 2
    for portal_index in range(portal_count):
        portal = packed_reader.getf('H')[0]


def read_sector(data):
    chunked_reader = xray_io.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == format_.Chunks.Sector.PORTALS:
            read_sector_portal(chunk_data)
        elif chunk_id == format_.Chunks.Sector.ROOT:
            read_sector_root(chunk_data)
        else:
            print('UNKNOW LEVEL SECTOR CHUNK: {0:#x}'.format(chunk_id))


def read_sectors(data):
    chunked_reader = xray_io.ChunkedReader(data)
    for sector_id, sector_data in chunked_reader:
        read_sector(sector_data)


def read_glows(data):
    packed_reader = xray_io.PackedReader(data)
    glows_count = len(data) // 18
    for glow_index in range(glows_count):
        position = packed_reader.getf('3f')
        radius = packed_reader.getf('f')[0]
        shader_index = packed_reader.getf('H')[0]


def read_light_dynamic(data):
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


def read_portals(data):
    packed_reader = xray_io.PackedReader(data)
    portals_count = len(data) // 80
    for portal_index in range(portals_count):
        sector_front = packed_reader.getf('H')[0]
        sector_back = packed_reader.getf('H')[0]
        for vertex_index in range(6):
            coord_x, coord_y, coord_z = packed_reader.getf('fff')
        used_vertices_count = packed_reader.getf('I')[0]


def read_visuals(data, level):
    chunked_reader = xray_io.ChunkedReader(data)
    for visual_index, visual_data in chunked_reader:
        visual = ogf.read.read_main(visual_data)
        level.visuals.append(visual)


def read_shaders(data, level):
    packed_reader = xray_io.PackedReader(data)
    shaders_count = packed_reader.getf('I')[0]
    empty_shader = packed_reader.gets()
    level.materials.append(bpy.data.materials.new('material'))
    for shader_index in range(shaders_count - 1):
        shader = packed_reader.gets()
        engine_shader, textures = shader.split('/')
        light_maps_count = textures.count(',')
        if not light_maps_count:
            texture = textures
        elif light_maps_count == 1:
            texture, lmap = textures.split(',')
        elif light_maps_count == 2:
            texture, lmap_0, lmap_1 = textures.split(',')
        else:
            raise Exception('Shader has to many lmaps!')

        abs_image_path = 'D:\\stalker\\xray_sdk_yurshat_repack\\editors\\gamedata\\textures\\' + texture + '.dds'
        bpy_mat = bpy.data.materials.new(texture)
        bpy_mat.use_shadeless = True
        bpy_mat.use_transparency = True
        bpy_mat.alpha = 0.0
        bpy_tex = bpy.data.textures.new(texture, type='IMAGE')
        bpy_tex.type = 'IMAGE'
        bpy_texture_slot = bpy_mat.texture_slots.add()
        bpy_texture_slot.texture = bpy_tex
        bpy_texture_slot.use_map_alpha = True

        try:
            bpy_image = bpy.data.images.load(abs_image_path)
        except RuntimeError as ex:  # e.g. 'Error: Cannot read ...'
            bpy_image = bpy.data.images.new(texture, 0, 0)
            bpy_image.source = 'FILE'
            bpy_image.filepath = abs_image_path

        bpy_tex.image = bpy_image
        level.materials.append(bpy_mat)


def read_header(data):
    packed_reader = xray_io.PackedReader(data)
    xrlc_version = packed_reader.getf('H')[0]
    xrlc_quality = packed_reader.getf('H')[0]


def read_main(data, level):
    st = time.time()
    chunked_reader = xray_io.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:

        if chunk_id == format_.Chunks.Level.HEADER:
            read_header(chunk_data)

        elif chunk_id == format_.Chunks.Level.SHADERS:
            read_shaders(chunk_data, level)

        elif chunk_id == format_.Chunks.Level.VISUALS:
            visuals_chunk_data = chunk_data

        elif chunk_id == format_.Chunks.Level.PORTALS:
            read_portals(chunk_data)

        elif chunk_id == format_.Chunks.Level.LIGHT_DYNAMIC:
            read_light_dynamic(chunk_data)

        elif chunk_id == format_.Chunks.Level.GLOWS:
            read_glows(chunk_data)

        elif chunk_id == format_.Chunks.Level.SECTORS:
            read_sectors(chunk_data)

        else:
            print('UNKNOW LEVEL CHUNK: {0:#x}'.format(chunk_id))

    print('Load Level', time.time() - st)

    st = time.time()
    read_visuals(visuals_chunk_data, level)
    print('Load Visuals', time.time() - st)
    st = time.time()
    importer.import_visuals(level)
    print('Imported Visuals', time.time() - st)


def read_file(file_path):
    st = time.time()
    level = geom.read.read_file(file_path + '.geom')
    print('load geom:', time.time() - st)
    file = open(file_path, 'rb')
    data = file.read()
    file.close()
    read_main(data, level)
