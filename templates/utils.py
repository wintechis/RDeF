from typing import List


def convert_color(rgb: List[int]) -> List[float]:
    if len(rgb) == 3: rgb.append(255)
    return [val/255 for val in rgb]