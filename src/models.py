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


@dataclass
class Model:
    template_path = Path()
    pid = ''

    nid: str

    @classmethod
    def from_block(cls, block: Block): ...

    def to_tex(self, **kwargs):
        content = Path(self.template_path).read_text()
        return content.format(**kwargs)


@dataclass
class RDWModel(Model):
    template_path = Path('templates/rdw.template')
    pid = 'RDW'

    pos_pattern = reg(r'\[xshift=-?(?P<x>\F),yshift=-?(?P<y>\F)\]')
    width_path_pattern = reg(r'\[width=(?P<width>\F)\w+\]{(?P<path>[^}]+)}')

    path: Path
    width: float
    pos: tuple[float, float]
    nid: str

    @classmethod
    def from_block(cls, block: Block):
        mxy = re.search(cls.pos_pattern, block.content)
        mpw = re.search(cls.width_path_pattern, block.content)
        return cls(nid=block.nid,
                   path=Path(mpw['path']),
                    width=float(mpw['width']),
                    pos=(float(mxy['x']), float(mxy['y'])))

    def to_tex(self):
        return super().to_tex(x=self.pos[0], y=self.pos[1], width=self.width, path=self.path)


@dataclass
class TextStrucModel(Model):
    template_path = Path('templates/text_struc.template')
    pid = 'TEXT_STRUC'

    text: str

    @classmethod
    def from_block(cls, block: Block):
        return cls(nid=block.nid, text=block.content)

    def to_tex(self):
        return super().to_tex(text=self.text)


# TODO: code this class
@dataclass
class ImgStrucModel(Model):
    template_path = Path('templates/img_struc.template')
    pid = 'IMG_STRUC'

    path: Path
    width: float # i think it's necessary

    @classmethod
    def from_block(cls, block: Block):
        ...

    def to_tex(self):
        return super().to_tex(path=self.path, width=self.width) # TODO: write the template


@dataclass
class LayoutStrucModel(Model):
    children: list[Self]

    def get_children_from_block(cls, block):
        children: list[Model] = []
        for b in block.children:
            match b.pid:
                case TextStrucModel.pid: children.append(TextStrucModel.from_block(b))
                case ImgStrucModel.pid: children.append(ImgStrucModel.from_block(b))
                case _: ...# unexpected child block: raise error ?
        return children


class VStrucModel(LayoutStrucModel):
    template_path = 'templates/v_struc.template'
    pid = 'V_STRUC'

    @classmethod
    def from_block(cls, block):
        return cls(super().get_children_from_block(block))


class HStrucModel(LayoutStrucModel):
    template_path = 'templates/h_struc.template'
    pid = 'H_STRUC'

    stretch_pattern = reg(r'\\begin{minipage}{(\F) *\\textwidth}')

    stretches_ratio: list[float]

    @classmethod
    def from_block(cls, block):
        stretches_ratio = [float(m.groups()[0]) for m in re.finditer(cls.stretch_pattern, block.content)]
        return cls(super().get_children_from_block(block), stretches_ratio)


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
        print(f'Find next block: parsing {start} {end}')
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
                        self.content[m1.end() + start:m2.start() + start],
                        pid,
                        nid,
                        [])

    def parse(self, start: int=0, end: int|None=None):
        print(f'Parse: parsing {start} {end}')
        blocks = []
        while 'there are still blocks to parse':
            b = self.find_next_block(start, end) # TODO: capture parsing error
            if not b:
                break
            print('Found block'); print(b); print()
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

    # def texify(self, model: Model, id: str=''):
    #     if not id:
    #         id = self.new_id(type(model))
    #     match model:
    #         case RDWModel()|TextStrucModel()|ImgStrucModel():
    #             content = model.to_tex()
    #             return Block.tex(id, content)
    #         case VStrucModel():
    #             return '\n\n\\vfill\n\n'.join(self.texify())
