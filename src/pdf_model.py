from itertools import batched
from pathlib import Path
import re
from re import Match


class RDWModel:
    def __init__(self, id: str, path: str|Path, width: int, pos: tuple[int, int], block_span: tuple[int, int]):
        self.id = id
        self.path = path
        self.width = width
        self.pos = pos
        self.block_span = block_span

    @classmethod
    def from_re_match(cls, id: str, m1: Match, m2: Match):
        tex = m1.string[m1.start():m2.end()]
        mxy = re.search(r'\[ *xshift *= *(?P<x>\d+\.\d+)* *, *yshift *= *- *(?P<y>\d+\.\d+)* *\]', tex)
        mpw = re.search(r'\[width *= *(?P<width>\d+\.\d+)\w+\]{ *(?P<path>[^}]+) *}', tex)
        return cls(id=id,
                   path=Path(mpw['path']),
                   width=float(mpw['width']),
                   pos=(float(mxy['x']), float(mxy['y'])),
                   block_span=(m1.start(), m2.end()))

    def to_tex(self) -> str:
        (x, y), width, path = self.pos, self.width, self.path
        return  (rf'%% BEAMER_GUI BEGIN {self.id}' + '\n'
                rf'\begin{{tikzpicture}}[remember picture, overlay]' + '\n'
                rf'  \node[anchor=north west] at ([xshift={x - 6}, yshift=-{y - 6}] current page.north west) {{\includegraphics[width={width}pt]{{{path}}}}};' + '\n'
                rf'\end{{tikzpicture}}' + '\n'
                f'%% BEAMER_GUI END {self.id}')
        # TODO: this -6 should be investigated (plus, it's not 100% precise)


class PdfModel:
    def __init__(self, path: str|Path, rdw_models: list[RDWModel]):
        self.path = path
        self.rdws: list[RDWModel] = rdw_models
        # self.arrows = []
        # self.blocks = []

    @classmethod
    def _parse_begin_end_block(cls, m1: Match, m2: Match, ids: set) -> RDWModel|None:
        if  m1['type'] == 'BEGIN' and m2['type'] == 'END' and\
            m1['element'] == m2['element'] and\
            m1['id'] == m2['id'] and (id := f'{m1["element"]}_{m1["id"]}') not in ids:

            if m1['element'] in ['RDW']:
                ids.add(id)
                if m1['element'] == 'RDW':
                    return RDWModel.from_re_match(id, m1, m2)

    @classmethod
    def parse(cls, path: str|Path):
        content = Path(path).read_text()
        ids = set()
        models = [cls._parse_begin_end_block(m1, m2, ids) 
                  for m1, m2 in batched(re.finditer(r'%% *BEAMER_GUI *(?P<type>\w+) *(?P<element>\w+)_(?P<id>\d+)', content), n=2)]
        rdw_models = [m for m in models if isinstance(m, RDWModel)]
        return cls(path, rdw_models)


if __name__ == "__main__":
    model = PdfModel.parse('../tex/main.tex')
    print(model)
