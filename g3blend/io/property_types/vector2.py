from dataclasses import dataclass

from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from .decorator import property_type


@property_type
@dataclass(slots=True)
class bCVector2(BinarySerializable):
    x: float
    y: float

    def read(self, reader: BinaryReader) -> None:
        self.x = reader.read_float()
        self.y = reader.read_float()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_float(self.x)
        writer.write_float(self.y)
