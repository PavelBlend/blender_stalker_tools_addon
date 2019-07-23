import math
import os

import bpy
import bmesh
import mathutils

from ..utils import imp as imp_utils

try:
    from io_scene_xray import utils
except ImportError:
    pass


MATRIX_BONE = mathutils.Matrix((
    (1.0, 0.0, 0.0, 0.0),
    (0.0, 0.0, -1.0, 0.0),
    (0.0, 1.0, 0.0, 0.0),
    (0.0, 0.0, 0.0, 1.0)
)).freeze()
MATRIX_BONE_INVERTED = MATRIX_BONE.inverted().freeze()


def merge_children(visual):
    if not visual.vertices and not visual.indices and visual.children_visuals:
        first_child = visual.children_visuals[0]
        vertices_count = len(first_child.vertices)

        if first_child.swidata:
            first_child.indices = first_child.indices[first_child.swidata[0].offset : ]
            first_child.swidata = None

        current_material = 0
        first_child.material_indices = [current_material, ] * (len(first_child.indices) // 3)
        first_child.textures = [first_child.texture, ]
        first_child.shaders = [first_child.shader, ]

        for child in visual.children_visuals[1 : ]:
            current_material += 1
            first_child.material_indices.extend([current_material, ] * (len(child.indices) // 3))
            first_child.textures.append(child.texture)
            first_child.shaders.append(child.shader)
            first_child.vertices.extend(child.vertices)
            first_child.uvs.extend(child.uvs)
            first_child.normals.extend(child.normals)

            if child.swidata:
                child.indices = child.indices[child.swidata[0].offset : ]

            for vertex_index in child.indices:
                first_child.indices.append(vertex_index + vertices_count)

            new_weights = {}
            for bone, weights in child.weghts.items():
                for vertex_index, weight in weights:
                    if new_weights.get(bone):
                        new_weights[bone].append((vertex_index + vertices_count, weight))
                    else:
                        new_weights[bone] = [(vertex_index + vertices_count, weight)]

            for bone, new_weight in new_weights.items():
                if first_child.weghts.get(bone):
                    first_child.weghts[bone].extend(new_weights[bone])
                else:
                    first_child.weghts[bone] = new_weights[bone]
            first_child.used_bones.update(child.used_bones)
            vertices_count += len(child.vertices)

        visual.children_visuals = [first_child, ]


def import_motions(visual, arm_obj):
    for motion_name, motion in visual.motions.items():
        act = bpy.data.actions.new(motion.name)
        xray_motion = arm_obj.xray.motions_collection.add()
        xray_motion.name = act.name
        for bone_name, bone_motion in motion.bones_motion.items():
            bpy_bone = arm_obj.data.bones[bone_motion.bone_name]
            bpy_bone_parent = bpy_bone.parent

            translate_fcurves = []
            for translate_index in range(3):
                translate_fcurve = act.fcurves.new(
                    'pose.bones["{}"].location'.format(bone_motion.bone_name),
                    index=translate_index,
                    action_group=bone_motion.bone_name
                )
                translate_fcurves.append(translate_fcurve)

            rotate_fcurves = []
            for rotate_index in range(3):
                rotate_fcurve = act.fcurves.new(
                    'pose.bones["{}"].rotation_euler'.format(bone_motion.bone_name),
                    index=rotate_index,
                    action_group=bone_motion.bone_name
                )
                rotate_fcurves.append(rotate_fcurve)

            rotations = []
            locations = []

            for frame_index, quaternion in enumerate(bone_motion.rotations):
                euler = mathutils.Quaternion((
                    quaternion[3] / 0x7fff,
                    quaternion[0] / 0x7fff,
                    quaternion[1] / 0x7fff,
                    -quaternion[2] / 0x7fff
                )).to_euler('ZXY')
                rotations.append(euler)

            for frame_index, translate in enumerate(bone_motion.translations.translate):
                location = []
                for index, value in enumerate(translate):
                    if bone_motion.t_present:
                        value = value * bone_motion.translations.t_size[index] + bone_motion.translations.t_init[index]
                    else:
                        value = value
                    if index == 2:
                        value = -value
                    location.append(value)
                locations.append(location)

            if len(rotations) > 1:
                frames_count = len(rotations)
            elif len(locations) > 1:
                frames_count = len(locations)
            else:
                frames_count = 1

            for frame_index in range(frames_count):
                if len(rotations) == 1:
                    rotation = rotations[0]
                else:
                    rotation = rotations[frame_index]

                if len(locations) == 1:
                    location = locations[0]
                else:
                    location = locations[frame_index]

                xmat = bpy_bone.matrix_local.inverted()
                if bpy_bone_parent:
                    xmat *= bpy_bone_parent.matrix_local
                else:
                    xmat *= MATRIX_BONE

                mat = xmat * mathutils.Matrix.Translation(location) * mathutils.Euler(rotation, 'ZXY').to_matrix().to_4x4()
                trn = mat.to_translation()
                rot = mat.to_euler('ZXY')

                for i in range(3):
                    translate_fcurves[i].keyframe_points.insert(frame_index, trn[i])

                for i in range(3):
                    rotate_fcurves[i].keyframe_points.insert(frame_index, rot[i])


def import_root_object(root_object_name):
    root_object = bpy.data.objects.new(root_object_name, None)
    bpy.context.scene.objects.link(root_object)
    root_object.xray.isroot = True
    root_object.xray.flags_simple = 'dy'
    return root_object


def import_bones(visual):
    bpy_armature = bpy.data.armatures.new(visual.file_name)
    bpy_armature.draw_type = 'STICK'
    bpy_object = bpy.data.objects.new(visual.file_name, bpy_armature)
    bpy_object.show_x_ray = True
    bpy_object.xray.isroot = False
    bpy.context.scene.objects.link(bpy_object)
    bpy.context.scene.objects.active = bpy_object
    bpy.ops.object.mode_set(mode='EDIT')
    matrices = {}

    visual.bones_names = {}
    for bone_index, bone in enumerate(visual.bones):
        visual.bones_names[bone_index] = bone.name
        bpy_bone = bpy_armature.edit_bones.new(bone.name)
        parent_matrix = matrices.get(bone.parent, mathutils.Matrix.Identity(4)) * MATRIX_BONE_INVERTED
        if bone.parent:
            bone_matrix = parent_matrix * mathutils.Matrix.Translation(bone.offset) * mathutils.Euler(bone.rotate, 'YXZ').to_matrix().to_4x4() * MATRIX_BONE
            bpy_bone.parent = bpy_armature.edit_bones[bone.parent]
        else:
            bone_matrix = mathutils.Matrix.Translation(bone.offset) * mathutils.Euler(bone.rotate, 'YXZ').to_matrix().to_4x4() * MATRIX_BONE
        matrices[bone.name] = bone_matrix
        bpy_bone.tail.y = 0.02
        bpy_bone.matrix = bone_matrix

    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in bpy_object.pose.bones:
        bone.rotation_mode = 'ZXY'

    for bone_index, bone in enumerate(visual.bones):
        bpy_bone = bpy_armature.bones[bone.name]
        bpy_bone.xray.gamemtl = bone.game_material
        bpy_bone.xray.mass.value = bone.mass
        bpy_bone.xray.mass.center = bone.center_of_mass
        bpy_bone.xray.shape.type = str(bone.shape_type)
        bpy_bone.xray.shape.flags = bone.shape_flags
        bpy_bone.xray.shape.sph_pos = bone.sphere_position
        bpy_bone.xray.shape.sph_rad = bone.sphere_radius
        bpy_bone.xray.shape.cyl_pos = bone.cylinder_center
        bpy_bone.xray.shape.cyl_dir = bone.cylinder_direction
        bpy_bone.xray.shape.cyl_hgh = bone.cylinder_height
        bpy_bone.xray.shape.cyl_rad = bone.cylinder_radius
        bpy_bone.xray.shape.box_rot = bone.box_rotate
        bpy_bone.xray.shape.box_trn = bone.box_translate
        bpy_bone.xray.shape.box_hsz = bone.box_halfsize

        xray_ik = bpy_bone.xray.ikjoint
        bone_ik = bone.ik_data

        xray_ik.type = str(bone_ik.joint_type)
        xray_ik.lim_x_min = bone_ik.joint_limits[0].limit[0]
        xray_ik.lim_x_max = bone_ik.joint_limits[0].limit[1]
        xray_ik.lim_x_spr = bone_ik.joint_limits[0].spring_factor
        xray_ik.lim_x_dmp = bone_ik.joint_limits[0].damping_factor
        xray_ik.lim_y_min = bone_ik.joint_limits[1].limit[0]
        xray_ik.lim_y_max = bone_ik.joint_limits[1].limit[1]
        xray_ik.lim_y_spr = bone_ik.joint_limits[1].spring_factor
        xray_ik.lim_y_dmp = bone_ik.joint_limits[1].damping_factor
        xray_ik.lim_z_min = bone_ik.joint_limits[2].limit[0]
        xray_ik.lim_z_max = bone_ik.joint_limits[2].limit[1]
        xray_ik.lim_z_spr = bone_ik.joint_limits[2].spring_factor
        xray_ik.lim_z_dmp = bone_ik.joint_limits[2].damping_factor

        xray_ik.spring = bone_ik.spring_factor
        xray_ik.damping = bone_ik.damping_factor
        bpy_bone.xray.ikflags = bone_ik.ik_flags
        bpy_bone.xray.breakf.force = bone_ik.break_force
        bpy_bone.xray.breakf.torque = bone_ik.break_torque
        bpy_bone.xray.friction = bone_ik.friction

        bpy_bone.xray.shape.set_curver()

    if visual.partitions:
        for partition in visual.partitions:
            bone_group = bpy_object.pose.bone_groups.new(partition.name)
            if partition.bones_names:
                for bone_name in partition.bones_names:
                    bpy_object.pose.bones[bone_name].bone_group = bone_group
            elif partition.bones_indices:
                for bone_idnex in partition.bones_indices:
                    bone = visual.bones[bone_idnex]
                    bone_name = bone.name
                    bpy_object.pose.bones[bone_name].bone_group = bone_group

    return bpy_object


def crete_vertex_groups(visual, bpy_object, root_visual):
    if not hasattr(visual, 'armature'):
        return
    if not visual.armature:
        return
    for bone_index in visual.used_bones:
        bone_name = root_visual.bones_names[bone_index]
        bone = visual.armature.data.bones[bone_name]
        bpy_object.vertex_groups.new(name=bone.name)


def import_visual(visual, root_object, child=False, root_visual=None):
    if visual.vertices and visual.indices:
        b_mesh = bmesh.new()
        if root_visual:
            file_name = root_visual.file_name
            obj_name = '{0}_{1}'.format(file_name, visual.type)
        else:
            file_name = visual.file_name
            obj_name = file_name
        bpy_mesh = bpy.data.meshes.new(obj_name)
        bpy_object = bpy.data.objects.new(obj_name, bpy_mesh)
        if root_object:
            bpy_object.parent = root_object
            bpy_object.xray.isroot = False
        bpy.context.scene.objects.link(bpy_object)
        crete_vertex_groups(visual, bpy_object, root_visual)

        if visual.swidata:
            visual.indices = visual.indices[visual.swidata[0].offset : ]

        # generate triangles
        triangles = []
        for index in range(0, len(visual.indices), 3):
            triangle = (
                visual.indices[index],
                visual.indices[index + 2],
                visual.indices[index + 1]
            )
            triangles.append(triangle)

        # merge ident verts
        load_vertices = {}
        new_triangles = []
        for tris_index, tris in enumerate(triangles):
            vert_0 = visual.vertices[tris[0]]
            vert_1 = visual.vertices[tris[1]]
            vert_2 = visual.vertices[tris[2]]
            norm_0 = visual.normals[tris[0]]
            norm_1 = visual.normals[tris[1]]
            norm_2 = visual.normals[tris[2]]
            verts = (vert_0, norm_0), (vert_1, norm_1), (vert_2, norm_2)
            new_face = [tris[0], tris[1], tris[2]]
            for vert_index, vert in enumerate(verts):
                if load_vertices.get(vert):
                    new_face[vert_index] = load_vertices[vert]
                else:
                    load_vertices[vert] = tris[vert_index]
            new_triangles.append(new_face)

        # find non-manifold edges
        loops_faces = {}
        load_vertices = {}
        load_vertices_indices = {}
        for tris_index, tris in enumerate(new_triangles):
            loop_0 = [tris[0], tris[1]]
            loop_1 = [tris[1], tris[2]]
            loop_2 = [tris[2], tris[0]]
            for loop in (loop_0, loop_1, loop_2):
                vert_0 = loop[0]
                vert_1 = loop[1]
                norm_0 = visual.normals[loop[0]]
                norm_1 = visual.normals[loop[1]]
                loop.sort()
                loop = tuple(loop)

                if loops_faces.get(loop):
                    loops_faces[loop].append(tris_index)
                else:
                    loops_faces[loop] = [tris_index, ]

                for vert, norm in ((vert_0, norm_0), (vert_1, norm_1)):
                    vert_coord = visual.vertices[vert]
                    if load_vertices.get(vert_coord):
                        if {norm} == set(load_vertices[vert_coord]):
                            loops_faces[loop].append(tris_index)
                        else:
                            pass

                        load_vertices[vert_coord].append(norm)
                        load_vertices_indices[vert_coord].append(vert)
                    else:
                        load_vertices[vert_coord] = [norm, ]
                        load_vertices_indices[vert_coord] = [vert, ]

        non_manifold_edges = set()
        for loop, tris in loops_faces.items():
            if len(tris) == 1:
                non_manifold_edges.add(loop)

        # remesh
        import_vertices = {}
        remap_indices = {}
        normals = {}
        uvs = []
        remap_vertex_index = 0

        for triangle_index, triangle in enumerate(triangles):
            for vertex_index in triangle:
                vertex_coord = visual.vertices[vertex_index]
                normal = visual.normals[vertex_index]
                uvs.append(visual.uvs[vertex_index])
                if import_vertices.get(vertex_coord) != None:
                    remap_indices[vertex_index] = import_vertices[vertex_coord]

                    normals[import_vertices[vertex_coord]].append(normal)

                else:
                    import_vertices[vertex_coord] = remap_vertex_index
                    remap_indices[vertex_index] = remap_vertex_index

                    normals[remap_vertex_index] = [normal, ]

                    remap_vertex_index += 1

        # remap non-manifold edges
        remap_non_manifold_edges = set()
        for non_manifold_edge in non_manifold_edges:
            vert_0 = remap_indices[non_manifold_edge[0]]
            vert_1 = remap_indices[non_manifold_edge[1]]
            verts = [vert_0, vert_1]
            verts.sort()
            verts = tuple(verts)
            remap_non_manifold_edges.add(verts)

        # create vertices
        for vertex_index in range(len(import_vertices)):
            b_mesh.verts.new((0, 0, 0))
        b_mesh.verts.ensure_lookup_table()

        # assign vertices coordinates
        for vert_coord, vert_index in import_vertices.items():
            b_mesh.verts[vert_index].co = vert_coord[0], vert_coord[1], vert_coord[2]

        # create triangles
        bm_faces = []
        for triangle in triangles:
            v1 = b_mesh.verts[remap_indices[triangle[0]]]
            v2 = b_mesh.verts[remap_indices[triangle[1]]]
            v3 = b_mesh.verts[remap_indices[triangle[2]]]
            try:
                face = b_mesh.faces.new((v1, v2, v3))
                face.smooth = True
                bm_faces.append(face)
            except ValueError:
                bm_faces.append(None)

        b_mesh.faces.ensure_lookup_table()
        b_mesh.normal_update()

        # generate sharp edges
        sharp_vertices = []
        for face in b_mesh.faces:
            for loop in face.loops:
                vert = loop.vert
                edge = loop.edge
                vert_normals = normals.get(vert.index)
                unique_normals = set()
                for vert_normal in vert_normals:
                    unique_normals.add(vert_normal)
                if len(unique_normals) > 1:
                    sharp_vertices.append(vert.index)

        for edge in b_mesh.edges:
            if edge.verts[0].index in sharp_vertices and edge.verts[1].index in sharp_vertices:
                edge_verts = [edge.verts[0].index, edge.verts[1].index]
                edge_verts.sort()
                edge_verts = tuple(edge_verts)
                if edge_verts in remap_non_manifold_edges:
                    if len(edge.link_faces) != 1:
                        edge.smooth = False

        # import uvs
        uv_layer = b_mesh.loops.layers.uv.new('Texture')
        uv_index = 0
        for face in bm_faces:
            if face:
                for loop in face.loops:
                    loop[uv_layer].uv = uvs[uv_index]
                    uv_index += 1
            else:
                uv_index += 3    # skip 3 face loops

        textures_folder = bpy.context.user_preferences.addons['io_scene_xray'].preferences.textures_folder_auto

        def create_material(texture, shader):
            abs_image_path = os.path.join(textures_folder, texture + '.dds')
            bpy_mat = bpy.data.materials.new(texture)
            bpy_mat.use_shadeless = True
            bpy_mat.use_transparency = True
            bpy_mat.alpha = 0.0
            bpy_tex = imp_utils.find_suitable_texture(texture)
            if not bpy_tex:
                bpy_tex = bpy.data.textures.new(texture, type='IMAGE')
                bpy_tex.type = 'IMAGE'
            bpy_texture_slot = bpy_mat.texture_slots.add()
            bpy_texture_slot.texture = bpy_tex
            bpy_texture_slot.use_map_alpha = True

            bpy_image = imp_utils.find_suitable_image(texture)
            if not bpy_image:
                try:
                    bpy_image = bpy.data.images.load(abs_image_path)
                except RuntimeError as ex:  # e.g. 'Error: Cannot read ...'
                    bpy_image = bpy.data.images.new(texture, 0, 0)
                    bpy_image.source = 'FILE'
                    bpy_image.filepath = abs_image_path

            bpy_tex.image = bpy_image
            bpy_mat.xray.eshader = shader
            bpy_mat.xray.cshader = 'default'
            bpy_mat.xray.gamemtl = 'default'
            bpy_mat.xray.version = utils.plugin_version_number()
            bpy_mesh.use_auto_smooth = True
            bpy_mesh.auto_smooth_angle = math.pi
            bpy_mesh.show_edge_sharp = True
            return bpy_mat

        if not getattr(visual, 'textures', None) and not getattr(visual, 'shaders', None):
            bpy_mat = imp_utils.find_suitable_material(visual.texture, visual.shader)
            if not bpy_mat:
                bpy_mat = create_material(visual.texture, visual.shader)
            bpy_mesh.materials.append(bpy_mat)
        else:
            for texture, shader in zip(visual.textures, visual.shaders):
                bpy_mat = imp_utils.find_suitable_material(texture, shader)
                if not bpy_mat:
                    bpy_mat = create_material(texture, shader)
                bpy_mesh.materials.append(bpy_mat)
            for tris_index, tris in enumerate(bm_faces):
                if tris:
                    tris.material_index = visual.material_indices[tris_index]
        b_mesh.to_mesh(bpy_mesh)

        # assign weghts
        for bone_index, vertices in visual.weghts.items():
            for vertex_index, vertex_weght in vertices:
                bone_name = root_visual.bones_names[bone_index]
                vertex_group = bpy_object.vertex_groups[bone_name]
                vertex_group.add([remap_indices[vertex_index], ], vertex_weght, type='REPLACE')
        if getattr(visual, 'armature', None):
            armature_modifier = bpy_object.modifiers.new('Armature', 'ARMATURE')
            armature_modifier.object = visual.armature


def set_xray_props_in_root_object(visual, root_object):
    if visual.swidata:
        root_object.xray.flags_simple = 'pd'

    root_object.xray.userdata = visual.user_data

    root_object.xray.revision.owner = visual.owner_name
    root_object.xray.revision.ctime = visual.creation_time
    root_object.xray.revision.moder = visual.modif_name
    root_object.xray.revision.mtime = visual.modified_time

    if visual.motion_reference:
        motion_references = root_object.xray.motionrefs_collection
        for motion_reference in visual.motion_reference.split(','):
            motion_references.add().name = motion_reference


def import_children_visuals(visual, root_obj):
    for child_visual in visual.children_visuals:
        if root_obj:
            if root_obj.type == 'ARMATURE':
                child_visual.armature = root_obj
        import_visual(child_visual, root_obj, child=True, root_visual=visual)


def import_ogf(visual):
    merge_children(visual)
    if len(visual.bones):
        arm_obj = import_bones(visual)
        set_xray_props_in_root_object(visual, arm_obj)
        import_children_visuals(visual, arm_obj)
        if visual.motions:
            import_motions(visual, arm_obj)
    else:
        if len(visual.children_visuals) > 1:
            root_object = import_root_object(visual.file_name)
            set_xray_props_in_root_object(visual, root_object)
            import_children_visuals(visual, root_object)
        else:
            import_children_visuals(visual, None)
