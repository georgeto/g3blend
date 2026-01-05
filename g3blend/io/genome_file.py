from typing import Type

from .binary import BinaryReader, BinaryWriter, TBinarySerializable
from .property_sets.property_set import PropertySet
from .property_sets.util import read_property_set, write_property_set

_GENOME_MAGIC = b'\x47\x45\x4e\x4f\x4d\x46\x4c\x45'
_DEADBEEF = b'\xef\xbe\xad\xde'
_VERSION = 1


def _read_content(reader: BinaryReader, content_type: Type[TBinarySerializable]) -> TBinarySerializable:
    if issubclass(content_type, PropertySet):
        property_set = read_property_set(reader)
        if not isinstance(property_set, content_type):
            raise ValueError(f'Expected property set {content_type}, got {type(property_set)}.')
        return property_set
    else:
        return reader.read(content_type)


def read(
    reader: BinaryReader, content_type: Type[TBinarySerializable], allow_fallback: bool = False
) -> TBinarySerializable:
    if not reader.expect_bytes(_GENOME_MAGIC):
        if allow_fallback:
            return _read_content(reader, content_type)
        else:
            raise ValueError('Not a valid Genome file.')

    if (version := reader.read_u16()) != _VERSION:
        raise ValueError(f'Unsupported Genome file version: {version}')

    deadbeef_offset = reader.read_u32()

    with reader.at_position(deadbeef_offset):
        if not reader.expect_bytes(_DEADBEEF):
            raise ValueError('Not a valid Genome file tail.')

        reader.read_stringtable()

    return _read_content(reader, content_type)


def write(writer: BinaryWriter, content: TBinarySerializable) -> None:
    writer.write_bytes(_GENOME_MAGIC)
    writer.write_u16(_VERSION)

    size_fixup_pos = writer.position()
    writer.write_u32(0)

    if isinstance(content, PropertySet):
        write_property_set(writer, content)
    else:
        writer.write(content)

    deadbeef_offset = writer.position()
    writer.write_bytes(_DEADBEEF)
    with writer.at_position(size_fixup_pos):
        writer.write_u32(deadbeef_offset)

    writer.write_stringtable()
