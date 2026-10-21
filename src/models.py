from __future__ import annotations

from dataclasses import dataclass
from itertools import batched, count
from pathlib import Path
import re
from re import Match
from typing import Self, Generator


def reg(expr: str):
    ''' Modifies a regex expression so that it captures any space around symbols `()[]{}=,-`, and defines `\\F` as a pattern for `int or float`.
    '''
    return expr.replace(r'\[', r' \[ ').replace(r'\]', r' \] ').\
            replace(r'\(', r' \( ').replace(r'\)', r' \) ').\
            replace(r'{', r' { ').replace(r'}', r' } ').\
            replace('=', ' = ').replace('-?', ' -? ').replace(',', ' , ').\
            replace(' ', r' *').\
            replace(r'\F', r'\d+(?:\.\d+)?')
    # TODO: add pattern to not capture comments


@dataclass
class Block:
    template_path = Path('templates/block.template')

    start: int
    end: int
    start_content: int
    end_content: int
    content: str
    pid: str
    nid: int
    children: list[Self]

    @property
    def id(self):
        return f'{self.pid}_{self.nid}'

    @classmethod
    def tex(cls, id: str, content: str):
        return Path(cls.template_path).read_text().format(id=id, content=content)


class Model:
    template_path: str|Path
    pid: str

    def to_tex(self, **kwargs):
        content = Path(self.template_path).read_text()
        return content.format(**kwargs)


@dataclass
class RDWModel(Model):
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

    def to_tex(self):
        return super().to_tex(x=self.pos[0], y=self.pos[1], width=self.width, path=self.path)


class EmptyStrucModel:
    template_path = ...
    pid = 'EMPTY_STRUC'

    children: ...

    @classmethod
    def from_block(cls, block: Block):
        ...


class FrameParser:
    begin_block_pattern = reg(r'%% BEAMER_GUI BEGIN (\w+)_(\d+)')
    end_block_pattern = '%% BEAMER_GUI END {id}'
    end_frame_pattern = reg(r'\\end{frame}')

    def __init__(self, path: str|Path):
        self.path = Path(path)
        self.content = self.path.read_text()
        self.end = re.search(self.end_frame_pattern, self.content).start()
        self.blocks: list[Block] = []
        self.blocks = self.parse()

    def walk_blocks(self, block: Block|None = None) -> Generator[Block]:
        if not block:
            for b in self.blocks:
                yield b
                yield from self.walk_blocks(b)

    def find_next_block(self, start: int=0, end: int|None=None) -> Block|None:
        m1 = re.search(self.begin_block_pattern, self.content[start:end])
        if m1:
            if len(m1.groups()) != 2:
                ... # TODO: raise parsing error
            pid, nid = m1.groups()
            m2 = re.search(self.end_block_pattern.format(id=f'{pid}_{nid}'), self.content[start:])
            if not m2:
                ... # TODO: raise parsing error
            return Block(m1.start() + start,
                        m2.end() + start,
                        m1.end() + start,
                        m2.start() + start,
                        self.content[m1.start() + start:m2.end() + start],
                        pid,
                        nid,
                        [])

    def parse(self, start: int=0, end: int|None=None):
        blocks = []
        while 'there are still blocks to parse':
            b = self.find_next_block(start, end) # TODO: capture parsing error
            if not b:
                break
            b.children = self.parse(b.start_content, b.end_content)
            blocks.append(b)
            start += b.end + 1
        return blocks

    def find_block_from_id(self, id: str) -> Block:
        try:
            r = next(b for b in self.walk_blocks() if b.id == id)
        except StopIteration:
            return
        return r

    def new_id(self, elem: type[Model]) -> str:
        return next(f'{elem.pid}_{id}' for id in count(1) if f'{elem.pid}_{id}' not in [b.id for b in self.walk_blocks()])
