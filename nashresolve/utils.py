from typing import Any

import numpy as np


def replace(array: np.ndarray, index: int, value: Any) -> np.ndarray:
    array = array.copy()
    array[index] = value

    return array


def limit(value: int, lower: int, upper: int) -> int:
    return min(max(value, lower), upper)
