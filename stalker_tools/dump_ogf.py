
import bpy
import bmesh

from . import xray_io
from . import fmt_ogf
from . import types
from . import importer


def read_ogf_color(packed_reader):
    rgb = packed_reader.getf('3f')
    hemi = packed_reader.getf('f')[0]
    sun = packed_reader.getf('f')[0]


def read_bsphere(packed_reader):
    center = packed_reader.getf('3f')
    radius = packed_reader.getf('f')[0]


def read_bbox(packed_reader):
    bbox_min = packed_reader.getf('3f')
    bbox_max = packed_reader.getf('3f')


def read_fastpath(data, visual):
    chunked_reader = xray_io.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == fmt_ogf.Chunks.GCONTAINER:
            read_gcontainer(chunk_data, visual, fast_path=True)
        elif chunk_id == fmt_ogf.Chunks.SWIDATA:
            read_swidata(chunk_data, visual, fast_path=True)
        else:
            print('UNKNOW OGF FASTPATH CHUNK: {0:#x}'.format(chunk_id))


def read_gcontainer(data, visual, fast_path=False):
    gcontainer = types.GeometryContainer()
    packed_reader = xray_io.PackedReader(data)
    vb_index = packed_reader.getf('I')[0]
    vb_offset = packed_reader.getf('I')[0]
    vb_size = packed_reader.getf('I')[0]
    ib_index = packed_reader.getf('I')[0]
    ib_offset = packed_reader.getf('I')[0]
    ib_size = packed_reader.getf('I')[0]

    gcontainer.vb_index = vb_index
    gcontainer.vb_offset = vb_offset
    gcontainer.vb_size = vb_size
    gcontainer.ib_index = ib_index
    gcontainer.ib_offset = ib_offset
    gcontainer.ib_size = ib_size

    if not fast_path:
        visual.gcontainer = gcontainer


def read_swicontainer(data, visual):
    packed_reader = xray_io.PackedReader(data)
    swi_index = packed_reader.getf('I')[0]

    visual.swi_index = swi_index


def read_s_joint_limit(packed_reader):
    limit = packed_reader.getf('2f')
    spring_factor = packed_reader.getf('f')[0]
    damping_factor = packed_reader.getf('f')[0]


def read_s_joint_ik_data(packed_reader):
    type = packed_reader.getf('I')[0]

    read_s_joint_limit(packed_reader)
    read_s_joint_limit(packed_reader)
    read_s_joint_limit(packed_reader)

    spring_factor = packed_reader.getf('f')[0]
    damping_factor = packed_reader.getf('f')[0]
    ik_flags = packed_reader.getf('I')[0]
    break_force = packed_reader.getf('f')[0]
    break_torque = packed_reader.getf('f')[0]
    friction = packed_reader.getf('f')[0]


def read_s_bone_shape(packed_reader):
    type = packed_reader.getf('H')[0]
    flags = packed_reader.getf('H')[0]
    read_obb(packed_reader)
    read_sphere(packed_reader)
    read_cylinder(packed_reader)


def read_s_ikdata(data, bones):
    packed_reader = xray_io.PackedReader(data)

    for bone in bones:
        version = packed_reader.getf('I')[0]
        game_material = packed_reader.gets()

        read_s_bone_shape(packed_reader)
        read_s_joint_ik_data(packed_reader)

        bind_offset = packed_reader.getf('3f')
        bind_rotate = packed_reader.getf('3f')
        mass = packed_reader.getf('f')[0]
        center_of_mass = packed_reader.getf('3f')


def read_cylinder(packed_reader):
    center = packed_reader.getf('3f')
    direction = packed_reader.getf('3f')
    height = packed_reader.getf('f')[0]
    radius = packed_reader.getf('f')[0]


def read_sphere(packed_reader):
    position = packed_reader.getf('3f')
    radius = packed_reader.getf('f')[0]


def read_obb(packed_reader):
    rotate = packed_reader.getf('9f')
    translate = packed_reader.getf('3f')
    halfsize = packed_reader.getf('3f')


def read_s_bone_names(data):
    packed_reader = xray_io.PackedReader(data)

    bones = []
    bones_count = packed_reader.getf('I')[0]

    for bone_index in range(bones_count):
        bone_name = packed_reader.gets()
        bone_parent = packed_reader.gets()
        read_obb(packed_reader)

        bones.append(bone_name)

    return bones


def read_motion_mark(packed_reader):
    pass


