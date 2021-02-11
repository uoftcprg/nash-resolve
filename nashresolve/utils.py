from typing import Any

import numpy as np


def replace(array: np.ndarray, index: int, value: Any) -> np.ndarray:
    array = array.copy()
    array[index] = value
    return array
