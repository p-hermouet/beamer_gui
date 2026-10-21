from dataclasses import dataclass
from itertools import batched, count
from pathlib import Path
import re
from re import Match
from typing import Self


# class RDWModel:
#     prefix_id = 'RDW'
#     pos_pattern = reg(r'\[xshift=-?(?P<x>\F),yshift=-?(?P<y>\F)\]')
#     width_path_pattern = reg(r'\[width=(?P<width>\F)\w+\]{(?P<path>[^}]+)}')

#     def __init__(self, id: str, path: str|Path, width: int, pos: tuple[int, int], block_span: tuple[int, int]|None=None):
#         self.id = id
#         self.path = path
#         self.width = width
#         self.pos = pos
#         self.block_span = block_span

#     @classmethod
#     def from_re_match(cls, id: str, m1: Match, m2: Match):
#         tex = m1.string[m1.start():m2.end()]
#         mxy = re.search(cls.pos_pattern, tex)
#         # TODO: this regex does not capture when the position x/y are int (ie w/o "."), fix it
#         mpw = re.search(cls.width_path_pattern, tex)
#         return cls(id=id,
#                    path=Path(mpw['path']),
#                    width=float(mpw['width']),
#                    pos=(float(mxy['x']), float(mxy['y'])),
#                    block_span=(m1.start(), m2.end()))

#     def to_tex(self) -> str:
#         (x, y), width, path = self.pos, self.width, self.path
#         return  (rf'%% BEAMER_GUI BEGIN {self.id}' + '\n'
#                 rf'\begin{{tikzpicture}}[remember picture, overlay]' + '\n'
#                 rf'  \node[anchor=north west] at ([xshift={x - 6}, yshift=-{y - 6}] current page.north west) {{\includegraphics[width={width}pt]{{{path}}}}};' + '\n'
#                 rf'\end{{tikzpicture}}' + '\n'
#                 f'%% BEAMER_GUI END {self.id}')
#         # TODO: this -6 in the template file should be investigated (plus, it's not 100% precise)


# class PdfModel:
#     def __init__(self, path: str|Path, end_frame_pos: int, rdw_models: list[RDWModel]):
#         self.path = path
#         self.end_frame_pos = end_frame_pos
#         self.rdws: list[RDWModel] = rdw_models
#         # self.arrows = []
#         # self.blocks = []

#     @classmethod
#     def _parse_begin_end_block(cls, m1: Match, m2: Match, ids: set) -> RDWModel|None:
#         if  m1['type'] == 'BEGIN' and m2['type'] == 'END' and\
#             m1['element'] == m2['element'] and\
#             m1['id'] == m2['id'] and (id := f'{m1["element"]}_{m1["id"]}') not in ids:

#             if m1['element'] in [RDWModel.prefix_id, StrucModel.prefix_id]:
#                 ids.add(id)
#                 match m1['element']:
#                     case RDWModel.prefix_id:
#                         return RDWModel.from_re_match(id, m1, m2)
#                     case StrucModel.prefix_id:
#                         return StrucModel.from_re_match(id, m1, m2)

#     @classmethod
#     def parse(cls, path: str|Path):
#         content = Path(path).read_text()
#         ids = set()
#         models = [cls._parse_begin_end_block(m1, m2, ids) 
#                     for m1, m2 in batched(re.finditer(reg(r'%% BEAMER_GUI (?P<type>\w+) (?P<element>\w+)_(?P<id>\d+)'), content), n=2)]
#         rdw_models = [m for m in models if isinstance(m, RDWModel)]
#         end_frame_pos = re.search(r'\\end{frame}', content).start()
#         return cls(path, end_frame_pos, rdw_models)

#     # @classmethod
#     # def parse_v2(cls, path: str|Path):
#     #     content = Path(path).read_text()

#     def find_rdw_from_id(self, id: str):
#         try: r = next(r for r in self.rdws if r.id == id)
#         except StopIteration: return
#         return r

#     def find_new_rdw_id(self):
#         return next(f'RDW_{id}' for id in count(1) if f'RDW_{id}' not in [r.id for r in self.rdws])


def reg(expr: str):
    ''' Modifies a regex expression so that it captures any space around symbols `()[]{}=,-`, and defines `\\F` as a pattern for `int or float`.
    '''
    return expr.replace(r'\[', r' \[ ').replace(r'\]', r' \] ').\
            replace(r'\(', r' \( ').replace(r'\)', r' \) ').\
            replace(r'{', r' { ').replace(r'}', r' } ').\
            replace('=', ' = ').replace('-?', ' -? ').replace(',', ' , ').\
            replace(' ', r' *').\
            replace(r'\F', r'\d+(?:\.\d+)?')


@dataclass
class Block:
    start: int
    end: int
    start_content: int
    end_content: int
    content: str
    elem: str
    pid: str
    nid: int

    @property
    def id(self):
        return f'{self.pid}_{self.nid}'


class Model:
    template_path: str|Path

    def to_tex(self, **kwargs):
        content = Path(self.template_path).read_text()
        return content.format(**kwargs)


@dataclass
class RDWModel:
    template_path = Path('templates/rdw.template')
    pid = 'RDW'
    pos_pattern = reg(r'\[xshift=-?(?P<x>\F),yshift=-?(?P<y>\F)\]')
    width_path_pattern = reg(r'\[width=(?P<width>\F)\w+\]{(?P<path>[^}]+)}')

    path: str|Path
    width: float
    pos: tuple[float, float]

    @classmethod
    def from_block(cls, block: Block):
        mxy = re.search(cls.pos_pattern, block.content)
        mpw = re.search(cls.width_path_pattern, block.content)
        return cls(path=Path(mpw['path']),
                    width=float(mpw['width']),
                    pos=(float(mxy['x']), float(mxy['y'])))


class EmptyStrucModel:
    template_path = ...
    pid = 'EMPTY_STRUC'

    children: ...

    @classmethod
    def from_block(cls, block: Block):
        ...


class PdfParser:
    begin_block_pattern = reg(r'%% BEAMER_GUI BEGIN (\w+)_(\d+)')
    end_block_pattern = reg('%% BEAMER_GUI END {id}')

    def __init__(self, path: str|Path):
        self.path = Path(path)
        self.content = self.path.read_text()
        self.blocks: list[Block] = []
        self.parse()

    def find_next_block(self, start: int):
        m1 = re.search(self.begin_block_pattern, self.content[start:])
        if len(m1.groups()) != 2:
            ... # raise parsing error
        pid, nid = m1
        m2 = re.search(self.end_block_pattern.format(id=f'{pid}_{nid}'), self.content[start:])
        if not m2:
            ... # raise parsing error
        block = Block(m1.start + start, m2.end + start, m1.end + start, m2.start + start, self.content[m1.start + start:m2.end + start])
        match pid:
            case RDWModel.pid:
                return RDWModel.from_block(block)
            case EmptyStrucModel.pid:
                return EmptyStrucModel.from_block(block)
            case _:
                ... # raise parsing error

    def parse(self):
        ...

    def find_block_from_id(self, id: str) -> Block:
        try:
            r = next(b for b in self.blocks if b.id == id)
        except StopIteration:
            return
        return r

    def new_id(self, elem: type[Block]) -> str:
        return next(f'{elem.pid}_{id}' for id in count(1) if f'{elem.pid}_{id}' not in [b.id for b in self.blocks])
