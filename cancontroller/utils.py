import re
import datetime

re_hex = re.compile(r"^0x(?P<hex>[0-9]+)$")
re_dec = re.compile(r"^(?P<dec>[0-9]+)$")

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


def is_bit(n: int, bit: int = 0) -> bool:
    return bool(n & (1 << bit))


def diffseconds(timestamp_seconds: int) -> str:
    diff = datetime.datetime.now() - datetime.datetime.fromtimestamp(timestamp_seconds)

    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    out = f"{seconds}s"
    if minutes:
        out = f"{minutes}m " + out
        if hours:
            out = f"{hours}h " + out
    return out


def fmttimestamp(timestamp_seconds: int) -> str:
    return datetime.datetime.fromtimestamp(timestamp_seconds).strftime("%Y-%m-%d %H:%M:%S")