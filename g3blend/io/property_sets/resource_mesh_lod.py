from dataclasses import dataclass, field

from .decorator import property_set
from .resource_base import eCResourceBase_PS
from ..binary import BinaryReader, BinaryWriter


@property_set
@dataclass
class eCResourceMeshLoD_PS(eCResourceBase_PS):
    meshes: list[str] = field(default_factory=list)

    def read_post_version(self, reader: BinaryReader):
        super().read_post_version(reader)
        self.meshes = reader.read_list(read=BinaryReader.read_entry)

    def write_post_version(self, writer: BinaryWriter):
        super().write_post_version(writer)
        writer.write_list(self.meshes, write=BinaryWriter.write_entry)
