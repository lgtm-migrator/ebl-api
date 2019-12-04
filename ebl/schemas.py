from abc import ABC, abstractmethod
from enum import Enum
from typing import Type, Optional, Any, List

from marshmallow import fields


class EnumField(fields.String, ABC):
    default_error_messages = {
        "invalid_value": "Invalid value.",
        "not_enum": "Not a valid Enum.",
    }

    def __init__(self, enum_class: Type[Enum], **kwargs):
        self._enum_class = enum_class
        super().__init__(enum=self._values(), **kwargs)

    def _serialize(self, value, attr, obj, **kwargs) -> Optional[str]:
        if isinstance(value, Enum):
            return super()._serialize(
                (self._serialize_enum(value) if value is not None else None),
                attr,
                obj,
                **kwargs
            )
        else:
            raise self.make_error("not_enum")

    def _deserialize(self, value, attr, data, **kwargs) -> Any:
        try:
            return self._deserialize_enum(
                super()._deserialize(value, attr, data, **kwargs)
            )
        except (KeyError, ValueError) as error:
            raise self.make_error("invalid_value") from error

    @abstractmethod
    def _serialize_enum(self, value: Enum) -> str:
        ...

    @abstractmethod
    def _deserialize_enum(self, value: str) -> Enum:
        ...

    @abstractmethod
    def _values(self) -> List[str]:
        ...


class ValueEnum(EnumField):
    def _serialize_enum(self, value: Enum) -> str:
        return value.value

    def _deserialize_enum(self, value: str) -> Enum:
        return self._enum_class(value)

    def _values(self) -> List[str]:
        return [e.value for e in self._enum_class]


class NameEnum(EnumField):
    def _serialize_enum(self, value: Enum) -> str:
        return value.name

    def _deserialize_enum(self, value: str) -> Enum:
        return self._enum_class[value]

    def _values(self) -> List[str]:
        return [e.name for e in self._enum_class]