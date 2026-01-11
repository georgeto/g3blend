from .. import log as logging
from ..io.animation.xact import ResourceAnimationActor as Xact
from ..io.property_types.date_time import bCDateTime


logger = logging.getLogger(__name__)


def save_xact():
    xact = Xact()
    xact.resource_size = 0
    xact.resource_priority = 0.0
    xact.native_file_time = bCDateTime(0)  # TODO?
    xact.native_file_size = 0
    # TODO: Calculate...
    # xact.boundary =
    raise NotImplementedError('Xact export not yet implemented')
