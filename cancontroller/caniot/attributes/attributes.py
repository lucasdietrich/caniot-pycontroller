

class Attribute:
    def __init__(self, key: int, name: str, size: int = 4, readonly: bool = False):
        self.key = key
        self.name = name
        self.size = size
        self.readonly = readonly

        self.parts = int(round(self.size / 4, 0))

        assert self.parts < 16

    def get_part_key(self, n: int = 0) -> int:
        assert n < self.parts

        return self.key + n


list = [
    Attribute(0x0000, "nodeid", size=1, readonly=True),
    Attribute(0x0010, "version", size=2, readonly=True),
    Attribute(0x0020, "name", size=32, readonly=True),
    Attribute(0x0030, "magic_number", size=4, readonly=True),

    Attribute(0x1010, "time"),

    Attribute(0x1050, "received.total", readonly=True),
    Attribute(0x10C0, "sent.total", readonly=True),
]

def get(name: str) -> Attribute:
    for attr in list:
        if attr.name == name:
            return attr

    return None