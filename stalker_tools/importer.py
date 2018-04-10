
import bpy
import bmesh


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
                bpy_mesh = bpy.data.meshes.new('visual')
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
                    swidata = level.swis_buffers[visual.swi_index]

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

            bpy_object = bpy.data.objects.new('visual', bpy_mesh)
            bpy.context.scene.objects.link(bpy_object)

            if visual.tree_xform:
                loc_x, loc_y, loc_z = visual.tree_xform[12 : 15]
                bpy_object.location = loc_x, loc_z, loc_y
                '''for i in visual.tree_xform:
                    print(round(i, 2), end=' ')
                print()'''
