
class Chunks:
    HEADER = 0x1
    SWIDATA = 0x6
    CHILDREN_L = 0xa
    LODDEF2 = 0xb
    TREEDEF2 = 0xc
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
