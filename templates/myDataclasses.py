from dataclasses import asdict, dataclass, field
from typing import Dict, List


@dataclass
class StoryInfo:
    title: str = ""
    media_source: str = ""
    authors: List[str] = field(default_factory=lambda: [])
    release: str = ""
    tags: List[str] = field(default_factory=lambda: [])
    desc: str = ""


@dataclass
class DesignInfo:
    font_size: int = 20
    fg: list[float] = field(default_factory=lambda: [151 / 255, 27 / 255, 47 / 255, 1])
    bg: list[float] = field(default_factory=lambda: [0.9, 0.9, 0.9, 1])
    hl: list[float] = field(
        default_factory=lambda: [209 / 255, 231 / 255, 224 / 255, 1]
    )  # [200/255, 15/255, 46/255, 1]



@dataclass(frozen=True)
class Speaker:
    name: str
    depiction: str


@dataclass(frozen=True)
class TalkItem:
    speaker: Speaker
    text: str
    triples: Dict[str, List[str]]


@dataclass(frozen=True)
class TalkInfo:
    dialogue: List[TalkItem]
    background: str
