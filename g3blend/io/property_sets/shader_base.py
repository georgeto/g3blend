from dataclasses import dataclass
from typing import Optional

from .property_set import PropertySet
from .shader_element_base import eCShaderEllementBase
from .util import read_property_set, write_property_set
from ..binary import BinaryReader, BinaryWriter
from ..types import bCGuid


@dataclass
class eCShaderBase(eCShaderEllementBase):
    shader_elements: list[PropertySet]

    def get_element(self, token: bCGuid) -> Optional[eCShaderEllementBase]:
        return next((e for e in self.shader_elements if isinstance(e, eCShaderEllementBase) and e.token == token), None)

    def read_post_version(self, reader: BinaryReader) -> None:
        if reader.read_u16() != 1:
            raise ValueError('Unsupported eCShaderBase version.')

        super().read_post_version(reader)
        self.shader_elements = reader.read_list(read=read_property_set)

    def write_post_version(self, writer: BinaryWriter) -> None:
        writer.write_u16(1)
        super().write_post_version(writer)
        writer.write_list(self.shader_elements, write=write_property_set)
