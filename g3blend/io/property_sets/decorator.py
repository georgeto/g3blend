from typing import Optional

from .registry import PropertySetRegistry


def _process_class(cls, aliases: Optional[list[str]]):
    PropertySetRegistry.register(cls, cls.__name__)
    if aliases:
        for alias in aliases:
            PropertySetRegistry.register(cls, alias)
    return cls


def property_set(cls=None, /, *, aliases: Optional[list[str]] = None):
    """Register in data type registry."""

    def wrap(cls):
        return _process_class(cls, aliases)

    # See if we're being called as @property_set or @property_set().
    if cls is None:
        # We're called with parens.
        return wrap

    # We're called as @property_set without parens.
    return wrap(cls)
