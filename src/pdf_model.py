from itertools import batched
from pathlib import Path
import re
from re import Match


class RDWModel:
    def __init__(self, path: str|Path, width: int, pos: tuple[int, int], block_span: tuple[int, int], content_span: tuple[int, int]):
        self.path = path
        self.width = width
        self.pos = pos
        self.block_span = block_span
        self.content_span = content_span

    @classmethod
    def from_re_match(cls, m1: Match, m2: Match):
        tex = m1.string[m1.start():m2.end()]
        mxy = re.search(r'\[ *xshift *= *(?P<x>\d+)* *, *yshift *= *- *(?P<y>\d+)* *\]', tex)
        mpw = re.search(r'\[width *= *(?P<width>\d+)\w+\]{ *(?P<path>[^}]+) *}', tex)
        return cls(path=Path(mpw['path']),
                   width=int(mpw['width']),
                   pos=(int(mxy['x']), int(mxy['y'])),
                   block_span=(m1.start(), m2.end()),
                   content_span=(m1.end(), m2.start()))

    def to_tex(self) -> str:
        (x, y), width, path = self.pos, self.width, self.path
        return  (rf'\begin{{tikzpicture}}[remember picture, overlay]' + '\n'
                rf'  \node[anchor=north west] at ([xshift={x - 6}, yshift=-{y - 6}] current page.north west) {{\includegraphics[width={width}pt]{{{path}}}}};' + '\n'
                rf'\end{{tikzpicture}}')


class PdfModel:
    def __init__(self, path: str|Path, rdw_models: list[RDWModel]):
        self.path = path
        self.rdws: list[RDWModel] = rdw_models
        # self.arrows = []
        # self.blocks = []

    @classmethod
    def _parse_begin_end_block(cls, m1: Match, m2: Match) -> RDWModel|None:
        if m1['type'] == 'BEGIN' and m2['type'] == 'END' and m1['element'] == m2['element']:
            match m1['element']:
                case 'RDW':
                    return RDWModel.from_re_match(m1, m2)
                case _:
                    return

    @classmethod
    def parse(cls, path: str|Path):
        content = Path(path).read_text()
        models = [cls._parse_begin_end_block(m1, m2) 
                  for m1, m2 in batched(re.finditer(r'%% *BEAMER_GUI *(?P<type>\w+) *(?P<element>\w+)', content), n=2)]
        rdw_models = [m for m in models if isinstance(m, RDWModel)]
        return cls(path, rdw_models)


if __name__ == "__main__":
    model = PdfModel.parse('../tex/main.tex')
    print(model)
