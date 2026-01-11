from typing import ClassVar, TypeVar


TPropertyType = TypeVar('TPropertyType', bound='BinarySerializable')  # noqa: F821 Avoid circular import


class PropertyTypeRegistry:
    property_types: ClassVar[dict[str, type[TPropertyType]]] = {}

    @classmethod
    def is_property_container(cls, type_name: str) -> bool:
        return type_name.startswith('bTPropertyContainer<enum')

    @classmethod
    def register(cls, property_type: type[TPropertyType], type_name: str) -> None:
        assert type_name not in cls.property_types
        cls.property_types[type_name] = property_type

    @classmethod
    def instantiate(cls, name: str, type_name: str) -> TPropertyType:
        if type_name not in cls.property_types:
            if cls.is_property_container(type_name):
                from .property_container import bTPropertyContainer  # noqa: PLC0415 Avoid circular import

                property_type = bTPropertyContainer
            else:
                raise ValueError(f'Unknown Property: {name} - {type_name}')
        else:
            property_type = cls.property_types[type_name]
        return property_type.__new__(property_type)
