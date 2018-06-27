
import os

from .. import xray_io
from .. import types
from .. import importer
from . import format_


def ogf_color(packed_reader):
    rgb = packed_reader.getf('3f')
    hemi = packed_reader.getf('f')[0]
    sun = packed_reader.getf('f')[0]


def bsphere(packed_reader):
    center = packed_reader.getf('3f')
    radius = packed_reader.getf('f')[0]


def bbox(packed_reader):
    bbox_min = packed_reader.getf('3f')
    bbox_max = packed_reader.getf('3f')


def fastpath(data, visual):
    chunked_reader = xray_io.ChunkedReader(data)

    for chunk_id, chunk_data in chunked_reader:

        if chunk_id == format_.Chunks.GCONTAINER:
            gcontainer(chunk_data, visual, fast_path=True)

        elif chunk_id == format_.Chunks.SWIDATA:
            swidata(chunk_data, visual, fast_path=True)

        else:
            print('UNKNOW OGF FASTPATH CHUNK: {0:#x}'.format(chunk_id))


def gcontainer(data, visual, fast_path=False):
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


def swicontainer(data, visual):
    packed_reader = xray_io.PackedReader(data)
    swi_index = packed_reader.getf('I')[0]

    visual.swi_index = swi_index


def s_userdata(data, visual):
    packed_reader = xray_io.PackedReader(data)

    user_data = packed_reader.gets()

    visual.user_data = user_data


def s_joint_limit(packed_reader):
    limit = packed_reader.getf('2f')
    spring_factor = packed_reader.getf('f')[0]
    damping_factor = packed_reader.getf('f')[0]


def s_joint_ik_data(packed_reader):
    type = packed_reader.getf('I')[0]

    s_joint_limit(packed_reader)
    s_joint_limit(packed_reader)
    s_joint_limit(packed_reader)

    spring_factor = packed_reader.getf('f')[0]
    damping_factor = packed_reader.getf('f')[0]
    ik_flags = packed_reader.getf('I')[0]
    break_force = packed_reader.getf('f')[0]
    break_torque = packed_reader.getf('f')[0]
    friction = packed_reader.getf('f')[0]


def s_bone_shape(packed_reader):
    type = packed_reader.getf('H')[0]
    flags = packed_reader.getf('H')[0]

    obb(packed_reader)
    sphere(packed_reader)
    cylinder(packed_reader)


def s_ikdata(data, visual, bones):
    packed_reader = xray_io.PackedReader(data)

    for bone_name, parent_name in bones:
        version = packed_reader.getf('I')[0]
        game_material = packed_reader.gets()

        s_bone_shape(packed_reader)
        s_joint_ik_data(packed_reader)

        rotate_x, rotate_y, rotate_z = packed_reader.getf('3f')
        offset_x, offset_y, offset_z = packed_reader.getf('3f')
        mass = packed_reader.getf('f')[0]
        center_of_mass = packed_reader.getf('3f')

        bone = visual.Bone(bone_name, (offset_x, offset_z, offset_y), (-rotate_x, -rotate_z, -rotate_y), parent_name)
        visual.bones.append(bone)


def cylinder(packed_reader):
    center = packed_reader.getf('3f')
    direction = packed_reader.getf('3f')
    height = packed_reader.getf('f')[0]
    radius = packed_reader.getf('f')[0]


def sphere(packed_reader):
    position = packed_reader.getf('3f')
    radius = packed_reader.getf('f')[0]


def obb(packed_reader):
    rotate = packed_reader.getf('9f')
    translate = packed_reader.getf('3f')
    halfsize = packed_reader.getf('3f')


def s_bone_names(data):
    packed_reader = xray_io.PackedReader(data)

    bones = []
    bones_count = packed_reader.getf('I')[0]

    for bone_index in range(bones_count):
        bone_name = packed_reader.gets()
        bone_parent = packed_reader.gets()

        obb(packed_reader)

        bones.append((bone_name, bone_parent))

    return bones


def motion_mark(packed_reader):
    pass


def motion_def(packed_reader):
	bone_or_part = packed_reader.getf('H')[0]
	motion = packed_reader.getf('H')[0]
	speed = packed_reader.getf('f')[0]
	power = packed_reader.getf('f')[0]
	accrue = packed_reader.getf('f')[0]
	falloff = packed_reader.getf('f')[0]


def s_smparams(data):
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
                bone_name = packed_reader.gets()
                bone_id = packed_reader.getf('I')[0]
            else:
                raise BaseException('Unknown params version')

    motion_count = packed_reader.getf('H')[0]

    for motion_index in range(motion_count):
        motion_name = packed_reader.gets()
        motion_flags = packed_reader.getf('I')[0]

        motion_def(packed_reader)

        if params_version == 4:
            num_marks = packed_reader.getf('I')[0]
            for mark_index in range(num_marks):
                motion_mark(packed_reader)


