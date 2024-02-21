# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore
from typing import NamedTuple

from .import kaitaistruct
from .kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import Enum
from .report_wrong_version import ReportWrongVersion


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

from . import genomfle
class Xact(ReadWriteKaitaiStruct):
    """Gothic 3 animation actor format
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
        self.version = self._io.read_bytes(2)
        if not (self.version == b"\x36\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x36\x00", self.version, self._io, u"/seq/1")
        self.resource_size = self._io.read_u4le()
        self.resource_priority = self._io.read_f4le()
        self.native_file_time = self._io.read_u8le()
        self.native_file_size = self._io.read_u4le()
        self.boundary_min = Xact._read_vector(self._io)
        self.boundary_max = Xact._read_vector(self._io)
        self.num_look_at_constraints = self._io.read_u4le()
        self.look_at_constraints = []
        for i in range(self.num_look_at_constraints):
            _t_look_at_constraints = Xact.LookAtConstraint(self._io, self, self._root)
            _t_look_at_constraints._read()
            self.look_at_constraints.append(_t_look_at_constraints)

        self.num_lods = self._io.read_u4le()
        self.lods = []
        for i in range(self.num_lods):
            _t_lods = Xact.Emfx2Actor(self._io, self, self._root)
            _t_lods._read()
            self.lods.append(_t_lods)

        self.actor = Xact.Emfx2Actor(self._io, self, self._root)
        self.actor._read()


    def _fetch_instances(self):
        pass
        self.meta._fetch_instances()
        for i in range(len(self.look_at_constraints)):
            pass
            self.look_at_constraints[i]._fetch_instances()

        for i in range(len(self.lods)):
            pass
            self.lods[i]._fetch_instances()

        self.actor._fetch_instances()


    def _write__seq(self, io=None):
        super(Xact, self)._write__seq(io)
        self.meta._write__seq(self._io)
        self._io.write_bytes(self.version)
        self._io.write_u4le(self.resource_size)
        self._io.write_f4le(self.resource_priority)
        self._io.write_u8le(self.native_file_time)
        self._io.write_u4le(self.native_file_size)
        self.boundary_min._write__seq(self._io)
        self.boundary_max._write__seq(self._io)
        self._io.write_u4le(self.num_look_at_constraints)
        for i in range(len(self.look_at_constraints)):
            pass
            self.look_at_constraints[i]._write__seq(self._io)

        self._io.write_u4le(self.num_lods)
        for i in range(len(self.lods)):
            pass
            self.lods[i]._write__seq(self._io)

        self.actor._write__seq(self._io)


    def _check(self):
        pass
        if not hasattr(self, 'version') or self.version is None:
            self.version = b"\x36\x00"
        if (len(self.version) != 2):
            raise kaitaistruct.ConsistencyError(u"version", len(self.version), 2)
        if not (self.version == b"\x36\x00"):
            raise kaitaistruct.ValidationNotEqualError(b"\x36\x00", self.version, self._io, u"/seq/1")
        if self.boundary_min._parent != self:
            raise kaitaistruct.ConsistencyError(u"boundary_min", self.boundary_min._parent, self)
        if self.boundary_max._root != self._root:
            raise kaitaistruct.ConsistencyError(u"boundary_max", self.boundary_max._root, self._root)
        if self.boundary_max._parent != self:
            raise kaitaistruct.ConsistencyError(u"boundary_max", self.boundary_max._parent, self)
        if (len(self.look_at_constraints) != self.num_look_at_constraints):
            raise kaitaistruct.ConsistencyError(u"look_at_constraints", len(self.look_at_constraints), self.num_look_at_constraints)
        for i in range(len(self.look_at_constraints)):
            pass
            if self.look_at_constraints[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"look_at_constraints", self.look_at_constraints[i]._root, self._root)
            if self.look_at_constraints[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"look_at_constraints", self.look_at_constraints[i]._parent, self)

        if (len(self.lods) != self.num_lods):
            raise kaitaistruct.ConsistencyError(u"lods", len(self.lods), self.num_lods)
        for i in range(len(self.lods)):
            pass
            if self.lods[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"lods", self.lods[i]._root, self._root)
            if self.lods[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"lods", self.lods[i]._parent, self)

        if self.actor._root != self._root:
            raise kaitaistruct.ConsistencyError(u"actor", self.actor._root, self._root)
        if self.actor._parent != self:
            raise kaitaistruct.ConsistencyError(u"actor", self.actor._parent, self)

    class Vector2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Xact.Vector2, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)


        def _check(self):
            pass


    class FloatColor(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.red = self._io.read_f4le()
            self.green = self._io.read_f4le()
            self.blue = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Xact.FloatColor, self)._write__seq(io)
            self._io.write_f4le(self.red)
            self._io.write_f4le(self.green)
            self._io.write_f4le(self.blue)


        def _check(self):
            pass


    class Chunk(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.chunk_id = KaitaiStream.resolve_enum(Xact.LmaChunkId, self._io.read_u4le())
            self.chunk_size = self._io.read_u4le()
            self.version = self._io.read_u4le()
            _on = self.chunk_id
            if _on == Xact.LmaChunkId.material:
                pass
                self._raw_content = self._io.read_bytes(self.chunk_size)
                _io__raw_content = KaitaiStream(BytesIO(self._raw_content))
                self.content = Xact.CnkMaterial(_io__raw_content, self, self._root)
                self.content._read()
            elif _on == Xact.LmaChunkId.mesh:
                pass
                self._raw_content = self._io.read_bytes(self.chunk_size)
                _io__raw_content = KaitaiStream(BytesIO(self._raw_content))
                self.content = Xact.CnkMesh(_io__raw_content, self, self._root)
                self.content._read()
            elif _on == Xact.LmaChunkId.node:
                pass
                self._raw_content = self._io.read_bytes(self.chunk_size)
                _io__raw_content = KaitaiStream(BytesIO(self._raw_content))
                self.content = Xact.CnkNode(_io__raw_content, self, self._root)
                self.content._read()
            elif _on == Xact.LmaChunkId.skinninginfo:
                pass
                self._raw_content = self._io.read_bytes(self.chunk_size)
                _io__raw_content = KaitaiStream(BytesIO(self._raw_content))
                self.content = Xact.CnkSkinninginfo(_io__raw_content, self, self._root)
                self.content._read()
            else:
                pass
                self.content = self._io.read_bytes(self.chunk_size)


        def _fetch_instances(self):
            pass
            _on = self.chunk_id
            if _on == Xact.LmaChunkId.material:
                pass
                self.content._fetch_instances()
            elif _on == Xact.LmaChunkId.mesh:
                pass
                self.content._fetch_instances()
            elif _on == Xact.LmaChunkId.node:
                pass
                self.content._fetch_instances()
            elif _on == Xact.LmaChunkId.skinninginfo:
                pass
                self.content._fetch_instances()
            else:
                pass


        def _write__seq(self, io=None):
            super(Xact.Chunk, self)._write__seq(io)
            self._io.write_u4le(self.chunk_id.value)
            _pos_chunk_size = self._io.pos()
            self.chunk_size = 0
            self._io.write_u4le(self.chunk_size)
            self._io.write_u4le(self.version)
            _pos_content = self._io.pos()
            _on = self.chunk_id
            if _on == Xact.LmaChunkId.material:
                pass
                self.content._write__seq(self._io)
            elif _on == Xact.LmaChunkId.mesh:
                pass
                self.content._write__seq(self._io)
            elif _on == Xact.LmaChunkId.node:
                pass
                self.content._write__seq(self._io)
            elif _on == Xact.LmaChunkId.skinninginfo:
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
            if _on == Xact.LmaChunkId.material:
                pass
                if self.content._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"content", self.content._root, self._root)
                if self.content._parent != self:
                    raise kaitaistruct.ConsistencyError(u"content", self.content._parent, self)
            elif _on == Xact.LmaChunkId.mesh:
                pass
                if self.content._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"content", self.content._root, self._root)
                if self.content._parent != self:
                    raise kaitaistruct.ConsistencyError(u"content", self.content._parent, self)
            elif _on == Xact.LmaChunkId.node:
                pass
                if self.content._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"content", self.content._root, self._root)
                if self.content._parent != self:
                    raise kaitaistruct.ConsistencyError(u"content", self.content._parent, self)
            elif _on == Xact.LmaChunkId.skinninginfo:
                pass
                if self.content._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"content", self.content._root, self._root)
                if self.content._parent != self:
                    raise kaitaistruct.ConsistencyError(u"content", self.content._parent, self)


    class CnkSkinninginfo(ReadWriteKaitaiStruct):
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

            self.node_index = self._io.read_u4le()
            self.influences = []
            i = 0
            while not self._io.is_eof():
                _t_influences = Xact.Influences(self._io, self, self._root)
                _t_influences._read()
                self.influences.append(_t_influences)
                i += 1



        def _fetch_instances(self):
            pass
            if (self._parent.version != 1):
                pass

            for i in range(len(self.influences)):
                pass
                self.influences[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xact.CnkSkinninginfo, self)._write__seq(io)
            if (self._parent.version != 1):
                pass
                _process_version_guard = ReportWrongVersion()
                self._raw_version_guard = _process_version_guard.encode(self.version_guard)
                if (len(self._raw_version_guard) != 0):
                    raise kaitaistruct.ConsistencyError(u"version_guard", len(self._raw_version_guard), 0)
                self._io.write_bytes(self._raw_version_guard)

            self._io.write_u4le(self.node_index)
            for i in range(len(self.influences)):
                pass
                self.influences[i]._write__seq(self._io)


        def _check(self):
            pass
            if (self._parent.version != 1):
                pass

            for i in range(len(self.influences)):
                pass
                if self.influences[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"influences", self.influences[i]._root, self._root)
                if self.influences[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"influences", self.influences[i]._parent, self)



    class Vertex(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.org_vertex = self._io.read_u4le()
            self.position = Xact._read_vector(self._io)
            self.normal = Xact._read_vector(self._io)
            self.uv_sets = []
            for i in range(self._parent.override_num_uv_sets):
                _t_uv_sets = Xact.Vector2(self._io, self, self._root)
                _t_uv_sets._read()
                self.uv_sets.append(_t_uv_sets)



        def _fetch_instances(self):
            pass
            for i in range(len(self.uv_sets)):
                pass
                self.uv_sets[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xact.Vertex, self)._write__seq(io)
            self._io.write_u4le(self.org_vertex)
            self.position._write__seq(self._io)
            self.normal._write__seq(self._io)
            for i in range(len(self.uv_sets)):
                pass
                self.uv_sets[i]._write__seq(self._io)



        def _check(self):
            pass
            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.normal._root != self._root:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._root, self._root)
            if self.normal._parent != self:
                raise kaitaistruct.ConsistencyError(u"normal", self.normal._parent, self)
            if (len(self.uv_sets) != self._parent.override_num_uv_sets):
                raise kaitaistruct.ConsistencyError(u"uv_sets", len(self.uv_sets), self._parent.override_num_uv_sets)
            for i in range(len(self.uv_sets)):
                pass
                if self.uv_sets[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"uv_sets", self.uv_sets[i]._root, self._root)
                if self.uv_sets[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"uv_sets", self.uv_sets[i]._parent, self)



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
            super(Xact.CnkUnknown, self)._write__seq(io)
            self._io.write_bytes(self.data)
            if not self._io.is_eof():
                raise kaitaistruct.ConsistencyError(u"data", self._io.size() - self._io.pos(), 0)


        def _check(self):
            pass


    class TangentVertices(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.values = []
            i = 0
            while not self._io.is_eof():
                _t_values = Xact._read_vector(self._io)
                self.values.append(_t_values)
                i += 1



        def _fetch_instances(self):
            pass



        def _write__seq(self, io=None):
            super(Xact.TangentVertices, self)._write__seq(io)
            for i in range(len(self.values)):
                pass
                self.values[i]._write__seq(self._io)


        def _check(self):
            pass
            for i in range(len(self.values)):
                pass
                if self.values[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"values", self.values[i]._root, self._root)
                if self.values[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"values", self.values[i]._parent, self)



    class LookAtConstraint(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.node_name = Xact.String(self._io, self, self._root)
            self.node_name._read()
            self.interpolation_speed = self._io.read_f4le()
            self.min_constraints = Xact._read_vector(self._io)
            self.max_constraints = Xact._read_vector(self._io)


        def _fetch_instances(self):
            pass
            self.node_name._fetch_instances()
            self.min_constraints._fetch_instances()
            self.max_constraints._fetch_instances()


        def _write__seq(self, io=None):
            super(Xact.LookAtConstraint, self)._write__seq(io)
            self.node_name._write__seq(self._io)
            self._io.write_f4le(self.interpolation_speed)
            self.min_constraints._write__seq(self._io)
            self.max_constraints._write__seq(self._io)


        def _check(self):
            pass
            if self.node_name._root != self._root:
                raise kaitaistruct.ConsistencyError(u"node_name", self.node_name._root, self._root)
            if self.node_name._parent != self:
                raise kaitaistruct.ConsistencyError(u"node_name", self.node_name._parent, self)
            if self.min_constraints._root != self._root:
                raise kaitaistruct.ConsistencyError(u"min_constraints", self.min_constraints._root, self._root)
            if self.min_constraints._parent != self:
                raise kaitaistruct.ConsistencyError(u"min_constraints", self.min_constraints._parent, self)
            if self.max_constraints._root != self._root:
                raise kaitaistruct.ConsistencyError(u"max_constraints", self.max_constraints._root, self._root)
            if self.max_constraints._parent != self:
                raise kaitaistruct.ConsistencyError(u"max_constraints", self.max_constraints._parent, self)


    class Emfx2Actor(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic1 = self._io.read_bytes(4)
            if not (self.magic1 == b"\x67\x65\x6E\x61"):
                raise kaitaistruct.ValidationNotEqualError(b"\x67\x65\x6E\x61", self.magic1, self._io, u"/types/emfx2_actor/seq/0")
            self.version = self._io.read_bytes(2)
            if not (self.version == b"\x04\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x04\x00", self.version, self._io, u"/types/emfx2_actor/seq/1")
            self.size = self._io.read_u4le()
            self.magic2 = self._io.read_bytes(4)
            if not (self.magic2 == b"\x46\x58\x41\x20"):
                raise kaitaistruct.ValidationNotEqualError(b"\x46\x58\x41\x20", self.magic2, self._io, u"/types/emfx2_actor/seq/3")
            self.high_version = self._io.read_bytes(1)
            if not (self.high_version == b"\x01"):
                raise kaitaistruct.ValidationNotEqualError(b"\x01", self.high_version, self._io, u"/types/emfx2_actor/seq/4")
            self.low_version = self._io.read_bytes(1)
            if not (self.low_version == b"\x01"):
                raise kaitaistruct.ValidationNotEqualError(b"\x01", self.low_version, self._io, u"/types/emfx2_actor/seq/5")
            self._raw_chunks = self._io.read_bytes((self.size - 6))
            _io__raw_chunks = KaitaiStream(BytesIO(self._raw_chunks))
            self.chunks = Xact.Chunks(_io__raw_chunks, self, self._root)
            self.chunks._read()
            self.num_materials = self._io.read_u4le()
            self.materials = []
            for i in range(self.num_materials):
                _t_materials = Xact.MaterialReference(self._io, self, self._root)
                _t_materials._read()
                self.materials.append(_t_materials)

            self.reserved = self._io.read_bytes(1)
            if not (self.reserved == b"\x01"):
                raise kaitaistruct.ValidationNotEqualError(b"\x01", self.reserved, self._io, u"/types/emfx2_actor/seq/9")
            self.num_lods = self._io.read_u4le()
            self.ambient_occlusion = []
            for i in range(self.num_lods):
                _t_ambient_occlusion = Xact.AmbientOcclusion(self._io, self, self._root)
                _t_ambient_occlusion._read()
                self.ambient_occlusion.append(_t_ambient_occlusion)

            self._raw_tangent_vertices = []
            self.tangent_vertices = []
            for i in range(self.num_lods):
                self._raw_tangent_vertices.append(self._io.read_bytes((self.ambient_occlusion[i].num_per_lod_vertices * 12)))
                _io__raw_tangent_vertices = KaitaiStream(BytesIO(self._raw_tangent_vertices[-1]))
                _t_tangent_vertices = Xact.TangentVertices(_io__raw_tangent_vertices, self, self._root)
                _t_tangent_vertices._read()
                self.tangent_vertices.append(_t_tangent_vertices)



        def _fetch_instances(self):
            pass
            self.chunks._fetch_instances()
            for i in range(len(self.materials)):
                pass
                self.materials[i]._fetch_instances()

            for i in range(len(self.ambient_occlusion)):
                pass
                self.ambient_occlusion[i]._fetch_instances()

            for i in range(len(self.tangent_vertices)):
                pass
                self.tangent_vertices[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xact.Emfx2Actor, self)._write__seq(io)
            self._io.write_bytes(self.magic1)
            self._io.write_bytes(self.version)
            _pos_size = self._io.pos()
            self.size = 0
            self._io.write_u4le(self.size)
            _pos_data = self._io.pos()
            self._io.write_bytes(self.magic2)
            self._io.write_bytes(self.high_version)
            self._io.write_bytes(self.low_version)
            self.chunks._write__seq(self._io)
            _pos_save = self._io.pos()
            self.size = _pos_save - _pos_data
            self._io.seek(_pos_size)
            self._io.write_u4le(self.size)
            self._io.seek(_pos_save)
            self._io.write_u4le(self.num_materials)
            for i in range(len(self.materials)):
                pass
                self.materials[i]._write__seq(self._io)

            self._io.write_bytes(self.reserved)
            self._io.write_u4le(self.num_lods)
            for i in range(len(self.ambient_occlusion)):
                pass
                self.ambient_occlusion[i]._write__seq(self._io)

            self._raw_tangent_vertices = []
            for i in range(len(self.tangent_vertices)):
                pass
                self.tangent_vertices[i]._write__seq(self._io)



        def _check(self):
            pass
            if not hasattr(self, 'magic1') or self.magic1 is None:
                self.magic1 = b"\x67\x65\x6E\x61"
            if (len(self.magic1) != 4):
                raise kaitaistruct.ConsistencyError(u"magic1", len(self.magic1), 4)
            if not (self.magic1 == b"\x67\x65\x6E\x61"):
                raise kaitaistruct.ValidationNotEqualError(b"\x67\x65\x6E\x61", self.magic1, self._io, u"/types/emfx2_actor/seq/0")
            if not hasattr(self, 'version') or self.version is None:
                self.version = b"\x04\x00"
            if (len(self.version) != 2):
                raise kaitaistruct.ConsistencyError(u"version", len(self.version), 2)
            if not (self.version == b"\x04\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x04\x00", self.version, self._io, u"/types/emfx2_actor/seq/1")
            if not hasattr(self, 'magic2') or self.magic2 is None:
                self.magic2 = b"\x46\x58\x41\x20"
            if (len(self.magic2) != 4):
                raise kaitaistruct.ConsistencyError(u"magic2", len(self.magic2), 4)
            if not (self.magic2 == b"\x46\x58\x41\x20"):
                raise kaitaistruct.ValidationNotEqualError(b"\x46\x58\x41\x20", self.magic2, self._io, u"/types/emfx2_actor/seq/3")
            if not hasattr(self, 'high_version') or self.high_version is None:
                self.high_version = b"\x01"
            if (len(self.high_version) != 1):
                raise kaitaistruct.ConsistencyError(u"high_version", len(self.high_version), 1)
            if not (self.high_version == b"\x01"):
                raise kaitaistruct.ValidationNotEqualError(b"\x01", self.high_version, self._io, u"/types/emfx2_actor/seq/4")
            if not hasattr(self, 'low_version') or self.low_version is None:
                self.low_version = b"\x01"
            if (len(self.low_version) != 1):
                raise kaitaistruct.ConsistencyError(u"low_version", len(self.low_version), 1)
            if not (self.low_version == b"\x01"):
                raise kaitaistruct.ValidationNotEqualError(b"\x01", self.low_version, self._io, u"/types/emfx2_actor/seq/5")
            if self.chunks._root != self._root:
                raise kaitaistruct.ConsistencyError(u"chunks", self.chunks._root, self._root)
            if self.chunks._parent != self:
                raise kaitaistruct.ConsistencyError(u"chunks", self.chunks._parent, self)
            self.num_materials = len(self.materials)
            if (len(self.materials) != self.num_materials):
                raise kaitaistruct.ConsistencyError(u"materials", len(self.materials), self.num_materials)
            for i in range(len(self.materials)):
                pass
                if self.materials[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"materials", self.materials[i]._root, self._root)
                if self.materials[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"materials", self.materials[i]._parent, self)

            if not hasattr(self, 'reserved') or self.reserved is None:
                self.reserved = b"\x01"
            if (len(self.reserved) != 1):
                raise kaitaistruct.ConsistencyError(u"reserved", len(self.reserved), 1)
            if not (self.reserved == b"\x01"):
                raise kaitaistruct.ValidationNotEqualError(b"\x01", self.reserved, self._io, u"/types/emfx2_actor/seq/9")
            self.num_lods = len(self.ambient_occlusion)
            if (len(self.ambient_occlusion) != self.num_lods):
                raise kaitaistruct.ConsistencyError(u"ambient_occlusion", len(self.ambient_occlusion), self.num_lods)
            for i in range(len(self.ambient_occlusion)):
                pass
                if self.ambient_occlusion[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"ambient_occlusion", self.ambient_occlusion[i]._root, self._root)
                if self.ambient_occlusion[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"ambient_occlusion", self.ambient_occlusion[i]._parent, self)

            if (len(self.tangent_vertices) != self.num_lods):
                raise kaitaistruct.ConsistencyError(u"tangent_vertices", len(self.tangent_vertices), self.num_lods)
            for i in range(len(self.tangent_vertices)):
                pass
                if self.tangent_vertices[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"tangent_vertices", self.tangent_vertices[i]._root, self._root)
                if self.tangent_vertices[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"tangent_vertices", self.tangent_vertices[i]._parent, self)



    class Influences(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.num_influences = self._io.read_u1()
            self.influences = []
            for i in range(self.num_influences):
                _t_influences = Xact.SkinInfluence(self._io, self, self._root)
                _t_influences._read()
                self.influences.append(_t_influences)



        def _fetch_instances(self):
            pass
            for i in range(len(self.influences)):
                pass
                self.influences[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xact.Influences, self)._write__seq(io)
            self._io.write_u1(self.num_influences)
            for i in range(len(self.influences)):
                pass
                self.influences[i]._write__seq(self._io)



        def _check(self):
            pass
            self.num_influences = len(self.influences)
            if (len(self.influences) != self.num_influences):
                raise kaitaistruct.ConsistencyError(u"influences", len(self.influences), self.num_influences)
            for i in range(len(self.influences)):
                pass
                if self.influences[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"influences", self.influences[i]._root, self._root)
                if self.influences[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"influences", self.influences[i]._parent, self)



    class AmbientOcclusion(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.reserved = self._io.read_bytes(1)
            if not (self.reserved == b"\x01"):
                raise kaitaistruct.ValidationNotEqualError(b"\x01", self.reserved, self._io, u"/types/ambient_occlusion/seq/0")
            self.num_per_lod_vertices = self._io.read_u4le()
            self.per_lod_vertices = []
            for i in range(self.num_per_lod_vertices):
                self.per_lod_vertices.append(self._io.read_u4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.per_lod_vertices)):
                pass



        def _write__seq(self, io=None):
            super(Xact.AmbientOcclusion, self)._write__seq(io)
            self._io.write_bytes(self.reserved)
            self._io.write_u4le(self.num_per_lod_vertices)
            for i in range(len(self.per_lod_vertices)):
                pass
                self._io.write_u4le(self.per_lod_vertices[i])



        def _check(self):
            pass
            if not hasattr(self, 'reserved') or self.reserved is None:
                self.reserved = b"\x01"
            if (len(self.reserved) != 1):
                raise kaitaistruct.ConsistencyError(u"reserved", len(self.reserved), 1)
            if not (self.reserved == b"\x01"):
                raise kaitaistruct.ValidationNotEqualError(b"\x01", self.reserved, self._io, u"/types/ambient_occlusion/seq/0")
            self.num_per_lod_vertices = len(self.per_lod_vertices)
            if (len(self.per_lod_vertices) != self.num_per_lod_vertices):
                raise kaitaistruct.ConsistencyError(u"per_lod_vertices", len(self.per_lod_vertices), self.num_per_lod_vertices)
            for i in range(len(self.per_lod_vertices)):
                pass



    class Chunks(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.chunks = []
            i = 0
            while not self._io.is_eof():
                _t_chunks = Xact.Chunk(self._io, self, self._root)
                _t_chunks._read()
                self.chunks.append(_t_chunks)
                i += 1



        def _fetch_instances(self):
            pass
            for i in range(len(self.chunks)):
                pass
                self.chunks[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xact.Chunks, self)._write__seq(io)
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

    class Vector(NamedTuple):
        x: float
        y: float
        z: float

    @staticmethod
    def _read_vector(io):
        return Xact.Vector._make(io.read_f4le_x3())

    @staticmethod
    def _write_vector(io, vector: Vector):
        io.write_f4le(vector.x)
        io.write_f4le(vector.y)
        io.write_f4le(vector.z)

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
            super(Xact.String, self)._write__seq(io)
            self._io.write_u2le(self.strtab_index)


        def _check(self):
            pass


    class CnkNode(ReadWriteKaitaiStruct):
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

            self.position = Xact._read_vector(self._io)
            self.rotation = Xact.Quaternion(self._io, self, self._root)
            self.rotation._read()
            self.scale = Xact._read_vector(self._io)
            self.scale_orient = Xact.Quaternion(self._io, self, self._root)
            self.scale_orient._read()
            self.shear = Xact._read_vector(self._io)
            self.name = Xact.LmaString(self._io, self, self._root)
            self.name._read()
            self.parent = Xact.LmaString(self._io, self, self._root)
            self.parent._read()


        def _fetch_instances(self):
            pass
            if (self._parent.version != 3):
                pass

            self.rotation._fetch_instances()
            self.scale_orient._fetch_instances()
            self.name._fetch_instances()
            self.parent._fetch_instances()


        def _write__seq(self, io=None):
            super(Xact.CnkNode, self)._write__seq(io)
            if (self._parent.version != 3):
                pass
                _process_version_guard = ReportWrongVersion()
                self._raw_version_guard = _process_version_guard.encode(self.version_guard)
                if (len(self._raw_version_guard) != 0):
                    raise kaitaistruct.ConsistencyError(u"version_guard", len(self._raw_version_guard), 0)
                self._io.write_bytes(self._raw_version_guard)

            self.position._write__seq(self._io)
            self.rotation._write__seq(self._io)
            self.scale._write__seq(self._io)
            self.scale_orient._write__seq(self._io)
            self.shear._write__seq(self._io)
            self.name._write__seq(self._io)
            self.parent._write__seq(self._io)


        def _check(self):
            pass
            if (self._parent.version != 3):
                pass

            if self.position._root != self._root:
                raise kaitaistruct.ConsistencyError(u"position", self.position._root, self._root)
            if self.position._parent != self:
                raise kaitaistruct.ConsistencyError(u"position", self.position._parent, self)
            if self.rotation._root != self._root:
                raise kaitaistruct.ConsistencyError(u"rotation", self.rotation._root, self._root)
            if self.rotation._parent != self:
                raise kaitaistruct.ConsistencyError(u"rotation", self.rotation._parent, self)
            if self.scale._root != self._root:
                raise kaitaistruct.ConsistencyError(u"scale", self.scale._root, self._root)
            if self.scale._parent != self:
                raise kaitaistruct.ConsistencyError(u"scale", self.scale._parent, self)
            if self.scale_orient._root != self._root:
                raise kaitaistruct.ConsistencyError(u"scale_orient", self.scale_orient._root, self._root)
            if self.scale_orient._parent != self:
                raise kaitaistruct.ConsistencyError(u"scale_orient", self.scale_orient._parent, self)
            if self.shear._root != self._root:
                raise kaitaistruct.ConsistencyError(u"shear", self.shear._root, self._root)
            if self.shear._parent != self:
                raise kaitaistruct.ConsistencyError(u"shear", self.shear._parent, self)
            if self.name._root != self._root:
                raise kaitaistruct.ConsistencyError(u"name", self.name._root, self._root)
            if self.name._parent != self:
                raise kaitaistruct.ConsistencyError(u"name", self.name._parent, self)
            if self.parent._root != self._root:
                raise kaitaistruct.ConsistencyError(u"parent", self.parent._root, self._root)
            if self.parent._parent != self:
                raise kaitaistruct.ConsistencyError(u"parent", self.parent._parent, self)


    class CnkMaterial(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            if (self._parent.version != 5):
                pass
                self._raw_version_guard = self._io.read_bytes(0)
                _process = ReportWrongVersion()
                self.version_guard = _process.decode(self._raw_version_guard)

            self.ambient_color = Xact.FloatColor(self._io, self, self._root)
            self.ambient_color._read()
            self.diffuse_color = Xact.FloatColor(self._io, self, self._root)
            self.diffuse_color._read()
            self.specular_color = Xact.FloatColor(self._io, self, self._root)
            self.specular_color._read()
            self.emissive_color = Xact.FloatColor(self._io, self, self._root)
            self.emissive_color._read()
            self.shine = self._io.read_f4le()
            self.shine_strength = self._io.read_f4le()
            self.opacity = self._io.read_f4le()
            self.ior = self._io.read_f4le()
            self.double_sided = self._io.read_u1()
            self.wire_frame = self._io.read_u1()
            self.transparency_type = (self._io.read_bytes(1)).decode("windows-1252")
            self.padding = self._io.read_bytes(1)
            self.material_name = Xact.LmaString(self._io, self, self._root)
            self.material_name._read()
            self.shader_file_name = Xact.LmaString(self._io, self, self._root)
            self.shader_file_name._read()


        def _fetch_instances(self):
            pass
            if (self._parent.version != 5):
                pass

            self.ambient_color._fetch_instances()
            self.diffuse_color._fetch_instances()
            self.specular_color._fetch_instances()
            self.emissive_color._fetch_instances()
            self.material_name._fetch_instances()
            self.shader_file_name._fetch_instances()


        def _write__seq(self, io=None):
            super(Xact.CnkMaterial, self)._write__seq(io)
            if (self._parent.version != 5):
                pass
                _process_version_guard = ReportWrongVersion()
                self._raw_version_guard = _process_version_guard.encode(self.version_guard)
                if (len(self._raw_version_guard) != 0):
                    raise kaitaistruct.ConsistencyError(u"version_guard", len(self._raw_version_guard), 0)
                self._io.write_bytes(self._raw_version_guard)

            self.ambient_color._write__seq(self._io)
            self.diffuse_color._write__seq(self._io)
            self.specular_color._write__seq(self._io)
            self.emissive_color._write__seq(self._io)
            self._io.write_f4le(self.shine)
            self._io.write_f4le(self.shine_strength)
            self._io.write_f4le(self.opacity)
            self._io.write_f4le(self.ior)
            self._io.write_u1(self.double_sided)
            self._io.write_u1(self.wire_frame)
            self._io.write_bytes((self.transparency_type).encode(u"windows-1252"))
            self._io.write_bytes(self.padding)
            self.material_name._write__seq(self._io)
            self.shader_file_name._write__seq(self._io)


        def _check(self):
            pass
            if (self._parent.version != 5):
                pass

            if self.ambient_color._root != self._root:
                raise kaitaistruct.ConsistencyError(u"ambient_color", self.ambient_color._root, self._root)
            if self.ambient_color._parent != self:
                raise kaitaistruct.ConsistencyError(u"ambient_color", self.ambient_color._parent, self)
            if self.diffuse_color._root != self._root:
                raise kaitaistruct.ConsistencyError(u"diffuse_color", self.diffuse_color._root, self._root)
            if self.diffuse_color._parent != self:
                raise kaitaistruct.ConsistencyError(u"diffuse_color", self.diffuse_color._parent, self)
            if self.specular_color._root != self._root:
                raise kaitaistruct.ConsistencyError(u"specular_color", self.specular_color._root, self._root)
            if self.specular_color._parent != self:
                raise kaitaistruct.ConsistencyError(u"specular_color", self.specular_color._parent, self)
            if self.emissive_color._root != self._root:
                raise kaitaistruct.ConsistencyError(u"emissive_color", self.emissive_color._root, self._root)
            if self.emissive_color._parent != self:
                raise kaitaistruct.ConsistencyError(u"emissive_color", self.emissive_color._parent, self)
            if (len((self.transparency_type).encode(u"windows-1252")) != 1):
                raise kaitaistruct.ConsistencyError(u"transparency_type", len((self.transparency_type).encode(u"windows-1252")), 1)
            if (len(self.padding) != 1):
                raise kaitaistruct.ConsistencyError(u"padding", len(self.padding), 1)
            if self.material_name._root != self._root:
                raise kaitaistruct.ConsistencyError(u"material_name", self.material_name._root, self._root)
            if self.material_name._parent != self:
                raise kaitaistruct.ConsistencyError(u"material_name", self.material_name._parent, self)
            if self.shader_file_name._root != self._root:
                raise kaitaistruct.ConsistencyError(u"shader_file_name", self.shader_file_name._root, self._root)
            if self.shader_file_name._parent != self:
                raise kaitaistruct.ConsistencyError(u"shader_file_name", self.shader_file_name._parent, self)


    class MaterialReference(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.lod_index = self._io.read_u2le()
            self.mat_index = self._io.read_u2le()
            self.name = Xact.String(self._io, self, self._root)
            self.name._read()


        def _fetch_instances(self):
            pass
            self.name._fetch_instances()


        def _write__seq(self, io=None):
            super(Xact.MaterialReference, self)._write__seq(io)
            self._io.write_u2le(self.lod_index)
            self._io.write_u2le(self.mat_index)
            self.name._write__seq(self._io)


        def _check(self):
            pass
            if self.name._root != self._root:
                raise kaitaistruct.ConsistencyError(u"name", self.name._root, self._root)
            if self.name._parent != self:
                raise kaitaistruct.ConsistencyError(u"name", self.name._parent, self)


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
            super(Xact.LmaString, self)._write__seq(io)
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
            super(Xact.Quaternion, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            pass


    class CnkMesh(ReadWriteKaitaiStruct):
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

            self.node_number = self._io.read_u4le()
            self.num_org_verts = self._io.read_u4le()
            self.total_verts = self._io.read_u4le()
            self.total_indices = self._io.read_u4le()
            self.num_submeshes = self._io.read_u4le()
            self.num_uv_sets = self._io.read_u4le()
            self.is_collision_mesh = self._io.read_u1()
            self.padding = self._io.read_bytes(3)
            self.submeshes = []
            for i in range(self.num_submeshes):
                _t_submeshes = Xact.Submesh(self._io, self, self._root)
                _t_submeshes._read()
                self.submeshes.append(_t_submeshes)



        def _fetch_instances(self):
            pass
            if (self._parent.version != 3):
                pass

            for i in range(len(self.submeshes)):
                pass
                self.submeshes[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xact.CnkMesh, self)._write__seq(io)
            if (self._parent.version != 3):
                pass
                _process_version_guard = ReportWrongVersion()
                self._raw_version_guard = _process_version_guard.encode(self.version_guard)
                if (len(self._raw_version_guard) != 0):
                    raise kaitaistruct.ConsistencyError(u"version_guard", len(self._raw_version_guard), 0)
                self._io.write_bytes(self._raw_version_guard)

            self._io.write_u4le(self.node_number)
            self._io.write_u4le(self.num_org_verts)
            self._io.write_u4le(self.total_verts)
            self._io.write_u4le(self.total_indices)
            self._io.write_u4le(self.num_submeshes)
            self._io.write_u4le(self.num_uv_sets)
            self._io.write_u1(self.is_collision_mesh)
            self._io.write_bytes(self.padding)
            for i in range(len(self.submeshes)):
                pass
                self.submeshes[i]._write__seq(self._io)



        def _check(self):
            pass
            if (self._parent.version != 3):
                pass

            if (len(self.padding) != 3):
                raise kaitaistruct.ConsistencyError(u"padding", len(self.padding), 3)
            self.num_submeshes = len(self.submeshes)
            if (len(self.submeshes) != self.num_submeshes):
                raise kaitaistruct.ConsistencyError(u"submeshes", len(self.submeshes), self.num_submeshes)
            for i in range(len(self.submeshes)):
                pass
                if self.submeshes[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"submeshes", self.submeshes[i]._root, self._root)
                if self.submeshes[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"submeshes", self.submeshes[i]._parent, self)



    class SkinInfluence(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.node_index = self._io.read_u2le()
            self.padding = self._io.read_bytes(2)
            self.weight = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Xact.SkinInfluence, self)._write__seq(io)
            self._io.write_u2le(self.node_index)
            self._io.write_bytes(self.padding)
            self._io.write_f4le(self.weight)


        def _check(self):
            pass
            if (len(self.padding) != 2):
                raise kaitaistruct.ConsistencyError(u"padding", len(self.padding), 2)


    class Submesh(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.mat_id = self._io.read_u1()
            self.num_uv_sets = self._io.read_u1()
            self.padding = self._io.read_bytes(2)
            self.num_indices = self._io.read_u4le()
            self.num_verts = self._io.read_u4le()
            self.vertices = []
            for i in range(self.num_verts):
                _t_vertices = Xact.Vertex(self._io, self, self._root)
                _t_vertices._read()
                self.vertices.append(_t_vertices)

            self.indices = []
            for i in range(self.num_indices):
                self.indices.append(self._io.read_u4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.vertices)):
                pass
                self.vertices[i]._fetch_instances()

            for i in range(len(self.indices)):
                pass



        def _write__seq(self, io=None):
            super(Xact.Submesh, self)._write__seq(io)
            self._io.write_u1(self.mat_id)
            self._io.write_u1(self.num_uv_sets)
            self._io.write_bytes(self.padding)
            self._io.write_u4le(self.num_indices)
            self._io.write_u4le(self.num_verts)
            for i in range(len(self.vertices)):
                pass
                self.vertices[i]._write__seq(self._io)

            for i in range(len(self.indices)):
                pass
                self._io.write_u4le(self.indices[i])



        def _check(self):
            pass
            if (len(self.padding) != 2):
                raise kaitaistruct.ConsistencyError(u"padding", len(self.padding), 2)
            self.num_verts = len(self.vertices)
            if (len(self.vertices) != self.num_verts):
                raise kaitaistruct.ConsistencyError(u"vertices", len(self.vertices), self.num_verts)
            for i in range(len(self.vertices)):
                pass
                if self.vertices[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._root, self._root)
                if self.vertices[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"vertices", self.vertices[i]._parent, self)

            self.num_indices = len(self.indices)
            if (len(self.indices) != self.num_indices):
                raise kaitaistruct.ConsistencyError(u"indices", len(self.indices), self.num_indices)
            for i in range(len(self.indices)):
                pass


        @property
        def override_num_uv_sets(self):
            if hasattr(self, '_m_override_num_uv_sets'):
                return self._m_override_num_uv_sets

            self._m_override_num_uv_sets = self._parent.num_uv_sets
            return getattr(self, '_m_override_num_uv_sets', None)

        def _invalidate_override_num_uv_sets(self):
            del self._m_override_num_uv_sets


