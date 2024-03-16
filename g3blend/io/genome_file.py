from typing import Type

from .binary import BinaryReader, BinaryWriter, TBinarySerializable

_GENOME_MAGIC = b'\x47\x45\x4E\x4F\x4D\x46\x4C\x45'
_DEADBEEF = b'\xEF\xBE\xAD\xDE'
_VERSION = 1


def read(reader: BinaryReader, content_type: Type[TBinarySerializable]) -> TBinarySerializable:
    if not reader.expect_bytes(_GENOME_MAGIC):
        raise ValueError('Not a valid Genome file.')

    if (version := reader.read_u16()) != _VERSION:
        raise ValueError(f'Unsupported Genome file version: {version}')

    deadbeef_offset = reader.read_u32()

    with reader.at_position(deadbeef_offset):
        if not reader.expect_bytes(_DEADBEEF):
            raise ValueError('Not a valid Genome file tail.')

        reader.read_stringtable()

    content = content_type()
    content.read(reader)
    return content


def write(writer: BinaryWriter, content: TBinarySerializable) -> None:
    writer.write_bytes(_GENOME_MAGIC)
    writer.write_u16(_VERSION)

    size_fixup_pos = writer.position()
    writer.write_u32(0)

    content.write(writer)

    deadbeef_offset = writer.position()
    writer.write_bytes(_DEADBEEF)
    with writer.at_position(size_fixup_pos):
        writer.write_u32(deadbeef_offset)

    writer.write_stringtable()
