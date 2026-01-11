from dataclasses import dataclass, field

from ..binary import BinaryReader, BinaryWriter
from ..structs.mesh_element import eCMeshElement
from .decorator import property_set
from .resource_base import eCResourceBase_PS


@property_set
@dataclass
class eCResourceMeshComplex_PS(eCResourceBase_PS):
    resource_priority: float = 0.0
    mesh_elements: list[eCMeshElement] = field(default_factory=list)

    def read_post_version(self, reader: BinaryReader):
        super().read_post_version(reader)

        if self.version < 0x22:
            raise ValueError('eCResourceMeshComplex_PS: Old format is not supported.')

        self.resource_priority = reader.read_float()
        self.mesh_elements = reader.read_list(eCMeshElement)

    def write_post_version(self, writer: BinaryWriter):
        super().write_post_version(writer)
        writer.write_float(self.resource_priority)
        writer.write_list(self.mesh_elements)
