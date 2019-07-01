class CForm:
    def __init__(self):
        self.version = None
        self.bbox = None
        self.vertices_count = None
        self.triangles_count = None
        self.vertices = []
        self.triangles = []
        self.sectors = []
        self.materials = []
        self.sectors_ids = None


class BoneMotionTranslation:
    def __init__(self):
        self.translate = []
        self.t_size = (1.0, 1.0, 1.0)
        self.t_init = (0.0, 0.0, 0.0)


class BoneMotion:
    def __init__(self):
        self.bone_name = None
        self.t_present = None
        self.r_absent = None
        self.hq = None
        self.rotations = []
        self.translations = None


class Motion:
    def __init__(self):
        self.name = None
        self.length = None
        self.bones_motion = {}


class Sector:
    def __init__(self):
        self.root = None
        self.portal_count = 0


class FastPathGeom:
    def __init__(self):
        self.vertex_buffers = []
        self.indices_buffers = []
        self.swis_buffers = []


class Level:
    def __init__(self):
        self.format_version = None
        self.file_path = None
        self.vertex_buffers = []
        self.indices_buffers = []
        self.swis_buffers = []
        self.visuals = []
        self.materials = []
        self.shaders = []
        self.lmaps = []
        self.lmaps_0 = []
        self.lmaps_1 = []
        self.sectors = []
        self.fastpath = FastPathGeom()
        self.cform = CForm()
        self.glows = []


class FastPath:
    def __init__(self):
        self.gcontainer = None
        self.swidata = None


class VertexBuffer:
    def __init__(self):
        self.position = []
        self.normal = []
        self.uv = []
        self.uv_lmap = []
        self.colors_light = []
        self.colors_sun = []
        self.colors_hemi = []
        self.shader_data = []


class GeometryContainer:
    def __init__(self):
        self.vb_index = 0
        self.vb_offset = 0
        self.vb_size = 0
        self.ib_index = 0
        self.ib_offset = 0
        self.ib_size = 0


class SlideWindowData:
    def __init__(self):
        self.offset = 0
        self.triangles_count = 0
        self.vertices_count = 0


class Glow:
    def __init__(self):
        self.position = None
        self.radius = None
        self.shader_index = None


class Visual:
    class Bone:
        def __init__(self):
            self.name = None
            self.offset = None
            self.rotate = None
            self.parent = None
            self.game_material = None
            self.mass = None
            self.center_of_mass = None
            self.shape_type = None
            self.shape_flags = None
            self.sphere_position = None
            self.sphere_radius = None
            self.cylinder_center = None
            self.cylinder_direction = None
            self.cylinder_height = None
            self.cylinder_radius = None

    class Partition:
        def __init__(self, name):
            self.name = name
            self.bones_indices = []
            self.bones_names = []

    def __init__(self):
        self.file_path = None
        self.type = None
        self.shader_id = None
        self.gcontainer = None
        self.swidata = None
        self.swi_index = None
        self.tree_xform = None
        self.chunks = []
        self.vertices = []
        self.uvs = []
        self.indices = []
        self.normals = []
        self.texture = None
        self.shader = None
        self.root_object = None
        self.bones = []
        self.weghts = {}
        self.children_visuals = []
        self.user_data = ''
        self.owner_name = ''
        self.creation_time = 0
        self.modif_name = ''
        self.modified_time = 0
        self.motion_reference = None
        self.partitions = []
        self.children_l = []
        self.fastpath = None
        self.texture_l = None
        self.shader_l = None
        self.motions = None
