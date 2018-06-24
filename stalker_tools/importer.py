
import math
import os

import bpy
import bmesh
import mathutils


def import_root_object(visual):
    root_object = bpy.data.objects.new(visual.root_object, None)
    bpy.context.scene.objects.link(root_object)
    visual.root_object = root_object.name


def import_visual(visual, root_object):
    if visual.vertices and visual.indices:
        b_mesh = bmesh.new()
        bpy_mesh = bpy.data.meshes.new(visual.type)

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
        abs_image_path = textures_folder + os.sep + visual.texture + '.dds'
        bpy_mat = bpy.data.materials.new(visual.texture)
        bpy_mat.use_shadeless = True
        bpy_mat.use_transparency = True
        bpy_mat.alpha = 0.0
        bpy_tex = bpy.data.textures.new(visual.texture, type='IMAGE')
        bpy_tex.type = 'IMAGE'
        bpy_texture_slot = bpy_mat.texture_slots.add()
        bpy_texture_slot.texture = bpy_tex
        bpy_texture_slot.use_map_alpha = True

        try:
            bpy_image = bpy.data.images.load(abs_image_path)
        except RuntimeError as ex:  # e.g. 'Error: Cannot read ...'
            bpy_image = bpy.data.images.new(visual.texture, 0, 0)
            bpy_image.source = 'FILE'
            bpy_image.filepath = abs_image_path

        bpy_tex.image = bpy_image
        bpy_mesh.materials.append(bpy_mat)
        bpy_mesh.use_auto_smooth = True
        bpy_mesh.auto_smooth_angle = math.pi
        bpy_mesh.show_edge_sharp = True

        b_mesh.to_mesh(bpy_mesh)
        bpy_object = bpy.data.objects.new(visual.type, bpy_mesh)
        if root_object:
            bpy_object.parent = bpy.data.objects[root_object]
        bpy.context.scene.objects.link(bpy_object)


def import_visuals(level):
    bpy_materials = []
    bpy_materials.append(None)    # first empty shader
    for texture in level.materials:
        textures_folder = bpy.context.user_preferences.addons['io_scene_xray'].preferences.textures_folder_auto
        abs_image_path = textures_folder + os.sep + texture + '.dds'
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
        bpy_materials.append(bpy_mat)

    loaded_visuals = {}
    for visual in level.visuals:
        if visual.gcontainer:
            visual_key = '{0},{1},{2},{3},{4},{5}'.format(
                visual.gcontainer.vb_index,
                visual.gcontainer.vb_offset,
                visual.gcontainer.vb_size,
                visual.gcontainer.ib_index,
                visual.gcontainer.ib_offset,
                visual.gcontainer.ib_size
            )
            bpy_mesh_name = loaded_visuals.get(visual_key)
            if not bpy_mesh_name:
                b_mesh = bmesh.new()
                bpy_mesh = bpy.data.meshes.new(visual.type)
                bpy_mesh.materials.append(bpy_materials[visual.shader_id])

                vertex_buffer = level.vertex_buffers[visual.gcontainer.vb_index]
                vertices = vertex_buffer.position[visual.gcontainer.vb_offset : visual.gcontainer.vb_offset + visual.gcontainer.vb_size]
                uvs = vertex_buffer.uv[visual.gcontainer.vb_offset : visual.gcontainer.vb_offset + visual.gcontainer.vb_size]
                for vertex in vertices:
                    b_mesh.verts.new((vertex[0], vertex[1], vertex[2]))
                b_mesh.verts.ensure_lookup_table()

                indices_buffer = level.indices_buffers[visual.gcontainer.ib_index]
                indices = indices_buffer[visual.gcontainer.ib_offset : visual.gcontainer.ib_offset + visual.gcontainer.ib_size]

                if not visual.swi_index is None:
                    visual.swidata = level.swis_buffers[visual.swi_index]

                if visual.swidata:
                    indices = indices[visual.swidata[0].offset : ]

                for i in range(0, len(indices), 3):
                    v1 = b_mesh.verts[indices[i]]
                    v2 = b_mesh.verts[indices[i + 2]]
                    v3 = b_mesh.verts[indices[i + 1]]
                    try:
                        face = b_mesh.faces.new((v1, v2, v3))
                        face.smooth = True
                    except ValueError:
                        pass
                b_mesh.faces.ensure_lookup_table()

                b_mesh.normal_update()

                uv_layer = b_mesh.loops.layers.uv.new('Texture')
                for face in b_mesh.faces:
                    for loop in face.loops:
                        loop[uv_layer].uv = uvs[loop.vert.index]

                b_mesh.to_mesh(bpy_mesh)
                loaded_visuals[visual_key] = bpy_mesh.name

            else:
                bpy_mesh = bpy.data.meshes[bpy_mesh_name]

            bpy_object = bpy.data.objects.new(visual.type, bpy_mesh)
            bpy.context.scene.objects.link(bpy_object)

            if visual.tree_xform:
                t = visual.tree_xform
                transform_matrix = mathutils.Matrix((
                    (t[0], t[1], t[2], t[3]),
                    (t[4], t[5], t[6], t[7]),
                    (t[8], t[9], t[10], t[11]),
                    (t[12], t[13], t[14], t[15])
                    ))
                transform_matrix.transpose()
                translate, rotate, scale = transform_matrix.decompose()
                bpy_object.location = translate[0], translate[2], translate[1]
                bpy_object.scale = scale[0], scale[2], scale[1]
                rotate = rotate.to_euler('ZXY')
                bpy_object.rotation_euler = -rotate[0], -rotate[2], -rotate[1]
