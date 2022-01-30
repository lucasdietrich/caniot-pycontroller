from random import randint

from typing import List

from cancontroller.caniot.models import BufferType


def fit_buffer(buffer: BufferType, expected_len: int, padding: int = 0x00) -> BufferType:
    buffer_len = len(buffer)

    output: BufferType = []

    for i, b in enumerate(buffer):
        if i < expected_len:
            output.append(b)
        else:
            break

    if buffer_len < expected_len:
        output += [padding] * (expected_len - buffer_len)

    return output


def generate_random_data(size: int) -> List[int]:
    return [randint(0, 0xFF) for _ in range(size)]


def read_bit(number: int, bit: int) -> bool:
    return bool(number & (1 << bit))