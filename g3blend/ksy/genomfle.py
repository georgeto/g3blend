# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

from . import kaitaistruct
from .kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Genomfle(ReadWriteKaitaiStruct):
    """Gothic 3 common structures
    """
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._should_write_tail = False
        self.tail__to_write = True

    def _read(self):
        self.header = Genomfle.GenomfleHeader(self._io, self, self._root)
        self.header._read()


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        _ = self.tail
        self.tail._fetch_instances()


    def _write__seq(self, io=None):
        super(Genomfle, self)._write__seq(io)
        self._should_write_tail = self.tail__to_write
        self.header._write__seq(self._io)


    def _check(self):
        pass
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self.header._root, self._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self.header._parent, self)

    class GenomfleHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic = self._io.read_bytes(8)
            if not (self.magic == b"\x47\x45\x4E\x4F\x4D\x46\x4C\x45"):
                raise kaitaistruct.ValidationNotEqualError(b"\x47\x45\x4E\x4F\x4D\x46\x4C\x45", self.magic, self._io, u"/types/genomfle_header/seq/0")
            self.version = self._io.read_u2le()
            self.tail_offset = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Genomfle.GenomfleHeader, self)._write__seq(io)
            self._io.write_bytes(self.magic)
            self._io.write_u2le(self.version)
            self._io.write_u4le(self.tail_offset)


        def _check(self):
            pass
            if not hasattr(self, 'magic') or self.magic is None:
                self.magic = b"\x47\x45\x4E\x4F\x4D\x46\x4C\x45"
            if (len(self.magic) != 8):
                raise kaitaistruct.ConsistencyError(u"magic", len(self.magic), 8)
            if not (self.magic == b"\x47\x45\x4E\x4F\x4D\x46\x4C\x45"):
                raise kaitaistruct.ValidationNotEqualError(b"\x47\x45\x4E\x4F\x4D\x46\x4C\x45", self.magic, self._io, u"/types/genomfle_header/seq/0")


    class GenomfleTail(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.deadbeef = self._io.read_bytes(4)
            if not (self.deadbeef == b"\xEF\xBE\xAD\xDE"):
                raise kaitaistruct.ValidationNotEqualError(b"\xEF\xBE\xAD\xDE", self.deadbeef, self._io, u"/types/genomfle_tail/seq/0")
            self.strtbl_present = self._io.read_u1()
            if (self.strtbl_present == 1):
                pass
                self.num_strtbl_entries = self._io.read_u4le()

            if (self.strtbl_present == 1):
                pass
                self.strtbl_entries = []
                for i in range(self.num_strtbl_entries):
                    _t_strtbl_entries = Genomfle.GenomfleStr(self._io, self, self._root)
                    _t_strtbl_entries._read()
                    self.strtbl_entries.append(_t_strtbl_entries)




        def _fetch_instances(self):
            pass
            if (self.strtbl_present == 1):
                pass

            if (self.strtbl_present == 1):
                pass
                for i in range(len(self.strtbl_entries)):
                    pass
                    self.strtbl_entries[i]._fetch_instances()




        def _write__seq(self, io=None):
            super(Genomfle.GenomfleTail, self)._write__seq(io)
            self._io.write_bytes(self.deadbeef)
            self._io.write_u1(self.strtbl_present)
            if (self.strtbl_present == 1):
                pass
                self._io.write_u4le(self.num_strtbl_entries)

            if (self.strtbl_present == 1):
                pass
                for i in range(len(self.strtbl_entries)):
                    pass
                    self.strtbl_entries[i]._write__seq(self._io)




        def _check(self):
            pass
            if not hasattr(self, 'deadbeef') or self.deadbeef is None:
                self.deadbeef = b"\xEF\xBE\xAD\xDE"
            if (len(self.deadbeef) != 4):
                raise kaitaistruct.ConsistencyError(u"deadbeef", len(self.deadbeef), 4)
            if not (self.deadbeef == b"\xEF\xBE\xAD\xDE"):
                raise kaitaistruct.ValidationNotEqualError(b"\xEF\xBE\xAD\xDE", self.deadbeef, self._io, u"/types/genomfle_tail/seq/0")
            if (self.strtbl_present == 1):
                pass

            if (self.strtbl_present == 1):
                pass
                self.num_strtbl_entries = len(self.strtbl_entries)
                if (len(self.strtbl_entries) != self.num_strtbl_entries):
                    raise kaitaistruct.ConsistencyError(u"strtbl_entries", len(self.strtbl_entries), self.num_strtbl_entries)
                for i in range(len(self.strtbl_entries)):
                    pass
                    if self.strtbl_entries[i]._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"strtbl_entries", self.strtbl_entries[i]._root, self._root)
                    if self.strtbl_entries[i]._parent != self:
                        raise kaitaistruct.ConsistencyError(u"strtbl_entries", self.strtbl_entries[i]._parent, self)




    class GenomfleStr(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.len = self._io.read_u2le()
            self.data = (self._io.read_bytes(self.len)).decode("windows-1252")


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Genomfle.GenomfleStr, self)._write__seq(io)
            self._io.write_u2le(self.len)
            self._io.write_bytes((self.data).encode(u"windows-1252"))


        def _check(self):
            pass
            self.len = len((self.data).encode(u"windows-1252"))
            if (len((self.data).encode(u"windows-1252")) != self.len):
                raise kaitaistruct.ConsistencyError(u"data", len((self.data).encode(u"windows-1252")), self.len)


    @property
    def tail(self):
        if self._should_write_tail:
            self._write_tail()
        if hasattr(self, '_m_tail'):
            return self._m_tail

        _pos = self._io.pos()
        self._io.seek(self.header.tail_offset)
        self._m_tail = Genomfle.GenomfleTail(self._io, self, self._root)
        self._m_tail._read()
        self._io.seek(_pos)
        return getattr(self, '_m_tail', None)

    @tail.setter
    def tail(self, v):
        self._m_tail = v

    def _write_tail(self):
        self._should_write_tail = False
        _pos = self._io.pos()
        self._io.seek(self.header.tail_offset)
        self.tail._write__seq(self._io)
        self._io.seek(_pos)


    def _check_tail(self):
        pass
        if self.tail._root != self._root:
            raise kaitaistruct.ConsistencyError(u"tail", self.tail._root, self._root)
        if self.tail._parent != self:
            raise kaitaistruct.ConsistencyError(u"tail", self.tail._parent, self)

    @property
    def content_size(self):
        if hasattr(self, '_m_content_size'):
            return self._m_content_size

        self._m_content_size = (self.header.tail_offset - self._io.pos())
        return getattr(self, '_m_content_size', None)

    def _invalidate_content_size(self):
        del self._m_content_size
