from typing import ClassVar, TypeVar

from .default_property_set import DefaultPropertySet
from .property_set import PropertySet


TPropertySet = TypeVar('TPropertySet', bound=PropertySet)


class PropertySetRegistry:
    property_types: ClassVar[dict[str, type[TPropertySet]]] = {}

    @classmethod
    def register(cls, property_type: type[TPropertySet], type_name: str) -> None:
        assert type_name not in cls.property_types
        cls.property_types[type_name] = property_type

    @classmethod
    def instantiate(cls, name: str) -> TPropertySet:
        property_set = cls.property_types.get(name, DefaultPropertySet)
        return property_set.__new__(property_set)
