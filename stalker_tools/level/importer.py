
import os

import bpy
import bmesh
import mathutils

from io_scene_xray import utils


def import_visuals(level):
    textures_folder = bpy.context.user_preferences.addons['io_scene_xray'].preferences.textures_folder_auto
    lmaps = set(level.lmaps)
    lmaps_0 = set(level.lmaps_0)
    lmaps_1 = set(level.lmaps_1)

    lmaps_textures = {}
    for lmap in lmaps:
        if lmap:
            bpy_tex = bpy.data.textures.new(lmap, type='IMAGE')
            bpy_tex.type = 'IMAGE'
            abs_image_path = os.path.dirname(level.file_path) + os.sep + lmap + '.dds'
            try:
                bpy_image = bpy.data.images.load(abs_image_path)
            except RuntimeError as ex:  # e.g. 'Error: Cannot read ...'
                bpy_image = bpy.data.images.new(lmap, 0, 0)
                bpy_image.source = 'FILE'
                bpy_image.filepath = abs_image_path
            bpy_tex.image = bpy_image
            lmaps_textures[lmap] = bpy_tex

    lmaps_0_textures = {}
    for lmap in lmaps_0:
        if lmap:
            bpy_tex = bpy.data.textures.new(lmap, type='IMAGE')
            bpy_tex.type = 'IMAGE'
            abs_image_path = os.path.dirname(level.file_path) + os.sep + lmap + '.dds'
            try:
                bpy_image = bpy.data.images.load(abs_image_path)
            except RuntimeError as ex:  # e.g. 'Error: Cannot read ...'
                bpy_image = bpy.data.images.new(lmap, 0, 0)
                bpy_image.source = 'FILE'
                bpy_image.filepath = abs_image_path
            bpy_tex.image = bpy_image
            lmaps_0_textures[lmap] = bpy_tex

    lmaps_1_textures = {}
    for lmap in lmaps_1:
        if lmap:
            bpy_tex = bpy.data.textures.new(lmap, type='IMAGE')
            bpy_tex.type = 'IMAGE'
            abs_image_path = os.path.dirname(level.file_path) + os.sep + lmap + '.dds'
            try:
                bpy_image = bpy.data.images.load(abs_image_path)
            except RuntimeError as ex:  # e.g. 'Error: Cannot read ...'
                bpy_image = bpy.data.images.new(lmap, 0, 0)
                bpy_image.source = 'FILE'
                bpy_image.filepath = abs_image_path
            bpy_tex.image = bpy_image
            lmaps_1_textures[lmap] = bpy_tex

    bpy_materials = []
    bpy_materials.append(None)    # first empty shader
    for material_index, texture in enumerate(level.materials):
        lmap = level.lmaps[material_index]
        if not lmap:
            abs_image_path = textures_folder + os.sep + texture + '.dds'
        else:
            abs_image_path = os.path.dirname(level.file_path) + os.sep + texture + '.dds'
        bpy_mat = bpy.data.materials.new(texture)
        bpy_mat.use_shadeless = True
        bpy_mat.use_transparency = True
        bpy_mat.alpha = 0.0
        bpy_tex = bpy.data.textures.new(texture, type='IMAGE')
        bpy_tex.type = 'IMAGE'
        bpy_texture_slot = bpy_mat.texture_slots.add()
        bpy_texture_slot.texture = bpy_tex
        bpy_texture_slot.use_map_alpha = True
        bpy_texture_slot.uv_layer = 'Texture'

        try:
            bpy_image = bpy.data.images.load(abs_image_path)
        except RuntimeError as ex:  # e.g. 'Error: Cannot read ...'
            bpy_image = bpy.data.images.new(texture, 0, 0)
            bpy_image.source = 'FILE'
            bpy_image.filepath = abs_image_path

        bpy_tex.image = bpy_image
        bpy_materials.append(bpy_mat)

        shader = level.shaders[material_index]
        if shader:
            bpy_mat.xray.eshader = shader
            bpy_mat.xray.version = utils.plugin_version_number()

        # Generate material nodes

        lmap_1 = level.lmaps_0[material_index]
        lmap_2 = level.lmaps_1[material_index]

        if (lmap_1 and lmap_2) or lmap:

            bpy_mat.use_nodes = True
            bpy_mat.texture_slots[0].use_map_color_diffuse = False
            bpy_mat.texture_slots[0].use_map_alpha = False
            node_tree = bpy_mat.node_tree

            output_node = node_tree.nodes['Output']
            output_node.location = (580.3516235351562, 375.3576965332031)
            output_node.select = False

            material_node = node_tree.nodes['Material']
            material_node.material = bpy_mat
            material_node.location = (385.1767578125, 421.38262939453125)
            material_node.select = False

            uv_lmap_node = node_tree.nodes.new('ShaderNodeGeometry')
            uv_lmap_node.name = 'UV Light Map'
            uv_lmap_node.label = 'UV Light Map'
            uv_lmap_node.uv_layer = 'Light_Map'
            uv_lmap_node.location = (-711.32177734375, -48.62998962402344)
            uv_lmap_node.select = False

            if lmap:
                lmap_texture = lmaps_textures[lmap]

                lmap_texture_node = node_tree.nodes.new('ShaderNodeTexture')
                lmap_texture_node.name = 'Light Map'
                lmap_texture_node.label = 'Light Map'
                lmap_texture_node.texture = lmap_texture
                lmap_texture_node.location = (-461.5350341796875, -107.8274154663086)
                lmap_texture_node.select = False

            if lmap_1 and lmap_2:
                lmap_1_texture = lmaps_0_textures[lmap_1]

                lmap_1_texture_node = node_tree.nodes.new('ShaderNodeTexture')
                lmap_1_texture_node.name = 'Light Map 1'
                lmap_1_texture_node.label = 'Light Map 1'
                lmap_1_texture_node.texture = lmap_1_texture
                lmap_1_texture_node.location = (-461.5350341796875, -107.8274154663086)
                lmap_1_texture_node.select = False

                lmap_2_texture = lmaps_1_textures[lmap_2]

                lmap_2_texture_node = node_tree.nodes.new('ShaderNodeTexture')
                lmap_2_texture_node.name = 'Light Map 2'
                lmap_2_texture_node.label = 'Light Map 2'
                lmap_2_texture_node.texture = lmap_2_texture
                lmap_2_texture_node.location = (-460.4274597167969, 185.0209197998047)
                lmap_2_texture_node.select = False

            uv_texture_node = node_tree.nodes.new('ShaderNodeGeometry')
            uv_texture_node.name = 'UV Texture'
            uv_texture_node.label = 'UV Texture'
            uv_texture_node.uv_layer = 'Texture'
            uv_texture_node.location = (-458.37139892578125, 474.66326904296875)
            uv_texture_node.select = False

            texture_node = node_tree.nodes.new('ShaderNodeTexture')
            texture_node.name = 'Texture'
            texture_node.label = 'Texture'
            texture_node.texture = bpy_tex
            texture_node.location = (-201.79190063476562, 363.87408447265625)
            texture_node.select = False

            hemi_node = node_tree.nodes.new('ShaderNodeMixRGB')
            hemi_node.name = 'Hemi'
            hemi_node.label = 'Hemi'
            hemi_node.inputs['Fac'].default_value = 0.5
            hemi_node.blend_type = 'ADD'
            hemi_node.location = (-190.5177764892578, 63.71351623535156)
            hemi_node.select = False

            sun_color_node = node_tree.nodes.new('ShaderNodeMixRGB')
            sun_color_node.name = 'Sun Color'
            sun_color_node.label = 'Sun Color'
            sun_color_node.inputs['Fac'].default_value = 1.0
            sun_color_node.inputs['Color1'].default_value = (0.628471, 0.277553, 0.164482, 1)
            sun_color_node.blend_type = 'MULTIPLY'
            sun_color_node.location = (-182.14694213867188, -113.74629211425781)
            sun_color_node.select = False

            sun_node = node_tree.nodes.new('ShaderNodeMixRGB')
            sun_node.name = 'Sun'
            sun_node.label = 'Sun'
            sun_node.inputs['Fac'].default_value = 1.0
            sun_node.blend_type = 'ADD'
            sun_node.location = (10.250570297241211, 16.821426391601562)
            sun_node.select = False

            light_maps_node = node_tree.nodes.new('ShaderNodeMixRGB')
            light_maps_node.name = 'Light Maps'
            light_maps_node.label = 'Light Maps'
            light_maps_node.inputs['Fac'].default_value = 0.97
            light_maps_node.blend_type = 'MULTIPLY'
            light_maps_node.location = (193.79037475585938, 164.41893005371094)
            light_maps_node.select = False

            # Generate node links
            if lmap:
                node_tree.links.new(uv_lmap_node.outputs['UV'], lmap_texture_node.inputs['Vector'])
                node_tree.links.new(lmap_texture_node.outputs['Value'], sun_color_node.inputs['Color2'])
                node_tree.links.new(lmap_texture_node.outputs['Color'], hemi_node.inputs['Color1'])
                node_tree.links.new(texture_node.outputs['Value'], hemi_node.inputs['Color2'])
            if lmap_1:
                node_tree.links.new(uv_lmap_node.outputs['UV'], lmap_1_texture_node.inputs['Vector'])
                node_tree.links.new(lmap_1_texture_node.outputs['Value'], sun_color_node.inputs['Color2'])
                node_tree.links.new(lmap_1_texture_node.outputs['Color'], hemi_node.inputs['Color1'])
            if lmap_2:
                node_tree.links.new(uv_lmap_node.outputs['UV'], lmap_2_texture_node.inputs['Vector'])
                node_tree.links.new(lmap_2_texture_node.outputs['Color'], hemi_node.inputs['Color2'])
            node_tree.links.new(uv_texture_node.outputs['UV'], texture_node.inputs['Vector'])
            node_tree.links.new(hemi_node.outputs['Color'], sun_node.inputs['Color1'])
            node_tree.links.new(sun_color_node.outputs['Color'], sun_node.inputs['Color2'])
            node_tree.links.new(texture_node.outputs['Color'], light_maps_node.inputs['Color1'])
            node_tree.links.new(sun_node.outputs['Color'], light_maps_node.inputs['Color2'])
            node_tree.links.new(light_maps_node.outputs['Color'], material_node.inputs['Color'])

    # Import meshes
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
                uvs_lmap = vertex_buffer.uv_lmap[visual.gcontainer.vb_offset : visual.gcontainer.vb_offset + visual.gcontainer.vb_size]
                colors_light = vertex_buffer.colors_light[visual.gcontainer.vb_offset : visual.gcontainer.vb_offset + visual.gcontainer.vb_size]
                colors_sun = vertex_buffer.colors_sun[visual.gcontainer.vb_offset : visual.gcontainer.vb_offset + visual.gcontainer.vb_size]
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

                if uvs_lmap:
                    uv_layer = b_mesh.loops.layers.uv.new('Light_Map')
                    for face in b_mesh.faces:
                        for loop in face.loops:
                            loop[uv_layer].uv = uvs_lmap[loop.vert.index]

                if colors_light:
                    color_layer = b_mesh.loops.layers.color.new('Light')
                    for face in b_mesh.faces:
                        for loop in face.loops:
                            bmesh_color = loop[color_layer]
                            color = colors_light[loop.vert.index]
                            bmesh_color.r = color[0]
                            bmesh_color.g = color[1]
                            bmesh_color.b = color[2]

                if colors_sun:
                    color_layer = b_mesh.loops.layers.color.new('Sun')
                    for face in b_mesh.faces:
                        for loop in face.loops:
                            bmesh_color = loop[color_layer]
                            color = colors_sun[loop.vert.index]
                            bmesh_color.r = color
                            bmesh_color.g = color
                            bmesh_color.b = color

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
