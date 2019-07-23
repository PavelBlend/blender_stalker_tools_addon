import bpy


def check_image(image, texture):
    if texture in image.filepath:
        return True


def check_texture(bpy_texture, texture):
    if bpy_texture.type == 'IMAGE':
        image = bpy_texture.image
        if image:
            if check_image(image, texture):
                return True


def check_material_textures(material, texture):
    material_textures = []
    for texture_slot in material.texture_slots:
        if texture_slot:
            bpy_texture = texture_slot.texture
            if bpy_texture:
                material_textures.append(bpy_texture)
    if len(material_textures) == 1:
        bpy_texture = material_textures[0]
        if check_texture(bpy_texture, texture):
            return True


def check_xray_material_properties(material, shader):
    if (
            material.xray.eshader == shader and \
            material.xray.cshader == 'default' and \
            material.xray.gamemtl == 'default'
        ):
        return True
    else:
        return False


def find_suitable_image(texture):
    for bpy_image in bpy.data.images:
        if check_image(bpy_image, texture):
            return bpy_image


def find_suitable_texture(texture):
    for bpy_texture in bpy.data.textures:
        if check_texture(bpy_texture, texture):
            return bpy_texture


def find_suitable_material(texture, shader):
    for material in bpy.data.materials:
        if check_xray_material_properties(material, shader):
            if check_material_textures(material, texture):
                return material
