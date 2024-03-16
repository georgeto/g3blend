from abc import ABC, abstractmethod


class BinarySerializable(ABC):
    @abstractmethod
    def read(self, reader: 'BinaryReader') -> None:
        pass

    def read_sized(self, reader: 'BinaryReader', size: int) -> None:
        self.read(reader)

    @abstractmethod
    def write(self, writer: 'BinaryWriter') -> None:
        pass
