from dataclasses import dataclass

from .decorator import property_type
from ..binary import BinaryReader, BinarySerializable, BinaryWriter


@property_type(name='float')
@dataclass(slots=True)
class gFloat(BinarySerializable):
    value: float

    def read(self, reader: BinaryReader) -> None:
        self.value = reader.read_float()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_float(self.value)
