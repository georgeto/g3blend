# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

from . import kaitaistruct
from .kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import Enum
from .report_wrong_version import ReportWrongVersion

if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

from . import genomfle
class Xmot(ReadWriteKaitaiStruct):
    """Gothic 3 animation motion format
    """

    class LmaChunkId(Enum):
        node = 0
        motionpart = 1
        anim = 2
        mesh = 3
        skinninginfo = 4
        collisionmesh = 5
        material = 6
        materiallayer = 7
        limit = 8
        physicsinfo = 9
        meshexpressionpart = 10
        expressionmotionpart = 11
        phonememotiondata = 12
        fxmaterial = 13
        scene_info = 16
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        self.meta = genomfle.Genomfle(self._io)
        self.meta._read()
        self.version = self._io.read_u2le()
        self.resource_size = self._io.read_u4le()
        self.resource_priority = self._io.read_f4le()
        self.native_file_time = self._io.read_u8le()
        self.native_file_size = self._io.read_u4le()
        if (self.version >= 3):
            pass
            self.unk_file_time = self._io.read_u8le()

        if (self.version >= 2):
            pass
            self.num_frame_effects = self._io.read_u2le()

        if (self.version >= 2):
            pass
            self.frame_effects = []
            for i in range(self.num_frame_effects):
                _t_frame_effects = Xmot.FrameEffect(self._io, self, self._root)
                _t_frame_effects._read()
                self.frame_effects.append(_t_frame_effects)


        self.motion = Xmot.Emfx2Motion(self._io, self, self._root)
        self.motion._read()


    def _fetch_instances(self):
        pass
        self.meta._fetch_instances()
        if (self.version >= 3):
            pass

        if (self.version >= 2):
            pass

        if (self.version >= 2):
            pass
            for i in range(len(self.frame_effects)):
                pass
                self.frame_effects[i]._fetch_instances()


        self.motion._fetch_instances()


    def _write__seq(self, io=None):
        super(Xmot, self)._write__seq(io)
        self.meta._write__seq(self._io)
        self._io.write_u2le(self.version)
        self._io.write_u4le(self.resource_size)
        self._io.write_f4le(self.resource_priority)
        self._io.write_u8le(self.native_file_time)
        self._io.write_u4le(self.native_file_size)
        if (self.version >= 3):
            pass
            self._io.write_u8le(self.unk_file_time)

        if (self.version >= 2):
            pass
            self._io.write_u2le(self.num_frame_effects)

        if (self.version >= 2):
            pass
            for i in range(len(self.frame_effects)):
                pass
                self.frame_effects[i]._write__seq(self._io)


        self.motion._write__seq(self._io)


    def _check(self):
        pass
        if (self.version >= 3):
            pass

        if (self.version >= 2):
            pass

        if (self.version >= 2):
            pass
            self.num_frame_effects = len(self.frame_effects)
            if (len(self.frame_effects) != self.num_frame_effects):
                raise kaitaistruct.ConsistencyError(u"frame_effects", len(self.frame_effects), self.num_frame_effects)
            for i in range(len(self.frame_effects)):
                pass
                if self.frame_effects[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"frame_effects", self.frame_effects[i]._root, self._root)
                if self.frame_effects[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"frame_effects", self.frame_effects[i]._parent, self)


        if self.motion._root != self._root:
            raise kaitaistruct.ConsistencyError(u"motion", self.motion._root, self._root)
        if self.motion._parent != self:
            raise kaitaistruct.ConsistencyError(u"motion", self.motion._parent, self)

    class Chunk(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.chunk_id = KaitaiStream.resolve_enum(Xmot.LmaChunkId, self._io.read_u4le())
            self.chunk_size = self._io.read_u4le()
            self.version = self._io.read_u4le()
            _on = self.chunk_id
            if _on == Xmot.LmaChunkId.motionpart:
                pass
                self._raw_content = self._io.read_bytes(self.chunk_size)
                _io__raw_content = KaitaiStream(BytesIO(self._raw_content))
                self.content = Xmot.CnkMotionPart(_io__raw_content, self, self._root)
                self.content._read()
            elif _on == Xmot.LmaChunkId.anim:
                pass
                self._raw_content = self._io.read_bytes(self.chunk_size)
                _io__raw_content = KaitaiStream(BytesIO(self._raw_content))
                self.content = Xmot.CnkKeyFrame(_io__raw_content, self, self._root)
                self.content._read()
            else:
                pass
                self.content = self._io.read_bytes(self.chunk_size)


        def _fetch_instances(self):
            pass
            _on = self.chunk_id
            if _on == Xmot.LmaChunkId.motionpart:
                pass
                self.content._fetch_instances()
            elif _on == Xmot.LmaChunkId.anim:
                pass
                self.content._fetch_instances()
            else:
                pass


        def _write__seq(self, io=None):
            super(Xmot.Chunk, self)._write__seq(io)
            self._io.write_u4le(self.chunk_id.value)
            _pos_chunk_size = self._io.pos()
            self.chunk_size = 0
            self._io.write_u4le(self.chunk_size)
            self._io.write_u4le(self.version)
            _pos_content = self._io.pos()
            _on = self.chunk_id
            if _on == Xmot.LmaChunkId.motionpart:
                pass
                self.content._write__seq(self._io)
            elif _on == Xmot.LmaChunkId.anim:
                pass
                self.content._write__seq(self._io)
            else:
                pass
                self._io.write_bytes(self.content)

            _pos_save = self._io.pos()
            self.chunk_size = _pos_save - _pos_content
            self._io.seek(_pos_chunk_size)
            self._io.write_u4le(self.chunk_size)
            self._io.seek(_pos_save)


        def _check(self):
            pass
            _on = self.chunk_id
            if _on == Xmot.LmaChunkId.motionpart:
                pass
                if self.content._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"content", self.content._root, self._root)
                if self.content._parent != self:
                    raise kaitaistruct.ConsistencyError(u"content", self.content._parent, self)
            elif _on == Xmot.LmaChunkId.anim:
                pass
                if self.content._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"content", self.content._root, self._root)
                if self.content._parent != self:
                    raise kaitaistruct.ConsistencyError(u"content", self.content._parent, self)


    class CnkUnknown(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.data = self._io.read_bytes_full()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Xmot.CnkUnknown, self)._write__seq(io)
            self._io.write_bytes(self.data)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"data", self._io.size() - self._io.pos(), 0)


        def _check(self):
            pass


    class VectorKeyFrame(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.time = self._io.read_f4le()
            self.value = Xmot.Vector(self._io, self, self._root)
            self.value._read()


        def _fetch_instances(self):
            pass
            self.value._fetch_instances()


        def _write__seq(self, io=None):
            super(Xmot.VectorKeyFrame, self)._write__seq(io)
            self._io.write_f4le(self.time)
            self.value._write__seq(self._io)


        def _check(self):
            pass
            if self.value._root != self._root:
                raise kaitaistruct.ConsistencyError(u"value", self.value._root, self._root)
            if self.value._parent != self:
                raise kaitaistruct.ConsistencyError(u"value", self.value._parent, self)


    class CnkKeyFrame(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            if (self._parent.version != 1):
                pass
                self._raw_version_guard = self._io.read_bytes(0)
                _process = ReportWrongVersion()
                self.version_guard = _process.decode(self._raw_version_guard)

            self.num_frames = self._io.read_u4le()
            self.interpolation_type = (self._io.read_bytes(1)).decode("windows-1252")
            self.animation_type = (self._io.read_bytes(1)).decode("windows-1252")
            self.reserverd = self._io.read_u2le()
            self.frames = []
            for i in range(self.num_frames):
                _on = self.animation_type
                if _on == u"P":
                    pass
                    _t_frames = Xmot.VectorKeyFrame(self._io, self, self._root)
                    _t_frames._read()
                    self.frames.append(_t_frames)
                elif _on == u"R":
                    pass
                    _t_frames = Xmot.QuaternionKeyFrame(self._io, self, self._root)
                    _t_frames._read()
                    self.frames.append(_t_frames)
                elif _on == u"S":
                    pass
                    _t_frames = Xmot.VectorKeyFrame(self._io, self, self._root)
                    _t_frames._read()
                    self.frames.append(_t_frames)



        def _fetch_instances(self):
            pass
            if (self._parent.version != 1):
                pass

            for i in range(len(self.frames)):
                pass
                _on = self.animation_type
                if _on == u"P":
                    pass
                    self.frames[i]._fetch_instances()
                elif _on == u"R":
                    pass
                    self.frames[i]._fetch_instances()
                elif _on == u"S":
                    pass
                    self.frames[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xmot.CnkKeyFrame, self)._write__seq(io)
            if (self._parent.version != 1):
                pass
                _process_version_guard = ReportWrongVersion()
                self._raw_version_guard = _process_version_guard.encode(self.version_guard)
                if (len(self._raw_version_guard) != 0):
                    raise kaitaistruct.ConsistencyError(u"version_guard", len(self._raw_version_guard), 0)
                self._io.write_bytes(self._raw_version_guard)

            self._io.write_u4le(self.num_frames)
            self._io.write_bytes((self.interpolation_type).encode(u"windows-1252"))
            self._io.write_bytes((self.animation_type).encode(u"windows-1252"))
            self._io.write_u2le(self.reserverd)
            for i in range(len(self.frames)):
                pass
                _on = self.animation_type
                if _on == u"P":
                    pass
                    self.frames[i]._write__seq(self._io)
                elif _on == u"R":
                    pass
                    self.frames[i]._write__seq(self._io)
                elif _on == u"S":
                    pass
                    self.frames[i]._write__seq(self._io)



        def _check(self):
            pass
            if (self._parent.version != 1):
                pass

            if (len((self.interpolation_type).encode(u"windows-1252")) != 1):
                raise kaitaistruct.ConsistencyError(u"interpolation_type", len((self.interpolation_type).encode(u"windows-1252")), 1)
            if (len((self.animation_type).encode(u"windows-1252")) != 1):
                raise kaitaistruct.ConsistencyError(u"animation_type", len((self.animation_type).encode(u"windows-1252")), 1)
            self.num_frames = len(self.frames)
            if (len(self.frames) != self.num_frames):
                raise kaitaistruct.ConsistencyError(u"frames", len(self.frames), self.num_frames)
            for i in range(len(self.frames)):
                pass
                _on = self.animation_type
                if _on == u"P":
                    pass
                    if self.frames[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"frames", self.frames[i]._root, self._root)
                    if self.frames[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"frames", self.frames[i]._parent, self)
                elif _on == u"R":
                    pass
                    if self.frames[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"frames", self.frames[i]._root, self._root)
                    if self.frames[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"frames", self.frames[i]._parent, self)
                elif _on == u"S":
                    pass
                    if self.frames[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"frames", self.frames[i]._root, self._root)
                    if self.frames[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"frames", self.frames[i]._parent, self)



    class Chunks(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.chunks = []
            i = 0
            while not self._io.is_eof():
                _t_chunks = Xmot.Chunk(self._io, self, self._root)
                _t_chunks._read()
                self.chunks.append(_t_chunks)
                i += 1



        def _fetch_instances(self):
            pass
            for i in range(len(self.chunks)):
                pass
                self.chunks[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xmot.Chunks, self)._write__seq(io)
            for i in range(len(self.chunks)):
                pass
                self.chunks[i]._write__seq(self._io)


        def _check(self):
            pass
            for i in range(len(self.chunks)):
                pass
                if self.chunks[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"chunks", self.chunks[i]._root, self._root)
                if self.chunks[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"chunks", self.chunks[i]._parent, self)



    class Vector(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Xmot.Vector, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            pass


    class CnkMotionPart(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            if (self._parent.version != 3):
                pass
                self._raw_version_guard = self._io.read_bytes(0)
                _process = ReportWrongVersion()
                self.version_guard = _process.decode(self._raw_version_guard)

            self.pose_position = Xmot.Vector(self._io, self, self._root)
            self.pose_position._read()
            self.pose_rotation = Xmot.Quaternion(self._io, self, self._root)
            self.pose_rotation._read()
            self.pose_scale = Xmot.Vector(self._io, self, self._root)
            self.pose_scale._read()
            self.bind_pose_position = Xmot.Vector(self._io, self, self._root)
            self.bind_pose_position._read()
            self.bind_pose_rotation = Xmot.Quaternion(self._io, self, self._root)
            self.bind_pose_rotation._read()
            self.bind_pose_scale = Xmot.Vector(self._io, self, self._root)
            self.bind_pose_scale._read()
            self.name = Xmot.LmaString(self._io, self, self._root)
            self.name._read()


        def _fetch_instances(self):
            pass
            if (self._parent.version != 3):
                pass

            self.pose_position._fetch_instances()
            self.pose_rotation._fetch_instances()
            self.pose_scale._fetch_instances()
            self.bind_pose_position._fetch_instances()
            self.bind_pose_rotation._fetch_instances()
            self.bind_pose_scale._fetch_instances()
            self.name._fetch_instances()


        def _write__seq(self, io=None):
            super(Xmot.CnkMotionPart, self)._write__seq(io)
            if (self._parent.version != 3):
                pass
                _process_version_guard = ReportWrongVersion()
                self._raw_version_guard = _process_version_guard.encode(self.version_guard)
                if (len(self._raw_version_guard) != 0):
                    raise kaitaistruct.ConsistencyError(u"version_guard", len(self._raw_version_guard), 0)
                self._io.write_bytes(self._raw_version_guard)

            self.pose_position._write__seq(self._io)
            self.pose_rotation._write__seq(self._io)
            self.pose_scale._write__seq(self._io)
            self.bind_pose_position._write__seq(self._io)
            self.bind_pose_rotation._write__seq(self._io)
            self.bind_pose_scale._write__seq(self._io)
            self.name._write__seq(self._io)


        def _check(self):
            pass
            if (self._parent.version != 3):
                pass

            if self.pose_position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"pose_position", self.pose_position._root, self._root)
            if self.pose_position._parent != self:
                raise kaitaistruct.ConsistencyError(u"pose_position", self.pose_position._parent, self)
            if self.pose_rotation._root != self._root:
                raise kaitaistruct.ConsistencyError(u"pose_rotation", self.pose_rotation._root, self._root)
            if self.pose_rotation._parent != self:
                raise kaitaistruct.ConsistencyError(u"pose_rotation", self.pose_rotation._parent, self)
            if self.pose_scale._root != self._root:
                raise kaitaistruct.ConsistencyError(u"pose_scale", self.pose_scale._root, self._root)
            if self.pose_scale._parent != self:
                raise kaitaistruct.ConsistencyError(u"pose_scale", self.pose_scale._parent, self)
            if self.bind_pose_position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bind_pose_position", self.bind_pose_position._root, self._root)
            if self.bind_pose_position._parent != self:
                raise kaitaistruct.ConsistencyError(u"bind_pose_position", self.bind_pose_position._parent, self)
            if self.bind_pose_rotation._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bind_pose_rotation", self.bind_pose_rotation._root, self._root)
            if self.bind_pose_rotation._parent != self:
                raise kaitaistruct.ConsistencyError(u"bind_pose_rotation", self.bind_pose_rotation._parent, self)
            if self.bind_pose_scale._root != self._root:
                raise kaitaistruct.ConsistencyError(u"bind_pose_scale", self.bind_pose_scale._root, self._root)
            if self.bind_pose_scale._parent != self:
                raise kaitaistruct.ConsistencyError(u"bind_pose_scale", self.bind_pose_scale._parent, self)
            if self.name._root != self._root:
                raise kaitaistruct.ConsistencyError(u"name", self.name._root, self._root)
            if self.name._parent != self:
                raise kaitaistruct.ConsistencyError(u"name", self.name._parent, self)


    class String(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.strtab_index = self._io.read_u2le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Xmot.String, self)._write__seq(io)
            self._io.write_u2le(self.strtab_index)


        def _check(self):
            pass


    class Emfx2Motion(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.size = self._io.read_u4le()
            self.magic = self._io.read_bytes(4)
            if not (self.magic == b"\x4C\x4D\x41\x20"):
                raise kaitaistruct.ValidationNotEqualError(b"\x4C\x4D\x41\x20", self.magic, self._io, u"/types/emfx2_motion/seq/1")
            self.high_version = self._io.read_bytes(1)
            if not (self.high_version == b"\x01"):
                raise kaitaistruct.ValidationNotEqualError(b"\x01", self.high_version, self._io, u"/types/emfx2_motion/seq/2")
            self.low_version = self._io.read_bytes(1)
            if not (self.low_version == b"\x01"):
                raise kaitaistruct.ValidationNotEqualError(b"\x01", self.low_version, self._io, u"/types/emfx2_motion/seq/3")
            self.is_actor = self._io.read_bytes(1)
            if not (self.is_actor == b"\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x00", self.is_actor, self._io, u"/types/emfx2_motion/seq/4")
            # TOOD: Optimize this, no need to ready everything in a byte array I guess...
            self._raw_chunks = self._io.read_bytes((self.size - 7))
            _io__raw_chunks = KaitaiStream(BytesIO(self._raw_chunks))
            self.chunks = Xmot.Chunks(_io__raw_chunks, self, self._root)
            self.chunks._read()


        def _fetch_instances(self):
            pass
            self.chunks._fetch_instances()


        def _write__seq(self, io=None):
            super(Xmot.Emfx2Motion, self)._write__seq(io)
            _pos_size = self._io.pos()
            self.size = 0
            self._io.write_u4le(self.size)
            _pos_data = self._io.pos()
            self._io.write_bytes(self.magic)
            self._io.write_bytes(self.high_version)
            self._io.write_bytes(self.low_version)
            self._io.write_bytes(self.is_actor)
            self.chunks._write__seq(self._io)
            _pos_save = self._io.pos()
            self.size = _pos_save - _pos_data
            self._io.seek(_pos_size)
            self._io.write_u4le(self.size)
            self._io.seek(_pos_save)

        def _check(self):
            pass
            if not hasattr(self, 'magic') or self.magic is None:
                self.magic = b"\x4C\x4D\x41\x20"
            if (len(self.magic) != 4):
                raise kaitaistruct.ConsistencyError(u"magic", len(self.magic), 4)
            if not (self.magic == b"\x4C\x4D\x41\x20"):
                raise kaitaistruct.ValidationNotEqualError(b"\x4C\x4D\x41\x20", self.magic, self._io, u"/types/emfx2_motion/seq/1")
            if not hasattr(self, 'high_version') or self.high_version is None:
                self.high_version = b"\x01"
            if (len(self.high_version) != 1):
                raise kaitaistruct.ConsistencyError(u"high_version", len(self.high_version), 1)
            if not (self.high_version == b"\x01"):
                raise kaitaistruct.ValidationNotEqualError(b"\x01", self.high_version, self._io, u"/types/emfx2_motion/seq/2")
            if not hasattr(self, 'low_version') or self.low_version is None:
                self.low_version = b"\x01"
            if (len(self.low_version) != 1):
                raise kaitaistruct.ConsistencyError(u"low_version", len(self.low_version), 1)
            if not (self.low_version == b"\x01"):
                raise kaitaistruct.ValidationNotEqualError(b"\x01", self.low_version, self._io, u"/types/emfx2_motion/seq/3")
            if not hasattr(self, 'is_actor') or self.is_actor is None:
                self.is_actor = b"\x00"
            if (len(self.is_actor) != 1):
                raise kaitaistruct.ConsistencyError(u"is_actor", len(self.is_actor), 1)
            if not (self.is_actor == b"\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x00", self.is_actor, self._io, u"/types/emfx2_motion/seq/4")
            if self.chunks._root != self._root:
                raise kaitaistruct.ConsistencyError(u"chunks", self.chunks._root, self._root)
            if self.chunks._parent != self:
                raise kaitaistruct.ConsistencyError(u"chunks", self.chunks._parent, self)


    class FrameEffect(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.key_frame = self._io.read_u2le()
            self.effect_name = Xmot.String(self._io, self, self._root)
            self.effect_name._read()


        def _fetch_instances(self):
            pass
            self.effect_name._fetch_instances()


        def _write__seq(self, io=None):
            super(Xmot.FrameEffect, self)._write__seq(io)
            self._io.write_u2le(self.key_frame)
            self.effect_name._write__seq(self._io)


        def _check(self):
            pass
            if self.effect_name._root != self._root:
                raise kaitaistruct.ConsistencyError(u"effect_name", self.effect_name._root, self._root)
            if self.effect_name._parent != self:
                raise kaitaistruct.ConsistencyError(u"effect_name", self.effect_name._parent, self)


    class LmaString(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.len = self._io.read_u4le()
            self.data = (self._io.read_bytes(self.len)).decode("windows-1252")


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Xmot.LmaString, self)._write__seq(io)
            self._io.write_u4le(self.len)
            self._io.write_bytes((self.data).encode(u"windows-1252"))


        def _check(self):
            pass
            self.len = len((self.data).encode(u"windows-1252"))
            if (len((self.data).encode(u"windows-1252")) != self.len):
                raise kaitaistruct.ConsistencyError(u"data", len((self.data).encode(u"windows-1252")), self.len)


    class Quaternion(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Xmot.Quaternion, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            pass


    class QuaternionKeyFrame(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.time = self._io.read_f4le()
            self.value = Xmot.Quaternion(self._io, self, self._root)
            self.value._read()


        def _fetch_instances(self):
            pass
            self.value._fetch_instances()


        def _write__seq(self, io=None):
            super(Xmot.QuaternionKeyFrame, self)._write__seq(io)
            self._io.write_f4le(self.time)
            self.value._write__seq(self._io)


        def _check(self):
            pass
            if self.value._root != self._root:
                raise kaitaistruct.ConsistencyError(u"value", self.value._root, self._root)
            if self.value._parent != self:
                raise kaitaistruct.ConsistencyError(u"value", self.value._parent, self)



