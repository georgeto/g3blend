import struct

from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Type, TypeVar


class BinarySerializable(ABC):
    @abstractmethod
    def read(self, reader: 'BinaryReader') -> None:
        pass

    def read_sized(self, reader: 'BinaryReader', size: int) -> None:
        self.read(reader)

    @abstractmethod
    def write(self, writer: 'BinaryWriter') -> None:
        pass


TBinarySerializable = TypeVar('TBinarySerializable', bound=BinarySerializable)

T = TypeVar('T')
_ENCODING = 'windows-1252'


class BinaryReader:
    _buf: bytes | bytearray
    _pos: int
    _stringtable: Optional[list[str]]

    def __init__(self, data: bytes | bytearray | Path):
        if isinstance(data, Path):
            self._buf = data.read_bytes()
        else:
            self._buf = data
        self._pos = 0
        self._stringtable = None

    def position(self) -> int:
        return self._pos

    def seek(self, pos: int) -> None:
        self._pos = pos

    def skip(self, num: int) -> None:
        self._pos += num

    def size(self) -> int:
        return len(self._buf)

    def remaining(self) -> int:
        return len(self._buf) - self._pos

    def read_bytes(self, num: int) -> bytes:
        pos = self._pos
        self._pos += num
        return self._buf[pos : pos + num]

    def expect_bytes(self, expected: bytes) -> bool:
        if self.remaining() < len(expected):
            return False

        if not self.read_bytes(len(expected)) == expected:
            self.skip(-len(expected))
            return False

        return True

    def peek_bytes(self, num: int, offset: int = 0) -> bytes:
        at = self._pos + offset
        return self._buf[at : at + num]

    def read_bool(self) -> bool:
        return self.read_u8() & 0xFF == 1

    def read_char(self) -> bytes:
        return self._unpack_single('<c', 1)

    def read_u8(self) -> int:
        return self._unpack_single('<B', 1)

    def read_u16(self) -> int:
        return self._unpack_single('<H', 2)

    def read_u32(self) -> int:
        return self._unpack_single('<I', 4)

    def read_u64(self) -> int:
        return self._unpack_single('<Q', 8)

    def read_i8(self) -> int:
        return self._unpack_single('<b', 1)

    def read_i16(self) -> int:
        return self._unpack_single('<h', 2)

    def read_i32(self) -> int:
        return self._unpack_single('<i', 4)

    def read_i64(self) -> int:
        return self._unpack_single('<q', 8)

    def read_float(self) -> float:
        return self._unpack_single('<f', 4)

    def read_str(self, length: int) -> str:
        return self.read_bytes(length).decode(_ENCODING)

    def read_str_u16(self) -> str:
        return self.read_str(self.read_u16())

    def read_str_u32(self) -> str:
        return self.read_str(self.read_u32())

    def read_vec2(self) -> 'bCVector2':
        return bCVector2(*self._unpack('<ff', 8))

    def read_vec3(self) -> 'bCVector':
        return bCVector(*self._unpack('<fff', 12))

    def read_vec4(self) -> 'bCVector4':
        return bCVector4(*self._unpack('<ffff', 16))

    def read_quat(self) -> 'bCQuaternion':
        return bCQuaternion(*self._unpack('<ffff', 16))

    def read_guid(self) -> bytes:
        return self.read_bytes(20)

    def read(self, class_type: Type[TBinarySerializable], size: int = None) -> TBinarySerializable:
        value = class_type.__new__(class_type)
        if size is not None:
            value.read_sized(self, size)
        else:
            value.read(self)
        return value

    def read_list(
        self, typ: Type[TBinarySerializable] = None, read: Callable[['BinaryReader'], T] = None, num: int = None
    ) -> list[TBinarySerializable] | list[T]:
        if num is None:
            num = self.read_u32()

        if typ is not None:
            return [self.read(typ) for _ in range(num)]
        elif read is not None:
            return [read(self) for _ in range(num)]
        else:
            raise ValueError()

    def read_prefixed_list(
        self, typ: Type[TBinarySerializable] = None, read: Callable[['BinaryReader'], T] = None, num: int = None
    ) -> list[TBinarySerializable] | list[T]:
        # bTArray writes a useless byte during serialization.
        self.skip(1)
        return self.read_list(typ, read, num)

    def read_entry(self) -> str:
        if self._stringtable is None:
            return self.read_str_u16()
            # raise ValueError('Attempted to read entry from reader without stringtable.')

        return self._stringtable[self.read_u16()]

    def read_stringtable(self) -> None:
        self._stringtable = []
        # Stringtable enabled?
        if self.read_bool():
            for i in range(self.read_u32()):
                self._stringtable.append(self.read_str(self.read_u16()))

    @contextmanager
    def at_position(self, pos: int):
        save_pos = self.position()
        self.seek(pos)
        yield
        self.seek(save_pos)

    def _unpack(self, fmt: str, num: int) -> Any:
        assert num == struct.calcsize(fmt)

        pos = self._pos
        self._pos += num
        return struct.unpack_from(fmt, self._buf, pos)

    def _unpack_single(self, fmt: str, num: int) -> Any:
        return self._unpack(fmt, num)[0]

    def __str__(self) -> str:
        pos = self.position()
        num_left = pos - max(0, pos - 10)
        num_right = min(self.size(), pos + 10) - pos
        left = self.peek_bytes(num_left, -num_left) if num_left > 0 else b''
        current = self.peek_bytes(1, 0) if num_right > 0 else b''
        right = self.peek_bytes(num_right - 1, 1) if num_right > 1 else b''
        return f'@{pos:#08x}: {left.hex()} [{current.hex()}] {right.hex()}'

    def __repr__(self) -> str:
        return str(self)


