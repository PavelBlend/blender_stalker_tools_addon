
class Chunks:
    class Level:
        HEADER = 0x1
        SHADERS = 0x2
        VISUALS = 0x3
        PORTALS = 0x4
        LIGHT_DYNAMIC = 0x6
        GLOWS = 0x7
        SECTORS = 0x8

    class Geometry:
        VB = 0x9
        IB = 0xa
        SWIS = 0xb

    class Sector:
        PORTALS = 0x1
        ROOT = 0x2


# vertex buffer type names
FLOAT2 = 'FLOAT2'
FLOAT3 = 'FLOAT3'
FLOAT4 = 'FLOAT4'
D3DCOLOR = 'D3DCOLOR'
SHORT2 = 'SHORT2'
SHORT4 = 'SHORT4'
UNUSED = 'UNUSED'

# vertex buffer method names
DEFAULT = 'DEFAULT'
PARTIALU = 'PARTIALU'
PARTIALV = 'PARTIALV'
CROSSUV = 'CROSSUV'
UV = 'UV'

# vertex buffer usage names
POSITION = 'POSITION'
BLENDWEIGHT = 'BLENDWEIGHT'
BLENDINDICES = 'BLENDINDICES'
NORMAL = 'NORMAL'
PSIZE = 'PSIZE'
TEXCOORD = 'TEXCOORD'
TANGENT = 'TANGENT'
BINORMAL = 'BINORMAL'
TESSFACTOR = 'TESSFACTOR'
POSITIONT = 'POSITIONT'
COLOR = 'COLOR'
FOG = 'FOG'
DEPTH = 'DEPTH'
SAMPLE = 'SAMPLE'

types = {
    1: FLOAT2,
    2: FLOAT3,
    3: FLOAT4,
    4: D3DCOLOR,
    6: SHORT2,
    7: SHORT4,
    17: UNUSED
}

methods = {
    0: DEFAULT,
    1: PARTIALU,
    2: PARTIALV,
    3: CROSSUV,
    4: UV
}

usage = {
    0: POSITION,
    1: BLENDWEIGHT,
    2: BLENDINDICES,
    3: NORMAL,
    4: PSIZE,
    5: TEXCOORD,
    6: TANGENT,
    7: BINORMAL,
    8: TESSFACTOR,
    9: POSITIONT,
    10: COLOR,
    11: FOG,
    12: DEPTH,
    12: SAMPLE
}
