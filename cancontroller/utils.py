import math
import re
import datetime
import struct

from random import randint
from typing import List

re_hex = re.compile(r"^0x(?P<hex>[0-9]+)$")
re_dec = re.compile(r"^(?P<dec>[0-9]+)$")

def extract_bits_from_bytearray(raw: bytearray, bit_position: int = 0, size_bits: int = 10):
    raw = bytearray(raw)

    length = len(raw)
    assert length <= 8

    value, = struct.unpack("<Q", raw.ljust(8, b'\0'))

    return (value >> bit_position) & (pow(2, size_bits) - 1)


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

def generate_random_data(size: int) -> List[int]:
    return [randint(0, 0xFF) for _ in range(size)]

def read_bit(number: int, bit: int) -> bool:
    return bool(number & (1 << bit))

def fmttimestamp(timestamp_seconds: int) -> str:
    return datetime.datetime.fromtimestamp(timestamp_seconds).strftime("%Y-%m-%d %H:%M:%S")