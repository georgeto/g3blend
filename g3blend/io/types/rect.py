from dataclasses import dataclass

from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from . import bCPoint


@dataclass(slots=True)
class bCRect(BinarySerializable):
    top_left: bCPoint
    bottom_right: bCPoint

    def read(self, reader: BinaryReader) -> None:
        self.top_left = reader.read(bCPoint)
        self.bottom_right = reader.read(bCPoint)

    def write(self, writer: BinaryWriter) -> None:
        self.top_left.write(writer)
        self.bottom_right.write(writer)

    @property
    def left(self) -> int:
        return self.top_left.x

    @property
    def right(self) -> int:
        return self.bottom_right.x

    @property
    def top(self) -> int:
        return self.top_left.y

    @property
    def bottom(self) -> int:
        return self.bottom_right.y

    @property
    def width(self) -> int:
        return self.bottom_right.x - self.top_left.x

    @property
    def height(self) -> int:
        return self.bottom_right.y - self.top_left.y
