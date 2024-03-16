from abc import ABC, abstractmethod
from enum import Enum, IntEnum
from typing import Generic, Type, TypeVar

from ..binary import BinaryReader, BinarySerializable, BinaryWriter
from ..types.math import bCQuaternion, bCVector, bCVector2
from ..types.misc import FloatColor


class LMA_CHUNK(IntEnum):
    # a node (LMA_Node) coming up next
    LMA_CHUNK_NODE = 0
    # a motion part (LMA_MotionPart) coming up next
    LMA_CHUNK_MOTIONPART = 1
    # an animation (LMA_Anim) coming up next
    LMA_CHUNK_ANIM = 2
    # a mesh (LMA_Mesh) coming up next
    LMA_CHUNK_MESH = 3
    # skinning information (LMA_SkinInfluence)
    LMA_CHUNK_SKINNINGINFO = 4
    # a collision mesh
    LMA_CHUNK_COLLISIONMESH = 5
    # a material (LMA_Material)
    LMA_CHUNK_MATERIAL = 6
    # a material layer (LMA_MaterialLayer)
    LMA_CHUNK_MATERIALLAYER = 7
    # a node limit information
    LMA_CHUNK_LIMIT = 8
    # physic information
    LMA_CHUNK_PHYSICSINFO = 9
    # a mesh expression part
    LMA_CHUNK_MESHEXPRESSIONPART = 10
    # a expression motion part
    LMA_CHUNK_EXPRESSIONMOTIONPART = 11
    # list of phonemes and keyframe data
    LMA_CHUNK_PHONEMEMOTIONDATA = 12
    # a FX material
    LMA_CHUNK_FXMATERIAL = 13
    # scene info
    LMA_CHUNK_SCENE_INFO = 16


class Chunk(BinarySerializable, ABC):
    @property
    @abstractmethod
    def chunk_id(self) -> int:
        pass

    @chunk_id.setter
    @abstractmethod
    def chunk_id(self, chunk_id: int) -> None:
        pass

    @property
    @abstractmethod
    def version(self) -> int:
        pass

    @version.setter
    @abstractmethod
    def version(self, version: int) -> None:
        pass


TChunk = TypeVar('TChunk', bound=Chunk)


class AbstractChunk(Chunk, ABC):
    _version: int
    _chunk_id: int

    @property
    def version(self) -> int:
        return self._version

    @version.setter
    def version(self, version: int) -> None:
        self._version = version

    @property
    def chunk_id(self) -> int:
        return self._chunk_id

    @chunk_id.setter
    def chunk_id(self, chunk_id: int) -> None:
        self._chunk_id = chunk_id


class UnknownChunk(AbstractChunk):
    chunk_data: bytes

    def read(self, reader: 'BinaryReader') -> None:
        raise NotImplementedError("No size provided.")

    def read_sized(self, reader: BinaryReader, size: int = None) -> None:
        self.chunk_data = reader.read_bytes(size)

    def write(self, writer: BinaryWriter) -> None:
        writer.write_bytes(self.chunk_data)


class NodeChunk(AbstractChunk):
    ID = LMA_CHUNK.LMA_CHUNK_NODE
    VERSION = 3

    position: bCVector
    rotation: bCQuaternion
    scale: bCVector
    scale_orient: bCQuaternion
    shear: bCVector
    name: str
    parent: str

    def read(self, reader: BinaryReader) -> None:
        self.position = reader.read_vec3()
        self.rotation = reader.read_quat()
        self.scale_orient = reader.read_quat()
        self.scale = reader.read_vec3()
        self.shear = reader.read_vec3()
        self.name = reader.read_str_u32()
        self.parent = reader.read_str_u32()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_vec3(self.position)
        writer.write_quat(self.rotation)
        writer.write_quat(self.scale_orient)
        writer.write_vec3(self.scale)
        writer.write_vec3(self.shear)
        writer.write_str_u32(self.name)
        writer.write_str_u32(self.parent)


