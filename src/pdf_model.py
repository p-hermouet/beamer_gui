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
        if m1['type'] == 'BEGIN' and m2['type'] == 'END' and m1['element'] == m2['element']:
            match m1['element']:
                case 'RDW':
                    ...
                case _:
                    return

    @classmethod
    def parse(cls, path: str|Path):

        content = Path(path).read_text()
        for m1, m2 in batched(re.finditer(r'%% *BEAMER_GUI *(?P<type>\w+) *(?P<element>\w+)', content), n=2):
            ...


if __name__ == "__main__":
    content = Path().read_text()
    