def treedef2(data, visual):
    packed_reader = xray_io.PackedReader(data)

    tree_xform = packed_reader.getf('16f')
    ogf_color(packed_reader)    # c_scale
    ogf_color(packed_reader)    # c_bias

    visual.tree_xform = tree_xform


def s_motion_refs_0(data, visual):
    packed_reader = xray_io.PackedReader(data)

    motion_refs = packed_reader.gets()

    visual.motion_reference = motion_refs


def desc(data, visual):
    packed_reader = xray_io.PackedReader(data)

    source = packed_reader.gets()

    export_tool = packed_reader.gets()
    export_time = packed_reader.getf('I')[0]

    owner_name = packed_reader.gets()
    creation_time = packed_reader.getf('I')[0]

    modif_name = packed_reader.gets()
    modified_time = packed_reader.getf('I')[0]

    visual.owner_name = owner_name
    visual.creation_time = creation_time
    visual.modif_name = modif_name
    visual.modified_time = modified_time


def loddef2(data):
    packed_reader = xray_io.PackedReader(data)
    for i in range(8):
        for j in range(4):
            coord_x, coord_y, coord_z = packed_reader.getf('3f')
            coord_u, coord_v = packed_reader.getf('2f')
            hemi = packed_reader.getf('I')[0]
            sun = packed_reader.getf('B')[0]
            pad = packed_reader.getf('3B')


def children_l(data):
    packed_reader = xray_io.PackedReader(data)
    children_count = packed_reader.getf('I')[0]
    for children_index in range(children_count):
        children = packed_reader.getf('I')[0]


def children(data, visual):
    chunked_reader = xray_io.ChunkedReader(data)
    children_visuals = []
    for child_id, child_data in chunked_reader:
        child_visual = main(child_data, ogf=True, root=visual.root_object, child=True)
        children_visuals.append(child_visual)
    return children_visuals


def swidata(data, visual, fast_path=False):
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


def indices(data, visual):
    packed_reader = xray_io.PackedReader(data)
    indices_count = packed_reader.getf('I')[0]
    for index in range(indices_count):
        vertex_index = packed_reader.getf('H')[0]
        visual.indices.append(vertex_index)


def vertices(data, visual):
    packed_reader = xray_io.PackedReader(data)

    vertex_format = packed_reader.getf('I')[0]
    vertices_count = packed_reader.getf('I')[0]
    visual.used_bones = set()

    if vertex_format == format_.OGF_VERTEXFORMAT_FVF:
        for vertex_index in range(vertices_count):

            coord_x, coord_y, coord_z = packed_reader.getf('3f')
            normal_x, normal_y, normal_z = packed_reader.getf('3f')
            texture_coord_u, texture_coord_v = packed_reader.getf('2f')

            visual.vertices.append((coord_x, coord_z, coord_y))
            visual.uvs.append((texture_coord_u, 1 - texture_coord_v))
            visual.normals.append((normal_x, normal_z, normal_y))

    elif vertex_format == format_.OGF4_VERTEXFORMAT_FVF_1L:
        for vertex_index in range(vertices_count):

            coord_x, coord_y, coord_z = packed_reader.getf('3f')
            normal_x, normal_y, normal_z = packed_reader.getf('3f')
            tangent_x, tangent_y, tangent_z = packed_reader.getf('3f')
            binormal_x, binormal_y, binormal_z = packed_reader.getf('3f')
            texture_coord_u, texture_coord_v = packed_reader.getf('2f')
            bone = packed_reader.getf('I')[0]
            visual.used_bones.add(bone)

            visual.vertices.append((coord_x, coord_z, coord_y))
            visual.uvs.append((texture_coord_u, 1 - texture_coord_v))
            visual.normals.append((normal_x, normal_z, normal_y))
            if visual.weghts.get(bone):
                visual.weghts[bone].append((vertex_index, 1.0))
            else:
                visual.weghts[bone] = [(vertex_index, 1.0), ]

    elif vertex_format == format_.OGF4_VERTEXFORMAT_FVF_2L:
        for vertex_index in range(vertices_count):

            bone_0 = packed_reader.getf('H')[0]
            bone_1 = packed_reader.getf('H')[0]
            visual.used_bones.add(bone_0)
            visual.used_bones.add(bone_1)
            coord_x, coord_y, coord_z = packed_reader.getf('3f')
            normal_x, normal_y, normal_z = packed_reader.getf('3f')
            tangent_x, tangent_y, tangent_z = packed_reader.getf('3f')
            binormal_x, binormal_y, binormal_z = packed_reader.getf('3f')
            bone_influence = packed_reader.getf('f')[0]
            texture_coord_u, texture_coord_v = packed_reader.getf('2f')

            visual.vertices.append((coord_x, coord_z, coord_y))
            visual.uvs.append((texture_coord_u, 1 - texture_coord_v))
            visual.normals.append((normal_x, normal_z, normal_y))

            if bone_0 == bone_1:
                if visual.weghts.get(bone_0):
                    visual.weghts[bone_0].append((vertex_index, 1 - bone_influence))
                else:
                    visual.weghts[bone_0] = [(vertex_index, 1 - bone_influence), ]
            else:
                if visual.weghts.get(bone_0):
                    visual.weghts[bone_0].append((vertex_index, 1 - bone_influence))
                else:
                    visual.weghts[bone_0] = [(vertex_index, 1 - bone_influence), ]
                if visual.weghts.get(bone_1):
                    visual.weghts[bone_1].append((vertex_index, bone_influence))
                else:
                    visual.weghts[bone_1] = [(vertex_index, bone_influence), ]

    else:
        raise BaseException('Unknown vertex format: 0x{:x}'.format(vertex_format))


