from dataclasses import dataclass

from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from .guid import bCGuid


@dataclass(slots=True)
class eCTexCoordSrcProxy(BinarySerializable):
    vertex_tex_coord: int
    guid: bCGuid

    def read(self, reader: BinaryReader) -> None:
        self.vertex_tex_coord = reader.read_u32()
        self.guid = reader.read(bCGuid)

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u32(self.vertex_tex_coord)
        writer.write(self.guid)