def read_motion_def(packed_reader):
	bone_or_part = packed_reader.getf('H')[0]
	motion = packed_reader.getf('H')[0]
	speed = packed_reader.getf('f')[0]
	power = packed_reader.getf('f')[0]
	accrue = packed_reader.getf('f')[0]
	falloff = packed_reader.getf('f')[0]


def read_s_smparams(data):
    packed_reader = xray_io.PackedReader(data)

    params_version = packed_reader.getf('H')[0]
    partition_count = packed_reader.getf('H')[0]

    for partition_index in range(partition_count):
        partition_name = packed_reader.gets()
        bone_count = packed_reader.getf('H')[0]

        for bone in range(bone_count):
            if params_version == 1:
                bone_id = packed_reader.getf('I')[0]
            elif params_version == 2:
                bone_name = packed_reader.gets()
            elif params_version == 3 or params_version == 4:
                bone_id = packed_reader.getf('I')[0]
                bone_name = packed_reader.gets()
            else:
                raise BaseException('Unknown params version')

    motion_count = packed_reader.getf('H')[0]

    for motion_index in range(motion_count):
        motion_name = packed_reader.gets()
        motion_flags = packed_reader.getf('I')[0]

        read_motion_def(packed_reader)

        if params_version == 4:
            num_marks = packed_reader.getf('I')[0]
            for mark_index in range(num_marks):
                read_motion_mark(packed_reader)


def read_treedef2(data, visual):
    packed_reader = xray_io.PackedReader(data)
    tree_xform = packed_reader.getf('16f')
    read_ogf_color(packed_reader)    # c_scale
    read_ogf_color(packed_reader)    # c_bias

    visual.tree_xform = tree_xform


def read_desc(data):
    packed_reader = xray_io.PackedReader(data)

    source = packed_reader.gets()

    export_tool = packed_reader.gets()
    export_time = packed_reader.getf('I')[0]

    owner_name = packed_reader.gets()
    creation_time = packed_reader.getf('I')[0]

    modif_name = packed_reader.gets()
    modified_time = packed_reader.getf('I')[0]


def read_loddef2(data):
    packed_reader = xray_io.PackedReader(data)
    for i in range(8):
        for j in range(4):
            coord_x, coord_y, coord_z = packed_reader.getf('3f')
            coord_u, coord_v = packed_reader.getf('2f')
            hemi = packed_reader.getf('I')[0]
            sun = packed_reader.getf('B')[0]
            pad = packed_reader.getf('3B')


def read_children_l(data):
    packed_reader = xray_io.PackedReader(data)
    children_count = packed_reader.getf('I')[0]
    for children_index in range(children_count):
        children = packed_reader.getf('I')[0]


def read_children(data):
    chunked_reader = xray_io.ChunkedReader(data)
    for child_id, child_data in chunked_reader:
        read_main(child_data, ogf=True)


def read_swidata(data, visual, fast_path=False):
    packed_reader = xray_io.PackedReader(data)
    swis = []
    reserved = packed_reader.getf('4I')
    swi_count = packed_reader.getf('I')[0]
    for swi_index in range(swi_count):
        offset = packed_reader.getf('I')[0]
        triangles_count = packed_reader.getf('H')[0]
        vertices_count = packed_reader.getf('H')[0]

        swidata = types.SlideWindowData()
        swidata.offset = offset
        swidata.triangles_count = triangles_count
        swidata.vertices_count = vertices_count
        swis.append(swidata)

    if not fast_path:
        visual.swidata = swis


def read_indices(data, visual):
    packed_reader = xray_io.PackedReader(data)
    indices_count = packed_reader.getf('I')[0]
    for index in range(indices_count):
        vertex_index = packed_reader.getf('H')[0]
        visual.indices.append(vertex_index)


