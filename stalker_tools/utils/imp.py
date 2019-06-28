import bpy


def check_image(image, visual):
    if visual.texture in image.filepath:
        return True


def check_texture(texture, visual):
    if texture.type == 'IMAGE':
        image = texture.image
        if image:
            if check_image(image, visual):
                return True


def check_material_textures(material, visual):
    material_textures = []
    for texture_slot in material.texture_slots:
        if texture_slot:
            texture = texture_slot.texture
            if texture:
                material_textures.append(texture)
    if len(material_textures) == 1:
        texture = material_textures[0]
        if check_texture(texture, visual):
            return True


def check_xray_material_properties(material, visual):
    if (
            material.xray.eshader == visual.shader and \
            material.xray.cshader == 'default' and \
            material.xray.gamemtl == 'default'
        ):
        return True
    else:
        return False


def find_suitable_image(visual):
    for image in bpy.data.images:
        if check_image(image, visual):
            return image


def find_suitable_texture(visual):
    for texture in bpy.data.textures:
        if check_texture(texture, visual):
            return texture


def find_suitable_material(visual):
    for material in bpy.data.materials:
        if check_xray_material_properties(material, visual):
            if check_material_textures(material, visual):
                return material
