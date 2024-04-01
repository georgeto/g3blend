from dataclasses import dataclass

from .decorator import property_type
from .vector import bCVector
from ..binary import BinaryReader, BinarySerializable, BinaryWriter


@property_type
@dataclass(slots=True)
class bCBox(BinarySerializable):
    min: bCVector
    max: bCVector

    def read(self, reader: BinaryReader) -> None:
        self.min = reader.read_vec3()
        self.max = reader.read_vec3()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_vec3(self.min)
        writer.write_vec3(self.max)
