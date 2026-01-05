from dataclasses import dataclass

from .decorator import property_set
from .shader_element_base import eCShaderEllementBase
from ..binary import BinaryReader, BinaryWriter
from ..types import eCColorSrcProxy, eCTexCoordSrcProxy


@dataclass
class eCColorSrcBase(eCShaderEllementBase):
    def read_post_version(self, reader: BinaryReader) -> None:
        if reader.read_u16() != 1:
            raise ValueError('Unsupported eCColorSrcBase version.')

        super().read_post_version(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        writer.write_u16(1)

        super().write_post_version(writer)


@property_set
@dataclass
class eCColorSrcBlend(eCColorSrcBase):
    color_src1: eCColorSrcProxy
    color_src2: eCColorSrcProxy
    blend_src: eCColorSrcProxy

    def read_post_version(self, reader: BinaryReader) -> None:
        self.color_src1 = reader.read(eCColorSrcProxy)
        self.color_src2 = reader.read(eCColorSrcProxy)
        self.blend_src = reader.read(eCColorSrcProxy)

        super().read_post_version(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        writer.write(self.color_src1)
        writer.write(self.color_src2)
        writer.write(self.blend_src)
        super().write_post_version(writer)


@property_set
@dataclass
class eCColorSrcCombiner(eCColorSrcBase):
    color_src1: eCColorSrcProxy
    color_src2: eCColorSrcProxy

    def read_post_version(self, reader: BinaryReader) -> None:
        self.color_src1 = reader.read(eCColorSrcProxy)
        self.color_src2 = reader.read(eCColorSrcProxy)

        super().read_post_version(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        writer.write(self.color_src1)
        writer.write(self.color_src2)
        super().write_post_version(writer)


@property_set
@dataclass
class eCColorSrcConstant(eCColorSrcBase):
    def read_post_version(self, reader: BinaryReader) -> None:
        super().read_post_version(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        super().write_post_version(writer)


@property_set
@dataclass
class eCColorSrcCubeSampler(eCColorSrcBase):
    def read_post_version(self, reader: BinaryReader) -> None:
        super().read_post_version(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        super().write_post_version(writer)


@property_set
@dataclass
class eCColorSrcSampler(eCColorSrcBase):
    tex_coord_src: eCTexCoordSrcProxy
    sampler_type: int  # eEColorSrcSamplerType

    def read_post_version(self, reader: BinaryReader) -> None:
        self.tex_coord_src = reader.read(eCTexCoordSrcProxy)
        self.sampler_type = reader.read_u32()

        super().read_post_version(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        writer.write(self.tex_coord_src)
        writer.write_u32(self.sampler_type)
        super().write_post_version(writer)


@property_set
@dataclass
class eCColorSrcVertexColor(eCColorSrcBase):
    def read_post_version(self, reader: BinaryReader) -> None:
        super().read_post_version(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        super().write_post_version(writer)
