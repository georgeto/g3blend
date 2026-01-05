from dataclasses import dataclass

from .property_set import PropertySet
from ..binary import BinaryReader, BinaryWriter
from ..types import bCGuid, bCRect


@dataclass(slots=True)
class eCShaderEllementBase(PropertySet):
    token: bCGuid
    editor_layout: bCRect

    def read_post_version(self, reader: BinaryReader) -> None:
        if reader.read_u16() != 1:
            raise ValueError('Unsupported eCShaderEllementBase version.')
        self.token = reader.read(bCGuid)
        self.editor_layout = reader.read(bCRect)

    def write_post_version(self, writer: BinaryWriter) -> None:
        writer.write_u16(1)
        writer.write(self.token)
        writer.write(self.editor_layout)
