from dataclasses import dataclass

from .decorator import property_set
from .shader_base import eCShaderBase
from ..binary import BinaryReader, BinaryWriter
from ..types import eCColorSrcProxy


@property_set
@dataclass
class eCShaderDefault(eCShaderBase):
    color_src_diffuse: eCColorSrcProxy
    color_src_opacity: eCColorSrcProxy
    color_src_self_illumination: eCColorSrcProxy
    color_src_specular: eCColorSrcProxy
    color_src_specular_power: eCColorSrcProxy
    color_src_normal: eCColorSrcProxy
    color_src_distortion: eCColorSrcProxy

    def read_post_version(self, reader: BinaryReader) -> None:
        self.color_src_diffuse = reader.read(eCColorSrcProxy)
        self.color_src_opacity = reader.read(eCColorSrcProxy)
        self.color_src_self_illumination = reader.read(eCColorSrcProxy)
        self.color_src_specular = reader.read(eCColorSrcProxy)
        self.color_src_specular_power = reader.read(eCColorSrcProxy)
        self.color_src_normal = reader.read(eCColorSrcProxy)

        if self.version > 1:
            self.color_src_distortion = reader.read(eCColorSrcProxy)

        super().read_post_version(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        writer.write(self.color_src_diffuse)
        writer.write(self.color_src_opacity)
        writer.write(self.color_src_self_illumination)
        writer.write(self.color_src_specular)
        writer.write(self.color_src_specular_power)
        writer.write(self.color_src_normal)

        if self.version > 1:
            writer.write(self.color_src_distortion)

        super().write_post_version(writer)


@property_set
@dataclass
class eCShaderLeaf(eCShaderBase):
    color_src_diffuse: eCColorSrcProxy
    color_src_specular: eCColorSrcProxy
    color_src_specular_power: eCColorSrcProxy
    color_src_normal: eCColorSrcProxy

    def read_post_version(self, reader: BinaryReader) -> None:
        self.color_src_diffuse = reader.read(eCColorSrcProxy)
        self.color_src_specular = reader.read(eCColorSrcProxy)
        self.color_src_specular_power = reader.read(eCColorSrcProxy)
        self.color_src_normal = reader.read(eCColorSrcProxy)

        super().read_post_version(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        writer.write(self.color_src_diffuse)
        writer.write(self.color_src_specular)
        writer.write(self.color_src_specular_power)
        writer.write(self.color_src_normal)

        super().write_post_version(writer)


@property_set
@dataclass
class eCShaderParticle(eCShaderBase):
    color_src_diffuse: eCColorSrcProxy
    color_src_distortion: eCColorSrcProxy

    def read_post_version(self, reader: BinaryReader) -> None:
        self.color_src_diffuse = reader.read(eCColorSrcProxy)

        if self.version > 1:
            self.color_src_distortion = reader.read(eCColorSrcProxy)

        super().read_post_version(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        writer.write(self.color_src_diffuse)

        if self.version > 1:
            writer.write(self.color_src_distortion)

        super().write_post_version(writer)


@property_set
@dataclass
class eCShaderSkin(eCShaderBase):
    color_src_diffuse: eCColorSrcProxy
    color_src_opacity: eCColorSrcProxy
    color_src_self_illumination: eCColorSrcProxy
    color_src_specular: eCColorSrcProxy
    color_src_specular_power: eCColorSrcProxy
    color_src_normal: eCColorSrcProxy
    color_src_sub_surface: eCColorSrcProxy

    def read_post_version(self, reader: BinaryReader) -> None:
        self.color_src_diffuse = reader.read(eCColorSrcProxy)
        self.color_src_opacity = reader.read(eCColorSrcProxy)
        self.color_src_self_illumination = reader.read(eCColorSrcProxy)
        self.color_src_specular = reader.read(eCColorSrcProxy)
        self.color_src_specular_power = reader.read(eCColorSrcProxy)
        self.color_src_normal = reader.read(eCColorSrcProxy)
        self.color_src_sub_surface = reader.read(eCColorSrcProxy)

        super().read_post_version(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        writer.write(self.color_src_diffuse)
        writer.write(self.color_src_opacity)
        writer.write(self.color_src_self_illumination)
        writer.write(self.color_src_specular)
        writer.write(self.color_src_specular_power)
        writer.write(self.color_src_normal)
        writer.write(self.color_src_sub_surface)

        super().write_post_version(writer)


@property_set
@dataclass
class eCShaderWater(eCShaderBase):
    color_src_diffuse: eCColorSrcProxy
    color_src_static_bump: eCColorSrcProxy
    color_src_flowing_bump: eCColorSrcProxy
    color_src_specular: eCColorSrcProxy
    color_src_specular_power: eCColorSrcProxy
    color_src_reflection: eCColorSrcProxy
    color_src_distortion: eCColorSrcProxy

    def read_post_version(self, reader: BinaryReader) -> None:
        self.color_src_diffuse = reader.read(eCColorSrcProxy)
        self.color_src_static_bump = reader.read(eCColorSrcProxy)
        self.color_src_flowing_bump = reader.read(eCColorSrcProxy)
        self.color_src_specular = reader.read(eCColorSrcProxy)
        self.color_src_specular_power = reader.read(eCColorSrcProxy)
        self.color_src_reflection = reader.read(eCColorSrcProxy)

        if self.version > 1:
            self.color_src_distortion = reader.read(eCColorSrcProxy)

        super().read_post_version(reader)

    def write_post_version(self, writer: BinaryWriter) -> None:
        writer.write(self.color_src_diffuse)
        writer.write(self.color_src_static_bump)
        writer.write(self.color_src_flowing_bump)
        writer.write(self.color_src_specular)
        writer.write(self.color_src_specular_power)
        writer.write(self.color_src_reflection)

        if self.version > 1:
            writer.write(self.color_src_distortion)

        super().write_post_version(writer)
