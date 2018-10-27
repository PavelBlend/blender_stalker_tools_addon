
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


# format versions
XRLC_VERSION_13 = 13
XRLC_VERSION_14 = 14
XRLC_SUPPORT_VERSIONS = [
    XRLC_VERSION_13,
    XRLC_VERSION_14
]

# others
PORTAL_SIZE = 80
PORTAL_VERTEX_COUNT = 6
LIGHT_DYNAMIC_SIZE = 108
GLOW_SIZE = 18
SECTOR_PORTAL_SIZE = 2
