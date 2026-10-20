from itertools import batched, count
from pathlib import Path
import re
from re import Match
from typing import Self


def reg(expr: str):
    ''' Modifies a regex expression so that it captures any space around symbols `()[]{}=,-`, and defines `\\F` as a pattern for `int or float`.
    '''
    return expr.replace(r'\[', r' \[ ').replace(r'\]', r' \] ').\
            replace(r'\(', r' \( ').replace(r'\)', r' \) ').\
            replace(r'{', r' { ').replace(r'}', r' } ').\
            replace('=', ' = ').replace('-?', ' -? ').replace(',', ' , ').\
            replace(' ', r' *').\
            replace(r'\F', r'\d+(?:\.\d+)?')


class StrucModel:
    prefix_id = 'DEFAULT_STRUC'

    def __init__(self, id: str, children: list[Self], block_span: tuple[int, int]):
        self.id = id
        self.children = children
        self.block_span = block_span

    @classmethod
    def from_re_match(cls, m1: Match, m2: Match):
        tex = m1.string[m1.start():m2.end()]


class RDWModel:
    prefix_id = 'RDW'
    pos_pattern = reg(r'\[xshift=-?(?P<x>\F),yshift=-?(?P<y>\F)\]')
    width_path_pattern = reg(r'\[width=(?P<width>\F)\w+\]{(?P<path>[^}]+)}')

    def __init__(self, id: str, path: str|Path, width: int, pos: tuple[int, int], block_span: tuple[int, int]|None=None):
        self.id = id
        self.path = path
        self.width = width
        self.pos = pos
        self.block_span = block_span

    @classmethod
    def from_re_match(cls, id: str, m1: Match, m2: Match):
        tex = m1.string[m1.start():m2.end()]
        mxy = re.search(cls.pos_pattern, tex)
        # TODO: this regex does not capture when the position x/y are int (ie w/o "."), fix it
        mpw = re.search(cls.width_path_pattern, tex)
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
    def __init__(self, path: str|Path, end_frame_pos: int, rdw_models: list[RDWModel]):
        self.path = path
        self.end_frame_pos = end_frame_pos
        self.rdws: list[RDWModel] = rdw_models
        # self.arrows = []
        # self.blocks = []

    @classmethod
    def _parse_begin_end_block(cls, m1: Match, m2: Match, ids: set) -> RDWModel|None:
        if  m1['type'] == 'BEGIN' and m2['type'] == 'END' and\
            m1['element'] == m2['element'] and\
            m1['id'] == m2['id'] and (id := f'{m1["element"]}_{m1["id"]}') not in ids:

            if m1['element'] in [RDWModel.prefix_id, StrucModel.prefix_id]:
                ids.add(id)
                match m1['element']:
                    case RDWModel.prefix_id:
                        return RDWModel.from_re_match(id, m1, m2)
                    case StrucModel.prefix_id:
                        return StrucModel.from_re_match(id, m1, m2)

    @classmethod
    def parse(cls, path: str|Path):
        content = Path(path).read_text()
        ids = set()
        models = [cls._parse_begin_end_block(m1, m2, ids) 
                    for m1, m2 in batched(re.finditer(reg(r'%% BEAMER_GUI (?P<type>\w+) (?P<element>\w+)_(?P<id>\d+)'), content), n=2)]
        rdw_models = [m for m in models if isinstance(m, RDWModel)]
        end_frame_pos = re.search(r'\\end{frame}', content).start()
        return cls(path, end_frame_pos, rdw_models)

    # @classmethod
    # def parse_v2(cls, path: str|Path):
    #     content = Path(path).read_text()

    def find_rdw_from_id(self, id: str):
        try: r = next(r for r in self.rdws if r.id == id)
        except StopIteration: return
        return r

    def find_new_rdw_id(self):
        return next(f'RDW_{id}' for id in count(1) if f'RDW_{id}' not in [r.id for r in self.rdws])


class PdfModel2:
    begin_block_patter = reg(r'%% BEAMER_GUI BEGIN (\w+)_(\d+)')
    end_block_patter = reg('%% BEAMER_GUI END {id}')

    def __init__(self, path: str|Path):
        self.path = Path(path)
        self.content = self.path.read_text()

    def find_next_block(self, start: int):
        m1 = re.search(self.begin_block_patter, self.content[start:])
        if len(m1.groups()) != 2:
            ... # raise parsing error
        pid, nid = m1
        m2 = re.search(self.end_block_patter.format(id=f'{pid}_{nid}'), self.content[start:])
        if not m2:
            ... # raise parsing error
        match pid:
            case RDWModel.prefix_id:
                ...
            case StrucModel.prefix_id:
                ...
            case _:
                ... # raise parsing error
