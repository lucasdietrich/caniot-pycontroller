import re

re_hex = re.compile(r"^0x(?P<hex>[0-9]*)$")
re_dec = re.compile(r"^(?P<dec>[0-9]*)$")


def parse_number(text: str):
    m = re_hex.match(text)
    if m:
        return int(m.group("hex"), 16)

    m = re_dec.match(text)

    if m:
        return int(m.group("dec"), 10)

    return 0

def number_to_hexn(n: int, digits: int = 4):
    fmt = "0x{0:0" + str(int(digits)) + "X}"
    return fmt.format(n)