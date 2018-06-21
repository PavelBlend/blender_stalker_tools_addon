
import bpy
import bmesh
import mathutils


def import_visual(visual):
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

        abs_image_path = 'D:\\stalker\\xray_sdk_yurshat_repack\\editors\\gamedata\\textures\\' + visual.texture + '.dds'
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

        b_mesh.to_mesh(bpy_mesh)
        bpy_object = bpy.data.objects.new(visual.type, bpy_mesh)
        bpy.context.scene.objects.link(bpy_object)


def import_visuals(level):
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
                bpy_mesh.materials.append(level.materials[visual.shader_id])

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
