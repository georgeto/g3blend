from dataclasses import dataclass

from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from .decorator import property_type


@property_type(
    aliases=[
        'bCAnimationResourceString',
        'bCImageOrMaterialResourceString',
        'bCImageResourceString',
        'bCMeshResourceString',
        'bCScriptString',
        'bCSpeedTreeResourceString',
        'eCLocString',
    ]
)
@dataclass(slots=True)
class bCString(BinarySerializable):
    value: str

    def read(self, reader: BinaryReader) -> None:
        self.value = reader.read_entry()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_entry(self.value)
