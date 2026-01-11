from collections.abc import Callable
from dataclasses import dataclass, field
from enum import IntEnum
from typing import ClassVar, Generic, Optional, TypeVar

from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from ..property_types import bCBox, bCVector, bCVector2
from ..types.vector4 import bCVector4


@dataclass(slots=True, frozen=True)
class eSFVF:
    vertex_stream_type: int
    vertex_type_struct: int
    fvf: int


class eEVertexTypeStruct(IntEnum):
    bCVector2 = 0  # noqa: N815 Gothic 3 class name
    bCVector3 = 1  # noqa: N815 Gothic 3 class name
    bCVector4 = 2  # noqa: N815 Gothic 3 class name
    GEU16 = 3
    GEU32 = 4
    GEFloat = 5


class eEVertexStreamArrayType(IntEnum):
    # Faces / Triangles
    Face = 0

    # Vertex format includes the position of an untransformed vertex. (D3DFVF_XYZ) (bCVector3)
    VertexPosition = 1

    # Vertex format includes the position of a transformed vertex. (D3DFVF_XYZRHW) (bCVector4)
    VertexPositionTransformed = 2

    # Vertex format includes a vertex normal vector. (D3DFVF_NORMAL) (bCVector3)
    Normal = 3

    # Vertex format includes a diffuse color component. (D3DFVF_DIFFUSE) (DWORD in ARGB order)
    # <p>
    # Bi-Tangent Heading (G3MC Manual) - 00FF0000
    # <p>
    # Texture Fading (G3MC)
    Diffuse = 4

    # Vertex format includes a specular color component. (D3DFVF_SPECULAR) (DWORD in ARGB
    # order)
    # <p>
    # ? (G3MC Manual) - FF000000
    # <p>
    # "eCTexCoordSrcBumpOffset::GetImplementation - No color source for height set!"
    # <p>
    # "eCTexCoordSrcBumpOffset::GetImplementation - Invalid color source component. Color
    # component forced to alpha!"
    Specular = 5

    # Vertex format specified in point size. This size is expressed in camera space units for
    # vertices that are not transformed and lit, and in device-space units for transformed and
    # lit vertices. (D3DFVF_PSIZE) (GEFloat)
    PointSize = 6

    # Vertex format contains position data, and a corresponding number of weighting (beta)
    # values to use for multimatrix vertex blending operations. (D3DFVF_XYZB1 through
    # D3DFVF_XYZB5) (GEFloat)
    XYZB1 = 7
    XYZB2 = 8
    XYZB3 = 9
    XYZB4 = 10
    XYZB5 = 11
    TextureCoordinate = 12
    Unk_13 = 13
    Unk_14 = 14

    # Water Reflections (G3MC)
    Unk_15 = 15
    Unk_16 = 16
    Unk_17 = 17
    Unk_18 = 18
    Unk_19 = 19
    Unk_20 = 20
    Unk_21 = 21
    Unk_22 = 22
    Unk_23 = 23
    Unk_24 = 24
    Unk_25 = 25
    Unk_26 = 26
    Unk_27 = 27
    Unk_28 = 28
    Unk_29 = 29
    Unk_30 = 30
    Unk_31 = 31
    Unk_32 = 32
    Unk_33 = 33
    Unk_34 = 34
    Unk_35 = 35
    Unk_36 = 36
    Unk_37 = 37
    Unk_38 = 38
    Unk_39 = 39
    Unk_40 = 40
    Unk_41 = 41
    Unk_42 = 42
    Unk_43 = 43
    Unk_44 = 44
    Unk_45 = 45
    Unk_46 = 46
    Unk_47 = 47
    Unk_48 = 48
    Unk_49 = 49
    Unk_50 = 50
    Unk_51 = 51
    Unk_52 = 52
    Unk_53 = 53
    Unk_54 = 54
    Unk_55 = 55
    Unk_56 = 56
    Unk_57 = 57
    Unk_58 = 58
    Unk_59 = 59
    Unk_60 = 60
    Unk_61 = 61
    Unk_62 = 62
    Unk_63 = 63

    # Tangent Vector (G3MC Manual)
    TangentVector = 64
    Unk_65 = 65
    Unk_66 = 66
    Unk_67 = 67
    Unk_68 = 68
    Unk_69 = 69
    Unk_70 = 70
    Unk_71 = 71
    Unk_72 = 72
    UVLightmapGroups = 73


