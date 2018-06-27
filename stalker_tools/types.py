
class Level:
    def __init__(self):
        self.vertex_buffers = []
        self.indices_buffers = []
        self.swis_buffers = []
        self.visuals = []
        self.materials = []


class VertexBuffer:
    def __init__(self):
        self.position = []
        self.uv = []


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


class Visual:
    class Bone:
        def __init__(self, name, offset, rotate, parent):
            self.name = name
            self.offset = offset
            self.rotate = rotate
            self.parent = parent

    def __init__(self):
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