class Vertex(BinarySerializable):
    org_vertex: int
    position: bCVector  # Z, Y, X
    normal: bCVector  # Z, Y, X
    uv_sets: list[bCVector2]

    def read(self, reader: 'BinaryReader') -> None:
        raise NotImplementedError("No size provided.")

    def read_sized(self, reader: BinaryReader, size: int) -> None:
        self.org_vertex = reader.read_u32()
        self.position = reader.read_vec3()
        self.normal = reader.read_vec3()
        self.uv_sets = reader.read_list(bCVector2, num=(size - 28) // 8)

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u32(self.org_vertex)
        writer.write_vec3(self.position)
        writer.write_vec3(self.normal)
        writer.write_iter(self.uv_sets)

    def get_position_xyz(self) -> bCVector:
        return bCVector(self.position.z, self.position.y, self.position.x)

    def get_normal_xyz(self) -> bCVector:
        return bCVector(self.normal.z, self.normal.y, self.normal.x)


class Submesh(BinarySerializable):
    mat_id: int
    num_uv_sets: int
    padding: bytes
    vertices: list[Vertex]
    indices: list[int]

    def read(self, reader: 'BinaryReader') -> None:
        raise NotImplementedError("No size provided.")

    def read_sized(self, reader: BinaryReader, override_num_uv_sets: int) -> None:
        self.mat_id = reader.read_u8()

        # Workaround for broken Rimy3D meshes (does not trip the original MeshChunkProcessor3,
        # because it ignores the num_uv_sets property of submeshes, and instead uses the one from
        # the mesh)
        self.num_uv_sets = reader.read_u8()
        if override_num_uv_sets is not None:
            self.num_uv_sets = override_num_uv_sets

        self.padding = reader.read_bytes(2)
        num_indices = reader.read_u32()
        num_verts = reader.read_u32()
        vertex_size = 28 + 8 * self.num_uv_sets
        self.vertices = reader.read_list(read=lambda r: r.read(Vertex, vertex_size), num=num_verts)
        self.indices = reader.read_list(read=BinaryReader.read_u32, num=num_indices)

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u8(self.mat_id)
        writer.write_u8(self.num_uv_sets)
        writer.write_bytes(self.padding)
        writer.write_u32(len(self.indices))
        writer.write_u32(len(self.vertices))
        writer.write_iter(self.vertices)
        writer.write_iter(self.indices, write=BinaryWriter.write_u32)


class MeshChunk(AbstractChunk):
    ID = LMA_CHUNK.LMA_CHUNK_MESH
    VERSION = 3

    node_number: int
    num_org_verts: int
    total_verts: int
    total_indices: int
    num_uv_sets: int
    is_collision_mesh: bool
    padding: bytes
    submeshes: list[Submesh]

    def read(self, reader: BinaryReader) -> None:
        self.node_number = reader.read_u32()
        self.num_org_verts = reader.read_u32()
        self.total_verts = reader.read_u32()
        self.total_indices = reader.read_u32()
        num_sub_meshes = reader.read_u32()
        self.num_uv_sets = reader.read_u32()
        self.is_collision_mesh = reader.read_bool()
        self.padding = reader.read_bytes(3)
        self.submeshes = reader.read_list(read=lambda r: r.read(Submesh, self.num_uv_sets), num=num_sub_meshes)

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u32(self.node_number)
        writer.write_u32(self.num_org_verts)
        writer.write_u32(self.total_verts)
        writer.write_u32(self.total_indices)
        writer.write_u32(len(self.submeshes))
        writer.write_u32(self.num_uv_sets)
        writer.write_bool(self.is_collision_mesh)
        writer.write_bytes(self.padding)
        writer.write_iter(self.submeshes)


class SkinInfluence(BinarySerializable):
    node_index: int
    padding: bytes
    weight: float

    def read(self, reader: BinaryReader) -> None:
        self.node_index = reader.read_u16()
        self.padding = reader.read_bytes(2)
        self.weight = reader.read_float()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u16(self.node_index)
        writer.write_bytes(self.padding)
        writer.write_float(self.weight)


class SkinningInfoChunk(AbstractChunk):
    ID = LMA_CHUNK.LMA_CHUNK_SKINNINGINFO
    VERSION = 1

    node_index: int
    influences: list[list[SkinInfluence]]

    def read(self, reader: 'BinaryReader') -> None:
        raise NotImplementedError("No size provided.")

    def read_sized(self, reader: BinaryReader, size: int) -> None:
        chunk_end_offset = reader.position() + size
        self.node_index = reader.read_u32()
        self.influences = []
        while reader.position() < chunk_end_offset:
            self.influences.append(reader.read_list(SkinInfluence, num=reader.read_u8()))

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u32(self.node_index)
        for influence in self.influences:
            writer.write_u8(len(influence))
            writer.write_iter(influence)


KeyFrameValueType = TypeVar('KeyFrameValueType', bCVector, bCQuaternion)


class InterpolationType(Enum):
    Linear = b'L'
    Bezier = b'B'
    TCB = b'T'


class AnimationType(Enum):
    Position = b'P'
    Rotation = b'R'
    Scaling = b'S'


class KeyFrame(BinarySerializable, Generic[KeyFrameValueType], ABC):
    time: float  # time in seconds
    value: KeyFrameValueType


class VectorKeyFrame(KeyFrame[bCVector]):
    def read(self, reader: BinaryReader) -> None:
        self.time = reader.read_float()
        self.value = reader.read_vec3()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_float(self.time)
        writer.write_vec3(self.value)


class QuaternionKeyFrame(KeyFrame[bCQuaternion]):
    def read(self, reader: BinaryReader) -> None:
        self.time = reader.read_float()
        self.value = reader.read_quat()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_float(self.time)
        writer.write_quat(self.value)


class KeyFrameChunk(AbstractChunk):
    """A key frame chunk applies to the most recent motion part chunk."""
    ID = LMA_CHUNK.LMA_CHUNK_ANIM
    VERSION = 1

    interpolation_type: InterpolationType
    animation_type: AnimationType
    frames: list[KeyFrame]

    def read(self, reader: BinaryReader) -> None:
        key_frame_count = reader.read_u32()
        self.interpolation_type = InterpolationType(reader.read_char())
        self.animation_type = AnimationType(reader.read_char())
        reader.skip(2)  # Padding

        match self.animation_type:
            case AnimationType.Position | AnimationType.Scaling:
                self.frames = reader.read_list(VectorKeyFrame, num=key_frame_count)
            case AnimationType.Rotation:
                self.frames = reader.read_list(QuaternionKeyFrame, num=key_frame_count)

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u32(len(self.frames))
        writer.write_char(self.interpolation_type.value)
        writer.write_char(self.animation_type.value)
        writer.write_u16(0)  # Padding
        writer.write_iter(self.frames)


class MotionPartChunk(AbstractChunk):
    ID = LMA_CHUNK.LMA_CHUNK_MOTIONPART
    VERSION = 3

    pose_position: bCVector  # initial pose position
    pose_rotation: bCQuaternion  # initial pose rotation
    pose_scale: bCVector  # initial pose scale
    bind_pose_position: bCVector  # initial pose position
    bind_pose_rotation: bCQuaternion  # initial pose rotation
    bind_pose_scale: bCVector  # initial pose scale
    name: str

    def read(self, reader: BinaryReader) -> None:
        self.pose_position = reader.read_vec3()
        self.pose_rotation = reader.read_quat()
        self.pose_scale = reader.read_vec3()
        self.bind_pose_position = reader.read_vec3()
        self.bind_pose_rotation = reader.read_quat()
        self.bind_pose_scale = reader.read_vec3()
        self.name = reader.read_str_u32()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_vec3(self.pose_position)
        writer.write_quat(self.pose_rotation)
        writer.write_vec3(self.pose_scale)
        writer.write_vec3(self.bind_pose_position)
        writer.write_quat(self.bind_pose_rotation)
        writer.write_vec3(self.bind_pose_scale)
        writer.write_str_u32(self.name)


class TransparencyType(Enum):
    Filter = b'F'
    Substractive = b'S'
    Additive = b'A'
    Unknown = b'U'


# TODO: Use annotations to auto-generate read and write... -> default value, read, write
class MaterialChunk(AbstractChunk):
    ID = LMA_CHUNK.LMA_CHUNK_MATERIAL
    VERSION = 5

    ambient_color: FloatColor
    diffuse_color: FloatColor
    specular_color: FloatColor
    emissive_color: FloatColor  # self illumination color
    shine: float
    shine_strength: float
    opacity: float  # the opacity amount [1.0=full opac, 0.0=full transparent]
    ior: float  # index of refraction
    double_sided: bool
    wire_frame: bool  # render in wireframe?
    transparency_type: TransparencyType
    padding: int
    material_name: str
    shader_file_name: str

    def read(self, reader: BinaryReader) -> None:
        self.ambient_color = reader.read(FloatColor)
        self.diffuse_color = reader.read(FloatColor)
        self.specular_color = reader.read(FloatColor)
        self.emissive_color = reader.read(FloatColor)
        self.shine = reader.read_float()
        self.shine_strength = reader.read_float()
        self.opacity = reader.read_float()
        self.ior = reader.read_float()
        self.double_sided = reader.read_bool()
        self.wire_frame = reader.read_bool()
        self.transparency_type = TransparencyType(reader.read_char())
        self.padding = reader.read_u8()
        self.material_name = reader.read_str_u32()
        self.shader_file_name = reader.read_str_u32()

    def write(self, writer: BinaryWriter) -> None:
        writer.write(self.ambient_color)
        writer.write(self.diffuse_color)
        writer.write(self.specular_color)
        writer.write(self.emissive_color)
        writer.write_float(self.shine)
        writer.write_float(self.shine_strength)
        writer.write_float(self.opacity)
        writer.write_float(self.ior)
        writer.write_bool(self.double_sided)
        writer.write_bool(self.wire_frame)
        writer.write_char(self.transparency_type.value)
        writer.write_u8(self.padding)
        writer.write_str_u32(self.material_name)
        writer.write_str_u32(self.shader_file_name)


def get_chunk_type(chunk_id: int, version: int):
    match chunk_id:
        case NodeChunk.ID:
            if version == NodeChunk.VERSION:
                return NodeChunk

        case MotionPartChunk.ID:
            if version == MotionPartChunk.VERSION:
                return MotionPartChunk

        case KeyFrameChunk.ID:
            if version == KeyFrameChunk.VERSION:
                return KeyFrameChunk

        case MeshChunk.ID:
            if version == MeshChunk.VERSION:
                return MeshChunk

        case SkinningInfoChunk.ID:
            if version == SkinningInfoChunk.VERSION:
                return SkinningInfoChunk

        case MaterialChunk.ID:
            if version == MaterialChunk.VERSION:
                return MaterialChunk

        case _:
            return UnknownChunk

    raise ValueError(f"ChunkID {chunk_id} with version {version} is not supported.")


class ChunkContainer:
    chunks: list[Chunk]

    def has_chunk(self, chunk_type: Type[TChunk]) -> bool:
        return any(self.get_chunks_by_type(chunk_type))

    def get_chunk_by_type(self, chunk_type: Type[TChunk]) -> TChunk:
        typed_chunks = self.get_chunks_by_type(chunk_type)
        assert len(typed_chunks) == 1
        return typed_chunks[0]

    def get_chunks_by_type(self, chunk_type: Type[TChunk]) -> list[TChunk]:
        return [c for c in self.chunks if c.chunk_id == chunk_type.ID]

    def read_chunks(self, reader: BinaryReader, offset_end: int):
        self.chunks = []
        while reader.position() < offset_end:
            chunk_id = reader.read_u32()
            chunk_size = reader.read_u32()
            chunk_version = reader.read_u32()
            chunk_type = get_chunk_type(chunk_id, chunk_version)
            chunk = reader.read(chunk_type, chunk_size)
            chunk.chunk_id = chunk_id
            chunk.version = chunk_version
            self.chunks.append(chunk)

    def write_chunks(self, writer: BinaryWriter) -> None:
        for chunk in self.chunks:
            writer.write_u32(chunk.chunk_id)
            chunk_size_offset = writer.position()
            writer.write_u32(0)
            writer.write_u32(chunk.version)
            writer.write(chunk)
            with writer.at_position(chunk_size_offset) as pos:
                writer.write_u32(pos - chunk_size_offset - 8)

    def add_chunk(self, chunk_type: Type[TChunk]) -> TChunk:
        chunk = chunk_type()
        chunk.chunk_id = chunk_type.ID
        chunk.version = chunk_type.VERSION
        self.chunks.append(chunk)
        return chunk
