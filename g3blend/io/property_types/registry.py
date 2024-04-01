from typing import Type, TypeVar

TPropertyType = TypeVar('TPropertyType', bound='BinarySerializable')


class PropertyTypeRegistry:
    property_types: dict[str, Type[TPropertyType]] = {}

    @classmethod
    def register(cls, property_type: Type[TPropertyType], type_name: str) -> None:
        assert type_name not in cls.property_types
        cls.property_types[type_name] = property_type

    @classmethod
    def instantiate(cls, name: str, type_name: str) -> TPropertyType:
        if type_name not in cls.property_types:
            raise ValueError(f'Unknown Property: {name} - {type_name}')
        else:
            property_type = cls.property_types[type_name]
        return property_type.__new__(property_type)
