from dataclasses import dataclass
from typing import Optional, Type

from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from ..property_types import TPropertyType
from .property import Property
from .property_desc import PropertyDescriptor


@dataclass
class PropertySet(BinarySerializable):
    name: str
    properties: list[Property]
    version: int
    _property_version: int
    _deadcode_position: int

    def __init__(self, name: str, version: int):
        self.name = name
        self.properties = []
        self.version = version
        self._property_version = 30

    def read(self, reader: BinaryReader):
        object_version = reader.read_u16()
        self._deadcode_position = reader.read_u32() + reader.position()

        if object_version == 0x01:
            reader.read_entry()

        if object_version <= 0x51:
            reader.read_guid()

        self._property_version = reader.read_u16()
        self.properties = reader.read_list(Property)
        self.read_pre_version(reader)
        self.version = reader.read_u16()
        self.read_post_version(reader)

    def read_pre_version(self, reader: BinaryReader):
        pass

    def read_post_version(self, reader: BinaryReader):
        pass

    def write(self, writer: BinaryWriter):
        writer.write_u16(0x53)
        size_offset = writer.position()
        writer.write_u32(0)
        writer.write_u16(self._property_version)
        writer.write_list(self.properties)

        self.write_pre_version(writer)
        writer.write_u16(self.version)
        self.write_post_version(writer)

        with writer.at_position(size_offset) as pos:
            writer.write_u32(pos - size_offset - 4)

    def write_pre_version(self, writer: BinaryWriter):
        pass

    def write_post_version(self, writer: BinaryWriter):
        pass

    def get_name(self) -> str:
        return self.name

    def type_equal(self, type: str) -> bool:
        return self.name == type

    def add_property(self, prop: Property, predecessor: Optional[str] = None) -> 'PropertySet':
        if predecessor is None:
            self.properties.insert(0, prop)
        else:
            for i in range(len(self.properties)):
                if self.properties[i].name == predecessor:
                    self.properties.insert(i + 1, prop)
                    return self
            self.properties.append(prop)
        return self

    def add_property_by_desc(
        self,
        desc: PropertyDescriptor[TPropertyType],
        value: TPropertyType,
        predecessor: Optional[PropertyDescriptor] = None,
    ) -> 'PropertySet':
        prop = Property(desc.name, desc.get_data_type_name(), value)
        if predecessor is None:
            self.properties.insert(0, prop)
        else:
            for i in range(len(self.properties)):
                if self.properties[i].name == predecessor.name:
                    self.properties.insert(i + 1, prop)
                    return self
            self.properties.append(prop)
        return self

    def property_no_throw(self, name: str) -> Optional[TPropertyType]:
        for prop in self.properties:
            if prop.name == name:
                return prop.value
        return None

    def property(self, name: str) -> TPropertyType:
        for prop in self.properties:
            if prop.name == name:
                return prop.value
        raise ValueError(self._no_such_property_error(name))

    def property_no_throw_by_type(self, name: str, type: Type[TPropertyType]) -> Optional[TPropertyType]:
        for prop in self.properties:
            if prop.name == name:
                return type.cast(prop)
        return None

    def property_by_type(self, name: str, type: Type[TPropertyType]) -> TPropertyType:
        for prop in self.properties:
            if prop.name == name:
                return type.cast(prop.value)
        raise ValueError(self._no_such_property_error(name))

    def property_by_occurence(self, name: str, occurence: int) -> TPropertyType:
        skipped = 0
        for prop in self.properties:
            if prop == name and occurence == skipped + 1:
                return prop.value
        raise ValueError(self._no_such_property_error(name))

    def property_by_type_and_occurence(self, name: str, type: Type[TPropertyType], occurence: int) -> TPropertyType:
        skipped = 0
        for prop in self.properties:
            if prop == name and occurence == skipped + 1:
                return type.cast(prop.value)
        raise ValueError(self._no_such_property_error(name))

    def property_by_desc(self, desc: PropertyDescriptor[TPropertyType]) -> TPropertyType:
        for prop in self.properties:
            if prop.name == desc.name:
                return prop.value
        raise ValueError(self._no_such_property_error(desc.name))

    def property_no_throw_by_desc(self, desc: PropertyDescriptor[TPropertyType]) -> Optional[TPropertyType]:
        for prop in self.properties:
            if prop.name == desc.name:
                return prop.value
        return None

    def property_by_desc_and_occurence(self, desc: PropertyDescriptor[TPropertyType], occurrence: int) -> TPropertyType:
        skipped = 0
        for prop in self.properties:
            if prop.name == desc.name and occurrence == skipped + 1:
                skipped += 1
                return prop.value
        raise ValueError(self._no_such_property_error(desc.name))

    def has_property(self, desc: PropertyDescriptor) -> bool:
        return any(p.name == desc.name for p in self.properties)

    def has_property_by_name(self, name: str) -> bool:
        return any(p.name == name for p in self.properties)

    def set_property_data(self, desc: PropertyDescriptor[TPropertyType], data: TPropertyType) -> None:
        for prop in self.properties:
            if prop.name == desc.name:
                prop.value = data
                return
        self.add_property_by_desc(desc, data)

    def __str__(self) -> str:
        return self.name

    def property_count(self) -> int:
        return len(self.properties)

    def _no_such_property_error(self, name: str) -> str:
        return f"The class '{self.name}' has no property with name '{name}'."
