from dataclasses import dataclass

from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from .decorator import property_type


@property_type
@dataclass(slots=True)
class bTPropertyContainer(BinarySerializable):
    enum_value: int

    def read(self, reader: BinaryReader) -> None:
        reader.read_u16()  # Version
        self.enum_value = reader.read_u32()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u16(1)
        writer.write_u32(self.enum_value)
