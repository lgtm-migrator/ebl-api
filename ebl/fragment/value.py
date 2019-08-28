from abc import ABC, abstractmethod
from typing import Mapping, Optional, Sequence, Tuple, Union

import attr

from ebl.text.atf import UNIDENTIFIED_SIGN, VARIANT_SEPARATOR

INVALID_READING = '?'


ReadingKey = Tuple[str, Optional[int]]
SignMap = Mapping[ReadingKey, str]


@attr.s(frozen=True)
class Value(ABC):

    @abstractmethod
    def to_sign(self, sign_map: SignMap) -> str:
        ...

    @property
    def keys(self) -> Sequence[ReadingKey]:
        return []


@attr.s(auto_attribs=True, frozen=True)
class Reading(Value):
    reading: str
    sub_index: Optional[int]
    default: str

    @property
    def key(self):
        return self.reading, self.sub_index

    @property
    def keys(self) -> Sequence[ReadingKey]:
        return [self.key]

    def to_sign(self, sign_map: SignMap) -> str:
        return sign_map.get(self.key, self.default)


@attr.s(auto_attribs=True, frozen=True)
class NotReading(Value):
    value: str

    def to_sign(self, _) -> str:
        return self.value


@attr.s(auto_attribs=True, frozen=True)
class Variant(Value):
    values: Tuple[Union[Reading, NotReading], ...]

    @property
    def keys(self) -> Sequence[ReadingKey]:
        return [key for value in self.values for key in value.keys]

    def to_sign(self, sign_map: SignMap) -> str:
        return VARIANT_SEPARATOR.join([
            value.to_sign(sign_map)
            for value
            in self.values
        ])


class ValueFactory:
    EMPTY = NotReading('')
    UNIDENTIFIED = NotReading(UNIDENTIFIED_SIGN)
    INVALID = NotReading(INVALID_READING)

    @staticmethod
    def create_reading(value: str, sub_index: Optional[int]) -> Reading:
        return Reading(value, sub_index, INVALID_READING)

    @staticmethod
    def create_number(value: str) -> Reading:
        return Reading(value, 1, value)

    @staticmethod
    def create_variant(
            values: Tuple[Union[Reading, NotReading], ...]
    ) -> Variant:
        return Variant(values)

    @staticmethod
    def create_not_reading(value: str) -> NotReading:
        return NotReading(value)