class BinaryWriter:
    _buf: bytearray
    _pos: int
    _stringtable: dict[str, int]

    def __init__(self):
        self._buf = bytearray()
        self._pos = 0
        self._stringtable = {}

    def buf(self) -> bytearray:
        return self._buf

    def position(self) -> int:
        return self._pos

    def seek(self, pos: int) -> None:
        self._pos = pos

    def skip(self, num: int) -> None:
        self._pos += num

    def size(self) -> int:
        return len(self._buf)

    def write_bytes(self, val: bytes):
        pos = self._pos
        self._pos += len(val)

        if pos == len(self._buf):
            self._buf.extend(val)
        else:
            self._buf[pos : pos + len(val)] = val

    def write_bool(self, val: bool) -> None:
        self.write_u8(1 if val else 0)

    def write_char(self, val: bytes) -> None:
        self._pack('<c', 1, val)

    def write_u8(self, val: int) -> None:
        self._pack('<B', 1, val)

    def write_u16(self, val: int) -> None:
        self._pack('<H', 2, val)

    def write_u32(self, val: int) -> None:
        self._pack('<I', 4, val)

    def write_u64(self, val: int) -> None:
        self._pack('<Q', 8, val)

    def write_i8(self, val: int) -> None:
        self._pack('<b', 1, val)

    def write_i16(self, val: int) -> None:
        self._pack('<h', 2, val)

    def write_i32(self, val: int) -> None:
        self._pack('<i', 4, val)

    def write_i64(self, val: int) -> None:
        self._pack('<q', 8, val)

    def write_float(self, val: float) -> None:
        self._pack('<f', 4, val)

    def write_str_u16(self, val: str) -> None:
        val_bytes = val.encode(_ENCODING)
        self.write_u16(len(val_bytes))
        self.write_bytes(val_bytes)

    def write_str_u32(self, val: str) -> None:
        val_bytes = val.encode(_ENCODING)
        self.write_u32(len(val_bytes))
        self.write_bytes(val_bytes)

    def write_vec2(self, val: 'bCVector2') -> None:
        return self._pack('<ff', 8, val.x, val.y)

    def write_vec3(self, val: 'bCVector') -> None:
        return self._pack('<fff', 12, val.x, val.y, val.z)

    def write_vec4(self, val: 'bCVector4') -> None:
        return self._pack('<ffff', 16, val.x, val.y, val.z, val.w)

    def write_quat(self, val: 'bCQuaternion') -> None:
        return self._pack('<ffff', 16, val.x, val.y, val.z, val.w)

    def write(self, value: TBinarySerializable) -> None:
        value.write(self)

    def write_iter(
        self, vals: Iterable[TBinarySerializable] | Iterable[T], write: Callable[['BinaryWriter', T], None] = None
    ) -> None:
        for val in vals:
            if write is not None:
                write(self, val)
            else:
                self.write(val)

    def write_list(self, vals: list[TBinarySerializable] | list[T], write: Callable[['BinaryWriter', T], None] = None):
        self.write_u32(len(vals))
        self.write_iter(vals, write)

    def write_prefixed_list(
        self, vals: list[TBinarySerializable] | list[T], write: Callable[['BinaryWriter', T], None] = None
    ):
        # bTArray writes a useless byte during serialization.
        self.write_u8(1)
        self.write_list(vals, write)

    def write_entry(self, val: str) -> None:
        index = self._stringtable.get(val)
        if index is None:
            index = len(self._stringtable)
            self._stringtable[val] = index
        self.write_u16(index)

    def write_stringtable(self) -> None:
        if self._stringtable is None:
            self.write_bool(False)
            return

        self.write_bool(True)
        self.write_u32(len(self._stringtable))
        for entry in self._stringtable.keys():
            self.write_str_u16(entry)

    @contextmanager
    def at_position(self, pos: int):
        save_pos = self.position()
        self.seek(pos)
        yield save_pos
        self.seek(save_pos)

    def _pack(self, fmt: str, num: int, *args) -> None:
        assert num == struct.calcsize(fmt)
        self.write_bytes(struct.pack(fmt, *args))

    def peek_bytes(self, num: int, offset: int = 0) -> bytes:
        at = self._pos + offset
        return self._buf[at : at + num]

    def __str__(self) -> str:
        pos = self.position()
        num_left = pos - max(0, pos - 10)
        num_right = min(self.size(), pos + 10) - pos
        left = self.peek_bytes(num_left, -num_left) if num_left > 0 else b''
        current = self.peek_bytes(1, 0) if num_right > 0 else b''
        right = self.peek_bytes(num_right - 1, 1) if num_right > 1 else b''
        return f'@{pos:#08x}: {left.hex()} [{current.hex()}] {right.hex()}'

    def __repr__(self) -> str:
        return str(self)


from .property_types import bCVector, bCVector2
from .types import bCQuaternion, bCVector4