def read_vertices(data, visual):
    packed_reader = xray_io.PackedReader(data)

    vertex_format = packed_reader.getf('I')[0]
    vertices_count = packed_reader.getf('I')[0]

    if vertex_format == fmt_ogf.OGF_VERTEXFORMAT_FVF:
        for vertex_index in range(vertices_count):

            coord_x, coord_y, coord_z = packed_reader.getf('3f')
            normal_x, normal_y, normal_z = packed_reader.getf('3f')
            texture_coord_u, texture_coord_v = packed_reader.getf('2f')

            visual.vertices.append((coord_x, coord_z, coord_y))
            visual.uvs.append((texture_coord_u, 1 - texture_coord_v))

    elif vertex_format == fmt_ogf.OGF4_VERTEXFORMAT_FVF_1L:
        for vertex_index in range(vertices_count):

            coord_x, coord_y, coord_z = packed_reader.getf('3f')
            normal_x, normal_y, normal_z = packed_reader.getf('3f')
            tangent_x, tangent_y, tangent_z = packed_reader.getf('3f')
            binormal_x, binormal_y, binormal_z = packed_reader.getf('3f')
            texture_coord_u, texture_coord_v = packed_reader.getf('2f')
            bone_influence = packed_reader.getf('I')[0]

            visual.vertices.append((coord_x, coord_z, coord_y))
            visual.uvs.append((texture_coord_u, 1 - texture_coord_v))

    elif vertex_format == fmt_ogf.OGF4_VERTEXFORMAT_FVF_2L:
        for vertex_index in range(vertices_count):

            bone_0 = packed_reader.getf('H')[0]
            bone_1 = packed_reader.getf('H')[0]
            coord_x, coord_y, coord_z = packed_reader.getf('3f')
            normal_x, normal_y, normal_z = packed_reader.getf('3f')
            tangent_x, tangent_y, tangent_z = packed_reader.getf('3f')
            binormal_x, binormal_y, binormal_z = packed_reader.getf('3f')
            bone_influence = packed_reader.getf('f')[0]
            texture_coord_u, texture_coord_v = packed_reader.getf('2f')

            visual.vertices.append((coord_x, coord_z, coord_y))
            visual.uvs.append((texture_coord_u, 1 - texture_coord_v))

    else:
        raise BaseException('Unknown vertex format: 0x{:x}'.format(vertex_format))


def read_texture(data, visual):
    packed_reader = xray_io.PackedReader(data)
    texture = packed_reader.gets()
    shader = packed_reader.gets()
    visual.texture = texture


def read_header(data, visual):
    packed_reader = xray_io.PackedReader(data)

    ogf_version = packed_reader.getf('B')[0]
    if ogf_version != 4:
        raise BaseException('Unsupported format version: {0}'.format(ogf_version))

    model_type = packed_reader.getf('B')[0]
    shader_id = packed_reader.getf('H')[0]
    if ogf_version == 4:
        read_bbox(packed_reader)
        read_bsphere(packed_reader)

    visual.type = fmt_ogf.model_types[model_type]
    visual.shader_id = shader_id


def read_main(data, ogf=False):
    chunked_reader = xray_io.ChunkedReader(data)
    visual = types.Visual()

    for chunk_id, chunk_data in chunked_reader:
        visual.chunks.append(hex(chunk_id))

        if chunk_id == fmt_ogf.Chunks.HEADER:
            read_header(chunk_data, visual)

        elif chunk_id == fmt_ogf.Chunks.TEXTURE:
            read_texture(chunk_data, visual)

        elif chunk_id == fmt_ogf.Chunks.VERTICES:
            read_vertices(chunk_data, visual)

        elif chunk_id == fmt_ogf.Chunks.INDICES:
            read_indices(chunk_data, visual)

        elif chunk_id == fmt_ogf.Chunks.SWIDATA:
            read_swidata(chunk_data, visual)

        elif chunk_id == fmt_ogf.Chunks.CHILDREN:
            read_children(chunk_data)

        elif chunk_id == fmt_ogf.Chunks.CHILDREN_L:
            read_children_l(chunk_data)

        elif chunk_id == fmt_ogf.Chunks.LODDEF2:
            read_loddef2(chunk_data)

        elif chunk_id == fmt_ogf.Chunks.TREEDEF2:
            read_treedef2(chunk_data, visual)

        elif chunk_id == fmt_ogf.Chunks.S_BONE_NAMES:
            bones = read_s_bone_names(chunk_data)

        elif chunk_id == fmt_ogf.Chunks.S_SMPARAMS:
            read_s_smparams(chunk_data)

        elif chunk_id == fmt_ogf.Chunks.S_IKDATA:
            read_s_ikdata(chunk_data, bones)

        elif chunk_id == fmt_ogf.Chunks.DESC:
            read_desc(chunk_data)

        elif chunk_id == fmt_ogf.Chunks.SWICONTAINER:
            read_swicontainer(chunk_data, visual)

        elif chunk_id == fmt_ogf.Chunks.GCONTAINER:
            read_gcontainer(chunk_data, visual)

        elif chunk_id == fmt_ogf.Chunks.FASTPATH:
            read_fastpath(chunk_data, visual)

        else:
            print('UNKNOW OGF CHUNK: {0:#x}'.format(chunk_id))

    if ogf:
        importer.import_visual(visual)

    return visual


def read_file(file_path):
    file = open(file_path, 'rb')
    data = file.read()
    file.close()
    read_main(data, ogf=True)
