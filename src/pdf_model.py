from itertools import batched
from pathlib import Path
import re
from re import Match

from src.rdw import ResizableDragableWidget as RDW


class RDWModel:
    def __init__(self, path: str|Path, size: tuple[int, int], pos: tuple[int, int]):
        self.path = path
        self.size = size
        self.pos = pos


class PdfModel:
    def __init__(self, path: str|Path):
        self.path = path
        self.rdws: list[RDW] = []
        # self.arrows = []
        # self.blocks = []

    @classmethod
    def _parse_begin_end_block(cls, m1: Match, m2: Match) -> RDWModel|None:
        patter_begin = '%%.*BEAMER_GUI::.*::BEGIN'
        patter_end = '%%.*BEAMER_GUI::.*::END'
        if re.search('%%.*BEAMER_GUI::.*::BEGIN', m1.string[m1.start():m1.end()]):
            ...
        else:
            

    @classmethod
    def parse(cls, path: str|Path):

        content = Path(path).read_text()
        for m1, m2 in batched(re.finditer('%%.*BEAMER_GUI::.*::(BEGIN|END)', content), n=2):
            
