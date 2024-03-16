from dataclasses import dataclass

from ..binary_serialize import BinarySerializable


@dataclass(slots=True)
class bCQuaternion(BinarySerializable):
    x: float = None
    y: float = None
    z: float = None
    w: float = None

    def read(self, reader: 'BinaryReader') -> None:
        self.x = reader.read_float()
        self.y = reader.read_float()
        self.z = reader.read_float()
        self.w = reader.read_float()

    def write(self, writer: 'BinaryWriter') -> None:
        writer.write_float(self.x)
        writer.write_float(self.y)
        writer.write_float(self.z)
        writer.write_float(self.w)


@dataclass(slots=True)
class bCVector(BinarySerializable):
    x: float = None
    y: float = None
    z: float = None

    def read(self, reader: 'BinaryReader') -> None:
        self.x = reader.read_float()
        self.y = reader.read_float()
        self.z = reader.read_float()

    def write(self, writer: 'BinaryWriter') -> None:
        writer.write_float(self.x)
        writer.write_float(self.y)
        writer.write_float(self.z)


@dataclass(slots=True)
class bCVector2(BinarySerializable):
    x: float = None
    y: float = None

    def read(self, reader: 'BinaryReader') -> None:
        self.x = reader.read_float()
        self.y = reader.read_float()

    def write(self, writer: 'BinaryWriter') -> None:
        writer.write_float(self.x)
        writer.write_float(self.y)


@dataclass(slots=True)
class bCBox(BinarySerializable):
    min: bCVector = None
    max: bCVector = None

    def read(self, reader: 'BinaryReader') -> None:
        self.min = reader.read_vec3()
        self.max = reader.read_vec3()

    def write(self, writer: 'BinaryWriter') -> None:
        writer.write_vec3(self.min)
        writer.write_vec3(self.max)
