from dataclasses import dataclass

from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from .decorator import property_type


@property_type(name='float')
@dataclass(slots=True)
class gFloat(BinarySerializable):
    value: float

    def read(self, reader: BinaryReader) -> None:
        self.value = reader.read_float()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_float(self.value)
