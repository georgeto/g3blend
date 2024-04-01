from dataclasses import dataclass

from .guid import bCGuid
from ..binary import BinaryReader, BinarySerializable, BinaryWriter


@dataclass(slots=True)
class eCColorSrcProxy(BinarySerializable):
    color_component: int
    guid: bCGuid

    def read(self, reader: BinaryReader) -> None:
        self.color_component = reader.read_u32()
        self.guid = reader.read(bCGuid)

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u32(self.color_component)
        writer.write(self.guid)
