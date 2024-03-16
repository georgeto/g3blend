from dataclasses import dataclass

from ..binary import BinaryReader, BinarySerializable, BinaryWriter


class FloatColor(BinarySerializable):
    red: float
    green: float
    blue: float

    def read(self, reader: BinaryReader) -> None:
        self.red = reader.read_float()
        self.green = reader.read_float()
        self.blue = reader.read_float()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_float(self.red)
        writer.write_float(self.green)
        writer.write_float(self.blue)


@dataclass(slots=True)
class bCDateTime(BinarySerializable):
    file_time: int = None

    def read(self, reader: BinaryReader) -> None:
        self.file_time = reader.read_u64()

    def write(self, writer: BinaryWriter) -> None:
        writer.write_u64(self.file_time)

    # private static final Instant FILETIME_ZERO = Instant.parse("1601-01-01T00:00:00Z");

    # public static bCDateTime fromInstant(Instant instant)
    #	Duration duration = Duration.between(FILETIME_ZERO, instant);
    #	return new bCDateTime(duration.getSeconds() * 10_000_000 + duration.getNano() / 100);

    # public Instant toInstant()
    #	Duration duration = Duration.of(fileTime / 10, ChronoUnit.MICROS).plus(fileTime % 10 * 100, ChronoUnit.NANOS);
    #	return FILETIME_ZERO.plus(duration);
