from dataclasses import dataclass

from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from .decorator import property_type


@property_type(name='bool')
@dataclass(slots=True)
class gBool(BinarySerializable):
    value: bool

    def read(self, reader: BinaryReader) -> None:
        self.value = reader.read_bool()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_bool(self.value)
