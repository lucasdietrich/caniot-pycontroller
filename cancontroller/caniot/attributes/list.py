

UIN32_MAX = 2**32 - 1


class Attribute:
    def __init__(self, key: int, name: str, default: int = None, size: int = 4, min_val: int = 0, max_val: int = None, readonly: bool = False):
        self.key = key
        self.name = name
        self.default = default
        self.min_val = min_val
        self.max_val = max_val
        self.readonly = readonly
        self.size = size

        self.parts = int(round(self.size / 4, 0))

        assert self.parts < 16

    def get_part_key(self, n: int = 0) -> int:
        assert n < self.parts

        return self.key + n


class U8Attribute(Attribute):
    pass


class U16Attribute(Attribute):
    pass


class U32Attribute(Attribute):
    pass


attributes_list = {
    Attribute(0x0000, "nodeid", size=1, readonly=True),
    Attribute(0x0010, "version", size=2, readonly=True),
    Attribute(0x0020, "name", size=32, readonly=True),

    Attribute(0x1000, "uptime", readonly=True),
    Attribute(0x1010, "abstime")
}