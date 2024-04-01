from dataclasses import dataclass

from ..binary import BinaryReader, BinarySerializable, BinaryWriter


@dataclass(slots=True)
class bCGuid(BinarySerializable):
    guid: bytes
    _valid: int

    def read(self, reader: BinaryReader) -> None:
        self.guid = reader.read_bytes(16)
        self._valid = reader.read_u32()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_bytes(self.guid)
        writer.write_u32(self._valid)

    def is_valid(self) -> bool:
        return (self._valid & 0xFF) != 0

    def __eq__(self, other) -> bool:
        if isinstance(other, bCGuid):
            return self.is_valid() == other.is_valid() and self.guid == other.guid
