from dataclasses import dataclass

from ..binary import BinaryReader, BinaryWriter
from .decorator import property_set
from .resource_base import eCResourceBase_PS
from .shader_base import eCShaderBase
from .util import read_property_set, write_property_set


@property_set
@dataclass
class eCResourceShaderMaterial_PS(eCResourceBase_PS):
    shader: eCShaderBase

    def read_post_version(self, reader: BinaryReader) -> None:
        super().read_post_version(reader)
        self.shader = read_property_set(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        super().write_post_version(writer)
        write_property_set(writer, self.shader)
