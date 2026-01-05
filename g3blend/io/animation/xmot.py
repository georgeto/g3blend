from dataclasses import dataclass

from ..animation.chunks import ChunkContainer
from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from ..property_types import bCDateTime


@dataclass(slots=True)
class eSFrameEffect(BinarySerializable):
    key_frame: int
    effect_name: str

    def read(self, reader: BinaryReader) -> None:
        self.key_frame = reader.read_u16()
        self.effect_name = reader.read_entry()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u16(self.key_frame)
        writer.write_entry(self.effect_name)


class eCWrapper_emfx2Motion(BinarySerializable, ChunkContainer):
    _LMA_MAGIC = b'LMA '
    _HIGH_VERSION = 1
    _LOW_VERSION = 1

    def read(self, reader: BinaryReader) -> None:
        offset_end = reader.read_u32() + reader.position()
        if not reader.expect_bytes(self._LMA_MAGIC):
            raise ValueError('Invalid eCWrapper_emfx2Motion.')

        # high version (2 in case of v2.34)
        high_version = reader.read_u8()
        # low version (34 in case of v2.34)
        low_version = reader.read_u8()

        if high_version != self._HIGH_VERSION or low_version != self._LOW_VERSION:
            raise ValueError('Invalid eCWrapper_emfx2Motion.')

        # is this an actor? (if false, it's a motion)
        if reader.read_bool():
            raise ValueError('Invalid eCWrapper_emfx2Motion.')

        self.read_chunks(reader, offset_end)

    def write(self, writer: BinaryWriter) -> None:
        size_offset = writer.position()
        writer.write_u32(0)
        writer.write_bytes(self._LMA_MAGIC)
        writer.write_u8(self._HIGH_VERSION)
        writer.write_u8(self._LOW_VERSION)
        writer.write_bool(False)
        self.write_chunks(writer)
        with writer.at_position(size_offset) as pos:
            writer.write_u32(pos - size_offset - 4)


class ResourceAnimationMotion(BinarySerializable):  # eCResourceAnimationMotion_PS
    resource_size: int
    resource_priority: float
    native_file_time: bCDateTime
    native_file_size: int
    unk_file_time: bCDateTime  # Maybe actor?
    frame_effects: list[eSFrameEffect]
    motion: eCWrapper_emfx2Motion

    def read(self, reader: BinaryReader) -> None:
        version = reader.read_u16()
        self.resource_size = reader.read_u32()
        self.resource_priority = reader.read_float()
        self.native_file_time = reader.read(bCDateTime)
        self.native_file_size = reader.read_u32()
        self.unk_file_time = reader.read(bCDateTime) if version >= 3 else self.native_file_time
        self.frame_effects = reader.read_list(eSFrameEffect, num=reader.read_u16()) if version >= 2 else []
        self.motion = reader.read(eCWrapper_emfx2Motion)

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u16(5)
        writer.write_u32(self.resource_size)
        writer.write_float(self.resource_priority)
        writer.write(self.native_file_time)
        writer.write_u32(self.native_file_size)
        writer.write(self.unk_file_time)
        writer.write_u16(len(self.frame_effects))
        writer.write_iter(self.frame_effects)
        writer.write(self.motion)