def texture(data, visual):
    packed_reader = xray_io.PackedReader(data)

    texture = packed_reader.gets()
    shader = packed_reader.gets()

    visual.texture = texture
    visual.shader = shader


def header(data, visual):
    packed_reader = xray_io.PackedReader(data)

    ogf_version = packed_reader.getf('B')[0]
    if ogf_version != 4:
        raise BaseException('Unsupported format version: {0}'.format(ogf_version))

    model_type = packed_reader.getf('B')[0]
    shader_id = packed_reader.getf('H')[0]
    if ogf_version == 4:
        bbox(packed_reader)
        bsphere(packed_reader)

    visual.type = format_.model_types[model_type]
    visual.shader_id = shader_id


def main(data, ogf=False, root=None, child=False):
    chunked_reader = xray_io.ChunkedReader(data)
    visual = types.Visual()
    visual.root_object = root

    for chunk_id, chunk_data in chunked_reader:
        visual.chunks.append(hex(chunk_id))

        if chunk_id == format_.Chunks.HEADER:
            header(chunk_data, visual)

        elif chunk_id == format_.Chunks.TEXTURE:
            texture(chunk_data, visual)

        elif chunk_id == format_.Chunks.VERTICES:
            vertices(chunk_data, visual)

        elif chunk_id == format_.Chunks.INDICES:
            indices(chunk_data, visual)

        elif chunk_id == format_.Chunks.SWIDATA:
            swidata(chunk_data, visual)

        elif chunk_id == format_.Chunks.CHILDREN:
            visual.children_visuals = children(chunk_data, visual)

        elif chunk_id == format_.Chunks.CHILDREN_L:
            children_l(chunk_data)

        elif chunk_id == format_.Chunks.LODDEF2:
            loddef2(chunk_data)

        elif chunk_id == format_.Chunks.TREEDEF2:
            treedef2(chunk_data, visual)

        elif chunk_id == format_.Chunks.S_BONE_NAMES:
            bones = s_bone_names(chunk_data)

        elif chunk_id == format_.Chunks.S_SMPARAMS:
            s_smparams(chunk_data)

        elif chunk_id == format_.Chunks.S_IKDATA:
            s_ikdata(chunk_data, visual, bones)

        elif chunk_id == format_.Chunks.S_USERDATA:
            s_userdata(chunk_data, visual)

        elif chunk_id == format_.Chunks.DESC:
            desc(chunk_data, visual)

        elif chunk_id == format_.Chunks.S_MOTION_REFS_0:
            s_motion_refs_0(chunk_data, visual)

        elif chunk_id == format_.Chunks.SWICONTAINER:
            swicontainer(chunk_data, visual)

        elif chunk_id == format_.Chunks.GCONTAINER:
            gcontainer(chunk_data, visual)

        elif chunk_id == format_.Chunks.FASTPATH:
            fastpath(chunk_data, visual)

        else:
            print('UNKNOW OGF CHUNK: {0:#x}'.format(chunk_id))

    if ogf and not child:
        importer.import_visual(visual, root)

    return visual


def file(file_path):
    file = open(file_path, 'rb')
    data = file.read()
    file.close()
    if file:
        root_object_name = os.path.splitext(os.path.basename(file_path))[0]
        root_object = importer.import_root_object(root_object_name)
    main(data, ogf=True, root=root_object)
