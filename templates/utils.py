import os
from typing import List


def convert_color(rgb: List[int]) -> List[float]:
    if len(rgb) == 3:
        rgb.append(255)
    return [val / 255 for val in rgb]


def is_file(file: str, base: str = "") -> bool:
    f = os.path.join(base, file) if base else file
    return os.path.isfile(f)


def get_file_list(path: str, ext: str = "") -> List[str]:
    """returns a list of all turtle files"""
    names = os.listdir(path)
    entries = list(map(lambda x: os.path.join(path, x), names))
    l = [entry for entry in entries if os.path.isfile(entry)]
    if not ext:
        return l
    return [entry for entry in l if os.path.splitext(entry)[1] == ext]


def join_path(*args) -> str:
    return os.path.join(*args)
