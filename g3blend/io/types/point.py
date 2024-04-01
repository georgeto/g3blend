from dataclasses import dataclass

from ..binary import BinaryReader, BinarySerializable, BinaryWriter


@dataclass(slots=True)
class bCPoint(BinarySerializable):
    x: int
    y: int

    def read(self, reader: BinaryReader) -> None:
        self.x = reader.read_i32()
        self.y = reader.read_i32()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_i32(self.x)
        writer.write_i32(self.y)
