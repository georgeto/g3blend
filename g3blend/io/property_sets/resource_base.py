from dataclasses import dataclass

from .decorator import property_set
from .property_set import PropertySet
from ..binary import BinaryReader, BinaryWriter


@property_set
@dataclass
class eCResourceBase_PS(PropertySet):
    size: int

    def read_post_version(self, reader: BinaryReader) -> None:
        resource_version = reader.read_u16()
        self.size = reader.read_u32() if resource_version >= 0x17 else 0

        if resource_version < 0x1e:
            if reader.read_u16() > 1:
                reader.skip(1)

    def write_post_version(self, writer: BinaryWriter) -> None:
        writer.write_u16(0x1e)
        writer.write_u32(self.size)
