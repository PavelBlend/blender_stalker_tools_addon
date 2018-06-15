
class Chunks:
    HEADER = 0x1
    TEXTURE = 0x2
    VERTICES = 0x3
    INDICES = 0x4
    SWIDATA = 0x6
    CHILDREN = 0x9
    CHILDREN_L = 0xa
    LODDEF2 = 0xb
    TREEDEF2 = 0xc
    S_BONE_NAMES = 0xd
    S_SMPARAMS = 0xf
    S_IKDATA = 0x10
    S_USERDATA = 0x11
    DESC = 0x12
    S_MOTION_REFS_0 = 0x13
    SWICONTAINER = 0x14
    GCONTAINER = 0x15
    FASTPATH = 0x16


NORMAL = 'NORMAL'
HIERRARHY = 'HIERRARHY'
PROGRESSIVE = 'PROGRESSIVE'
SKELETON_ANIM = 'SKELETON_ANIM'
SKELETON_GEOMDEF_PM = 'SKELETON_GEOMDEF_PM'
SKELETON_GEOMDEF_ST = 'SKELETON_GEOMDEF_ST'
LOD = 'LOD'
TREE_ST = 'TREE_ST'
PARTICLE_EFFECT = 'PARTICLE_EFFECT'
PARTICLE_GROUP = 'PARTICLE_GROUP'
SKELETON_RIGID = 'SKELETON_RIGID'
TREE_PM = 'TREE_PM'

model_types = {
    0x0: NORMAL,
    0x1: HIERRARHY,
    0x2: PROGRESSIVE,
    0x3: SKELETON_ANIM,
    0x4: SKELETON_GEOMDEF_PM,
    0x5: SKELETON_GEOMDEF_ST,
    0x6: LOD,
    0x7: TREE_ST,
    0x8: PARTICLE_EFFECT,
    0x9: PARTICLE_GROUP,
    0xa: SKELETON_RIGID,
    0xb: TREE_PM
}

OGF_VERTEXFORMAT_FVF = 0x112
OGF4_VERTEXFORMAT_FVF_1L = 0x12071980
OGF4_VERTEXFORMAT_FVF_2L = 0x240e3300
OGF4_VERTEXFORMAT_FVF_NL = 0x36154c80
