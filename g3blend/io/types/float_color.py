from dataclasses import dataclass

from ..binary import BinaryReader, BinarySerializable, BinaryWriter


@dataclass(slots=True)
class FloatColor(BinarySerializable):
    red: float
    green: float
    blue: float

    def read(self, reader: BinaryReader) -> None:
        self.red = reader.read_float()
        self.green = reader.read_float()
        self.blue = reader.read_float()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_float(self.red)
        writer.write_float(self.green)
        writer.write_float(self.blue)
