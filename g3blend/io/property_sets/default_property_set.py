from dataclasses import dataclass
from typing import Optional

from .property_set import PropertySet
from ..binary import BinaryReader, BinaryWriter
from ... import log as logging

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DefaultPropertySet(PropertySet):
    raw: Optional[bytes]

    def read_post_version(self, reader: BinaryReader) -> None:
        if reader.position() < self._deadcode_position:
            logger.warning(f"{self.name} is handled by DefaultPropertySet but contains Subclass(es) - Size: "
                           f"{self._deadcode_position - 4 - reader.position()}")
            self.raw = reader.read_bytes(self._deadcode_position - reader.position())

    def write_post_version(self, writer: BinaryWriter) -> None:
        if self.raw is not None:
            writer.write_bytes(self.raw)
