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