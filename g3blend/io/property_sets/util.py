from .registry import PropertySetRegistry, TPropertySet
from ..binary import BinaryReader, BinaryWriter

_SUB_CLASS_IDENTIFIER = b'\x01\x00\x01\x01\x00\x01'
_TYPE_TO_VERSION_FILLER = b'\x01\x00\x00\x53\x00'
_DEADCODE = b'\xDE\xAD\xC0\xDE'


def read_property_set(reader: BinaryReader) -> TPropertySet:
    if not reader.expect_bytes(_SUB_CLASS_IDENTIFIER):
        raise ValueError('Not a valid sub class identifier.')
    name = reader.read_entry()
    if not reader.expect_bytes(_TYPE_TO_VERSION_FILLER):
        raise ValueError('Not a valid type to version filler.')
    property_set = PropertySetRegistry.instantiate(name)
    property_set.name = name
    property_set.read(reader)
    return property_set


def read_wrapped_property_set(reader: BinaryReader) -> tuple[TPropertySet, int]:
    version = reader.read_u16()
    property_set = read_property_set(reader)
    if not reader.expect_bytes(_DEADCODE):
        raise ValueError('Not a valid DEADCODE.')
    return property_set, version


def write_property_set(writer: BinaryWriter, property_set: TPropertySet):
    writer.write_bytes(_SUB_CLASS_IDENTIFIER)
    writer.write_entry(property_set.name)
    writer.write_bytes(_TYPE_TO_VERSION_FILLER)
    property_set.write(writer)


def write_wrapped_property_set(writer: BinaryWriter, property_set: TPropertySet, version: int):
    writer.write_u16(version)
    write_property_set(writer, property_set)
    writer.write_bytes(_DEADCODE)
