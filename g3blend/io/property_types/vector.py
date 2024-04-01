from dataclasses import dataclass

from .decorator import property_type
from ..binary import BinaryReader, BinarySerializable, BinaryWriter


@property_type
@dataclass(slots=True)
class bCVector(BinarySerializable):
    x: float
    y: float
    z: float

    def read(self, reader: BinaryReader) -> None:
        self.x = reader.read_float()
        self.y = reader.read_float()
        self.z = reader.read_float()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_float(self.x)
        writer.write_float(self.y)
        writer.write_float(self.z)
