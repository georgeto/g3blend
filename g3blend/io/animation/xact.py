from .chunks import ChunkContainer
from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from ..types.math import bCBox, bCVector
from ..types.misc import bCDateTime


class MaterialReference(BinarySerializable):
    # LoD level inside a emfx2Actor (not to be confused with LoD level in
    # eCResourceAnimationActor_PS), seems to be always zero
    lod_index: int
    mat_index: int
    name: str

    def read(self, reader: BinaryReader) -> None:
        # MaterialID = mat_index | lod_index
        self.lod_index = reader.read_u16()
        self.mat_index = reader.read_u16()
        try:
            self.name = reader.read_entry()
        except ValueError | IndexError:
            # Workaround for broken Rimy3D meshes (they don't have a stringtable, but still
            # refer to stringtable entries here)
            self.name = ""

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u16(self.lod_index)
        writer.write_u16(self.mat_index)
        writer.write_entry(self.name)


class eCWrapper_emfx2Actor(BinarySerializable, ChunkContainer):
    _GENA_MAGIC = b'gena'
    _FXA_MAGIC = b'FXA '

    high_version: int
    low_version: int
    # MaterialsLoDMappings: MaterialID -> MaterialReference
    materials: list[MaterialReference]
    # eCWrapper_emfx2Actor::CalculateAmbientOcclusion | ColorVertexAttribute
    ambient_occlusion: list[list[int]]
    tangent_vertices: list[list[bCVector]]  # TangentVertexAttribute

    def read(self, reader: BinaryReader) -> None:
        if not reader.expect_bytes(self._GENA_MAGIC):
            raise ValueError("Invalid eCWrapper_emfx2Actor.")

        version = reader.read_u16()
        if version != 4:
            raise ValueError("Version != 4 is not supported.")

        offset_end = reader.read_u32() + reader.position()
        if not reader.expect_bytes(self._FXA_MAGIC):
            raise ValueError("Invalid eCWrapper_emfx2Actor.")

        self.high_version = reader.read_u8()
        self.low_version = reader.read_u8()

        if self.high_version != 1 or self.low_version != 1:
            raise ValueError("Invalid eCWrapper_emfx2Actor.")

        self.read_chunks(reader, offset_end)
        self.materials = reader.read_list(MaterialReference)

        # Per LoD
        self.ambient_occlusion = reader.read_prefixed_list(
            read=lambda r: r.read_prefixed_list(read=BinaryReader.read_u32))
        self.tangent_vertices = [reader.read_list(bCVector, num=len(lod_vertices)) for lod_vertices in
                                 self.ambient_occlusion]

    def write(self, writer: BinaryWriter) -> None:
        writer.write_bytes(self._GENA_MAGIC)
        writer.write_u16(4)
        size_offset = writer.position()
        writer.write_u32(0)
        writer.write_bytes(self._FXA_MAGIC)
        writer.write_u8(self.high_version)
        writer.write_u8(self.low_version)
        self.write_chunks(writer)
        with writer.at_position(size_offset) as pos:
            writer.write_u32(pos - size_offset - 4)
        writer.write_list(self.materials)
        writer.write_prefixed_list(self.ambient_occlusion,
                                   lambda w, v: w.write_prefixed_list(v, BinaryWriter.write_u32))
        writer.write_iter(self.tangent_vertices, write=BinaryWriter.write_iter)


class eSLookAtConstraintData(BinarySerializable):
    node_name: str
    interpolation_speed: float
    min_constraints: bCVector
    max_constraints: bCVector

    def read(self, reader: BinaryReader) -> None:
        self.node_name = reader.read_entry()
        self.interpolation_speed = reader.read_float()
        self.min_constraints = reader.read_vec3()
        self.max_constraints = reader.read_vec3()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_entry(self.node_name)
        writer.write_float(self.interpolation_speed)
        writer.write_vec3(self.min_constraints)
        writer.write_vec3(self.max_constraints)


class ResourceAnimationActor(BinarySerializable):  # eCResourceAnimationActor_PS
    resource_size: int
    resource_priority: float
    native_file_time: bCDateTime
    native_file_size: int
    boundary: bCBox

    look_at_constraints: list[eSLookAtConstraintData]
    lods: list[eCWrapper_emfx2Actor]
    actor: eCWrapper_emfx2Actor

    def read(self, reader: BinaryReader) -> None:
        version = reader.read_u16()
        if version != 54:
            raise ValueError("Version != 54 is not supported.")

        self.resource_size = reader.read_u32()
        self.resource_priority = reader.read_float()
        self.native_file_time = reader.read(bCDateTime)
        self.native_file_size = reader.read_u32()
        self.boundary = reader.read(bCBox)

        self.look_at_constraints = reader.read_list(eSLookAtConstraintData)
        self.lods = reader.read_list(eCWrapper_emfx2Actor)
        self.actor = reader.read(eCWrapper_emfx2Actor)

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u16(54)
        writer.write_u32(self.resource_size)
        writer.write_float(self.resource_priority)
        writer.write(self.native_file_time)
        writer.write_u32(self.native_file_size)
        writer.write(self.boundary)
        writer.write_list(self.look_at_constraints)
        writer.write_list(self.lods)
        writer.write(self.actor)
