from dataclasses import dataclass

from ..binary import BinaryReader, BinaryWriter
from ..types import FloatColor
from .decorator import property_type


@property_type
@dataclass
class bCFloatColor(FloatColor):
    _vftable: int

    def read(self, reader: BinaryReader) -> None:
        self._vftable = reader.read_u32()
        super().read(reader)

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u32(self._vftable)
        super().write(writer)
