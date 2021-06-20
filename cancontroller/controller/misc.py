from random import randint

from typing import List


def generate_random_data(size: int) -> List[int]:
    return [randint(0, 0xFF) for i in range(size)]