_vertex_stream_to_struct_map = {
    eEVertexStreamArrayType.Face: eSFVF(eEVertexStreamArrayType.Face, eEVertexTypeStruct.GEU32, 0x0),
    eEVertexStreamArrayType.VertexPosition: eSFVF(
        eEVertexStreamArrayType.VertexPosition, eEVertexTypeStruct.bCVector3, 0x2
    ),
    eEVertexStreamArrayType.VertexPositionTransformed: eSFVF(
        eEVertexStreamArrayType.VertexPositionTransformed, eEVertexTypeStruct.bCVector4, 0x4
    ),
    eEVertexStreamArrayType.Normal: eSFVF(eEVertexStreamArrayType.Normal, eEVertexTypeStruct.bCVector3, 0x10),
    eEVertexStreamArrayType.Diffuse: eSFVF(eEVertexStreamArrayType.Diffuse, eEVertexTypeStruct.GEU32, 0x40),
    eEVertexStreamArrayType.Specular: eSFVF(eEVertexStreamArrayType.Specular, eEVertexTypeStruct.GEU32, 0x80),
    eEVertexStreamArrayType.PointSize: eSFVF(eEVertexStreamArrayType.PointSize, eEVertexTypeStruct.GEFloat, 0x20),
    eEVertexStreamArrayType.XYZB1: eSFVF(eEVertexStreamArrayType.XYZB1, eEVertexTypeStruct.GEFloat, 0x6),
    eEVertexStreamArrayType.XYZB2: eSFVF(eEVertexStreamArrayType.XYZB2, eEVertexTypeStruct.GEFloat, 0x8),
    eEVertexStreamArrayType.XYZB3: eSFVF(eEVertexStreamArrayType.XYZB3, eEVertexTypeStruct.GEFloat, 0x0A),
    eEVertexStreamArrayType.XYZB4: eSFVF(eEVertexStreamArrayType.XYZB4, eEVertexTypeStruct.GEFloat, 0x0C),
    eEVertexStreamArrayType.XYZB5: eSFVF(eEVertexStreamArrayType.XYZB5, eEVertexTypeStruct.GEFloat, 0x0E),
    eEVertexStreamArrayType.TextureCoordinate: eSFVF(
        eEVertexStreamArrayType.TextureCoordinate, eEVertexTypeStruct.bCVector2, 0
    ),
    eEVertexStreamArrayType.Unk_13: eSFVF(eEVertexStreamArrayType.Unk_13, eEVertexTypeStruct.bCVector3, 0x10000),
    eEVertexStreamArrayType.Unk_14: eSFVF(eEVertexStreamArrayType.Unk_14, eEVertexTypeStruct.bCVector4, 0x20000),
    eEVertexStreamArrayType.Unk_15: eSFVF(eEVertexStreamArrayType.Unk_15, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_16: eSFVF(eEVertexStreamArrayType.Unk_16, eEVertexTypeStruct.bCVector3, 0x40000),
    eEVertexStreamArrayType.Unk_17: eSFVF(eEVertexStreamArrayType.Unk_17, eEVertexTypeStruct.bCVector4, 0x80000),
    eEVertexStreamArrayType.Unk_18: eSFVF(eEVertexStreamArrayType.Unk_18, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_19: eSFVF(eEVertexStreamArrayType.Unk_19, eEVertexTypeStruct.bCVector3, 0x100000),
    eEVertexStreamArrayType.Unk_20: eSFVF(eEVertexStreamArrayType.Unk_20, eEVertexTypeStruct.bCVector4, 0x200000),
    eEVertexStreamArrayType.Unk_21: eSFVF(eEVertexStreamArrayType.Unk_21, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_22: eSFVF(eEVertexStreamArrayType.Unk_22, eEVertexTypeStruct.bCVector3, 0x400000),
    eEVertexStreamArrayType.Unk_23: eSFVF(eEVertexStreamArrayType.Unk_23, eEVertexTypeStruct.bCVector4, 0x800000),
    eEVertexStreamArrayType.Unk_24: eSFVF(eEVertexStreamArrayType.Unk_24, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_25: eSFVF(eEVertexStreamArrayType.Unk_25, eEVertexTypeStruct.bCVector3, 0x1000000),
    eEVertexStreamArrayType.Unk_26: eSFVF(eEVertexStreamArrayType.Unk_26, eEVertexTypeStruct.bCVector4, 0x2000000),
    eEVertexStreamArrayType.Unk_27: eSFVF(eEVertexStreamArrayType.Unk_27, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_28: eSFVF(eEVertexStreamArrayType.Unk_28, eEVertexTypeStruct.bCVector3, 0x4000000),
    eEVertexStreamArrayType.Unk_29: eSFVF(eEVertexStreamArrayType.Unk_29, eEVertexTypeStruct.bCVector4, 0x8000000),
    eEVertexStreamArrayType.Unk_30: eSFVF(eEVertexStreamArrayType.Unk_30, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_31: eSFVF(eEVertexStreamArrayType.Unk_31, eEVertexTypeStruct.bCVector3, 0x10000000),
    eEVertexStreamArrayType.Unk_32: eSFVF(eEVertexStreamArrayType.Unk_32, eEVertexTypeStruct.bCVector4, 0x20000000),
    eEVertexStreamArrayType.Unk_33: eSFVF(eEVertexStreamArrayType.Unk_33, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_34: eSFVF(eEVertexStreamArrayType.Unk_34, eEVertexTypeStruct.bCVector3, 0x40000000),
    eEVertexStreamArrayType.Unk_35: eSFVF(eEVertexStreamArrayType.Unk_35, eEVertexTypeStruct.bCVector4, 0x80000000),
    eEVertexStreamArrayType.Unk_36: eSFVF(eEVertexStreamArrayType.Unk_36, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_37: eSFVF(eEVertexStreamArrayType.Unk_37, eEVertexTypeStruct.bCVector3, 0),
    eEVertexStreamArrayType.Unk_38: eSFVF(eEVertexStreamArrayType.Unk_38, eEVertexTypeStruct.bCVector4, 0),
    eEVertexStreamArrayType.Unk_39: eSFVF(eEVertexStreamArrayType.Unk_39, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_40: eSFVF(eEVertexStreamArrayType.Unk_40, eEVertexTypeStruct.bCVector3, 0),
    eEVertexStreamArrayType.Unk_41: eSFVF(eEVertexStreamArrayType.Unk_41, eEVertexTypeStruct.bCVector4, 0),
    eEVertexStreamArrayType.Unk_42: eSFVF(eEVertexStreamArrayType.Unk_42, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_43: eSFVF(eEVertexStreamArrayType.Unk_43, eEVertexTypeStruct.bCVector3, 0),
    eEVertexStreamArrayType.Unk_44: eSFVF(eEVertexStreamArrayType.Unk_44, eEVertexTypeStruct.bCVector4, 0),
    eEVertexStreamArrayType.Unk_45: eSFVF(eEVertexStreamArrayType.Unk_45, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_46: eSFVF(eEVertexStreamArrayType.Unk_46, eEVertexTypeStruct.bCVector3, 0),
    eEVertexStreamArrayType.Unk_47: eSFVF(eEVertexStreamArrayType.Unk_47, eEVertexTypeStruct.bCVector4, 0),
    eEVertexStreamArrayType.Unk_48: eSFVF(eEVertexStreamArrayType.Unk_48, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_49: eSFVF(eEVertexStreamArrayType.Unk_49, eEVertexTypeStruct.bCVector3, 0),
    eEVertexStreamArrayType.Unk_50: eSFVF(eEVertexStreamArrayType.Unk_50, eEVertexTypeStruct.bCVector4, 0),
    eEVertexStreamArrayType.Unk_51: eSFVF(eEVertexStreamArrayType.Unk_51, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_52: eSFVF(eEVertexStreamArrayType.Unk_52, eEVertexTypeStruct.bCVector3, 0),
    eEVertexStreamArrayType.Unk_53: eSFVF(eEVertexStreamArrayType.Unk_53, eEVertexTypeStruct.bCVector4, 0),
    eEVertexStreamArrayType.Unk_54: eSFVF(eEVertexStreamArrayType.Unk_54, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_55: eSFVF(eEVertexStreamArrayType.Unk_55, eEVertexTypeStruct.bCVector3, 0),
    eEVertexStreamArrayType.Unk_56: eSFVF(eEVertexStreamArrayType.Unk_56, eEVertexTypeStruct.bCVector4, 0),
    eEVertexStreamArrayType.Unk_57: eSFVF(eEVertexStreamArrayType.Unk_57, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_58: eSFVF(eEVertexStreamArrayType.Unk_58, eEVertexTypeStruct.bCVector3, 0),
    eEVertexStreamArrayType.Unk_59: eSFVF(eEVertexStreamArrayType.Unk_59, eEVertexTypeStruct.bCVector4, 0),
    eEVertexStreamArrayType.Unk_60: eSFVF(eEVertexStreamArrayType.Unk_60, eEVertexTypeStruct.bCVector4, 0),
    eEVertexStreamArrayType.Unk_61: eSFVF(eEVertexStreamArrayType.Unk_61, eEVertexTypeStruct.bCVector4, 0),
    eEVertexStreamArrayType.Unk_62: eSFVF(eEVertexStreamArrayType.Unk_62, eEVertexTypeStruct.bCVector4, 0),
    eEVertexStreamArrayType.Unk_63: eSFVF(eEVertexStreamArrayType.Unk_63, eEVertexTypeStruct.bCVector4, 0),
    eEVertexStreamArrayType.TangentVector: eSFVF(
        eEVertexStreamArrayType.TangentVector, eEVertexTypeStruct.bCVector3, 0
    ),
    eEVertexStreamArrayType.Unk_65: eSFVF(eEVertexStreamArrayType.Unk_65, eEVertexTypeStruct.bCVector3, 0),
    eEVertexStreamArrayType.Unk_66: eSFVF(eEVertexStreamArrayType.Unk_66, eEVertexTypeStruct.bCVector3, 0),
    eEVertexStreamArrayType.Unk_67: eSFVF(eEVertexStreamArrayType.Unk_67, eEVertexTypeStruct.bCVector3, 0),
    eEVertexStreamArrayType.Unk_68: eSFVF(eEVertexStreamArrayType.Unk_68, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_69: eSFVF(eEVertexStreamArrayType.Unk_69, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_70: eSFVF(eEVertexStreamArrayType.Unk_70, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_71: eSFVF(eEVertexStreamArrayType.Unk_71, eEVertexTypeStruct.bCVector2, 0),
    eEVertexStreamArrayType.Unk_72: eSFVF(eEVertexStreamArrayType.Unk_72, eEVertexTypeStruct.bCVector3, 0),
    eEVertexStreamArrayType.UVLightmapGroups: eSFVF(
        eEVertexStreamArrayType.UVLightmapGroups, eEVertexTypeStruct.bCVector2, 0
    ),
}

TVetexArrayType = TypeVar('TVetexArrayType')


@dataclass(slots=True)
class eCVertexStructArrayBase(BinarySerializable, Generic[TVetexArrayType]):
    read_element: ClassVar[Callable[[BinaryReader], TVetexArrayType]]
    write_element: ClassVar[Callable[[BinaryWriter, TVetexArrayType], None]]

    vertex_stream_type: eEVertexStreamArrayType
    elements: list[TVetexArrayType] = field(default_factory=list)

    def read(self, reader: BinaryReader):
        reader.skip(2)
        self.elements = reader.read_prefixed_list(read=self.__class__.read_element)

    def write(self, writer: BinaryWriter):
        writer.write_u16(1)
        writer.write_prefixed_list(self.elements, write=self.__class__.write_element)


@dataclass(slots=True)
class eCVertexStructArray_GEFloat(eCVertexStructArrayBase[float]):
    struct_type = eEVertexTypeStruct.GEFloat
    read_element = BinaryReader.read_float
    write_element = BinaryWriter.write_float


@dataclass(slots=True)
class eCVertexStructArray_GEU16(eCVertexStructArrayBase[int]):
    struct_type = eEVertexTypeStruct.GEU16
    read_element = BinaryReader.read_u16
    write_element = BinaryWriter.write_u16


@dataclass(slots=True)
class eCVertexStructArray_GEU32(eCVertexStructArrayBase[int]):
    struct_type = eEVertexTypeStruct.GEU32
    read_element = BinaryReader.read_u32
    write_element = BinaryWriter.write_u32


@dataclass(slots=True)
class eCVertexStructArray_bCVector2(eCVertexStructArrayBase[bCVector2]):
    struct_type = eEVertexTypeStruct.bCVector2
    read_element = BinaryReader.read_vec2
    write_element = BinaryWriter.write_vec2


@dataclass(slots=True)
class eCVertexStructArray_bCVector3(eCVertexStructArrayBase[bCVector]):
    struct_type = eEVertexTypeStruct.bCVector3
    read_element = BinaryReader.read_vec3
    write_element = BinaryWriter.write_vec3


@dataclass(slots=True)
class eCVertexStructArray_bCVector4(eCVertexStructArrayBase[bCVector4]):
    struct_type = eEVertexTypeStruct.bCVector4
    read_element = BinaryReader.read_vec4
    write_element = BinaryWriter.write_vec4


def create_vertex_struct_array(vertex_stream_type: eEVertexStreamArrayType) -> eCVertexStructArrayBase:
    match _vertex_stream_to_struct_map[vertex_stream_type].vertex_type_struct:
        case eEVertexTypeStruct.bCVector2:
            return eCVertexStructArray_bCVector2(vertex_stream_type)
        case eEVertexTypeStruct.bCVector3:
            return eCVertexStructArray_bCVector3(vertex_stream_type)
        case eEVertexTypeStruct.bCVector4:
            return eCVertexStructArray_bCVector4(vertex_stream_type)
        case eEVertexTypeStruct.GEU16:
            return eCVertexStructArray_GEU16(vertex_stream_type)
        case eEVertexTypeStruct.GEU32:
            return eCVertexStructArray_GEU32(vertex_stream_type)
        case eEVertexTypeStruct.GEFloat:
            return eCVertexStructArray_GEFloat(vertex_stream_type)
        case _:
            raise ValueError('Unsupported vertex stream array.')


@dataclass(slots=True)
class eCMeshElement(BinarySerializable):
    version: int
    fvf: int
    bounding_box: bCBox
    size: int
    material_name: str
    stream_arrays: list[eCVertexStructArrayBase]

    def read(self, reader: BinaryReader):
        self.version = reader.read_u16()
        self.fvf = reader.read_u32()
        self.bounding_box = reader.read(bCBox)
        self.size = reader.read_u32()
        self.material_name = reader.read_entry()

        stream_array_count = reader.read_u32()
        self.stream_arrays = []
        for _ in range(stream_array_count):
            stream_array_type = eEVertexStreamArrayType(reader.read_u32())
            vertex_array = create_vertex_struct_array(stream_array_type)
            vertex_array.read(reader)
            self.stream_arrays.append(vertex_array)

        if self.version >= 3:
            reader.skip(1)  # true
            reader.skip(reader.read_u32() * 4)
            reader.skip(1)  # true
            reader.skip(reader.read_u32() * 4)

        if self.version >= 2:
            reader.skip(1)  # true
            group_count = reader.read_u32()
            for _ in range(group_count):
                reader.skip(1)  # true
                reader.skip(reader.read_u32() * 4)
                reader.skip(1)  # true
                reader.skip(reader.read_u32() * 4)
                reader.skip(12 + 64 + 8)

        if self.version < 5:
            # clear m_arrLightmapUVGroups and delete stream array 0x48
            pass

        if self.version >= 4:
            reader.skip(reader.read_u32() * 24)
            reader.skip(1)
            reader.skip(reader.read_u32() * 4)

    def write(self, writer: BinaryWriter):
        raise NotImplementedError

    def has_stream_array(self, stream_type: eEVertexStreamArrayType) -> bool:
        return any(a.vertex_stream_type == stream_type for a in self.stream_arrays)

    def get_stream_array_by_type(self, stream_type: eEVertexStreamArrayType) -> Optional[list[TVetexArrayType]]:
        return next((a.elements for a in self.stream_arrays if a.vertex_stream_type == stream_type), None)
