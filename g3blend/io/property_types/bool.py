from dataclasses import dataclass

from .decorator import property_type
from ..binary import BinaryReader, BinarySerializable, BinaryWriter


@property_type(name='bool')
@dataclass(slots=True)
class gBool(BinarySerializable):
    value: bool

    def read(self, reader: BinaryReader) -> None:
        self.value = reader.read_bool()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_bool(self.value)
