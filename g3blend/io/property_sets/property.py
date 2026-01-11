from dataclasses import dataclass
from typing import Generic, Optional

from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from ..property_types import PropertyTypeRegistry, TPropertyType


@dataclass(slots=True)
class Property(BinarySerializable, Generic[TPropertyType]):
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[TPropertyType] = None
    _magic_value: int = 30  # 0x1E00

    def read(self, reader: BinaryReader) -> None:
        self.name = reader.read_entry()
        self.type = reader.read_entry()
        self._magic_value = reader.read_u16()
        self.value = PropertyTypeRegistry.instantiate(self.name, self.type)
        self.value.read_sized(reader, reader.read_u32())

    def write(self, writer: BinaryWriter) -> None:
        writer.write_entry(self.name)
        writer.write_entry(self.type)
        writer.write_u16(self._magic_value)
        size_offset = writer.position()
        writer.write_u32(0)
        writer.write(self.value)
        with writer.at_position(size_offset) as pos:
            writer.write_u32(pos - size_offset - 4)

    def __str__(self) -> str:
        return f'{self.type} {self.name} = {self.value}'
