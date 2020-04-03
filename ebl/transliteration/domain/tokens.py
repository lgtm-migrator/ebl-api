from abc import ABC, abstractmethod
from typing import AbstractSet, Optional, Sequence, Type, TypeVar

import attr

import ebl.transliteration.domain.atf as atf
from ebl.transliteration.domain.alignment import AlignmentError, AlignmentToken
from ebl.transliteration.domain.enclosure_type import EnclosureType
from ebl.transliteration.domain.language import Language
from ebl.transliteration.domain.lemmatization import (
    LemmatizationError,
    LemmatizationToken,
)


class TokenVisitor(ABC):
    def visit(self, token: "Token") -> None:
        pass

    def visit_word(self, word) -> None:
        self.visit(word)

    def visit_language_shift(self, shift) -> None:
        self.visit(shift)

    def visit_document_oriented_gloss(self, gloss) -> None:
        self.visit(gloss)

    def visit_broken_away(self, broken_away) -> None:
        self.visit(broken_away)

    def visit_perhaps_broken_away(self, broken_away) -> None:
        self.visit(broken_away)

    def visit_accidental_omission(self, omission) -> None:
        self.visit(omission)

    def visit_intentional_omission(self, omission) -> None:
        self.visit(omission)

    def visit_removal(self, removal) -> None:
        self.visit(removal)

    def visit_erasure(self, erasure):
        self.visit(erasure)

    def visit_divider(self, divider) -> None:
        self.visit(divider)

    def visit_commentary_protocol(self, protocol) -> None:
        self.visit(protocol)

    def visit_variant(self, variant) -> None:
        self.visit(variant)

    def visit_gloss(self, gloss) -> None:
        self.visit(gloss)

    def visit_named_sign(self, named_sign) -> None:
        self.visit(named_sign)


T = TypeVar("T", bound="Token")


@attr.s(frozen=True, auto_attribs=True)
class Token(ABC):
    enclosure_type: AbstractSet[EnclosureType]

    @property
    @abstractmethod
    def value(self) -> str:
        ...

    @property
    @abstractmethod
    def parts(self) -> Sequence["Token"]:
        ...

    @property
    def clean_value(self) -> str:
        return self.value

    @property
    def lemmatizable(self) -> bool:
        return False

    @property
    def alignable(self) -> bool:
        return self.lemmatizable

    def get_key(self) -> str:
        parts = (
            f"⟨{'⁚'.join(part.get_key() for part in self.parts)}⟩" if self.parts else ""
        )
        return f"{type(self).__name__}⁝{self.value}{parts}"

    def set_unique_lemma(self, lemma: LemmatizationToken) -> "Token":
        if lemma.unique_lemma is None and lemma.value == self.value:
            return self
        else:
            raise LemmatizationError()

    def set_alignment(self, alignment: AlignmentToken):
        if alignment.alignment is None and alignment.value == self.value:
            return self
        else:
            raise AlignmentError()

    def set_enclosure_type(self, enclosure_type: AbstractSet[EnclosureType]) -> "Token":
        return attr.evolve(self, enclosure_type=enclosure_type)

    def strip_alignment(self):
        return self

    def merge(self, token: "Token") -> "Token":
        return token

    def accept(self, visitor: "TokenVisitor") -> None:
        visitor.visit(self)


T = TypeVar("T", bound="ValueToken")


@attr.s(auto_attribs=True, frozen=True)
class ValueToken(Token):
    _value: str

    @property
    def value(self) -> str:
        return self._value

    @property
    def parts(self):
        return tuple()

    @classmethod
    def of(cls: Type[T], value: str) -> T:
        return cls(frozenset(), value)  # pyre-ignore[19]


@attr.s(frozen=True)
class LanguageShift(ValueToken):
    _normalization_shift = "%n"

    @property
    def language(self):
        return Language.of_atf(self.value)

    @property
    def normalized(self):
        return self.value == LanguageShift._normalization_shift

    def accept(self, visitor: "TokenVisitor") -> None:
        visitor.visit_language_shift(self)


@attr.s(frozen=True)
class UnknownNumberOfSigns(Token):
    @property
    def value(self) -> str:
        return atf.UNKNOWN_NUMBER_OF_SIGNS

    @property
    def parts(self):
        return tuple()


@attr.s(frozen=True)
class Tabulation(ValueToken):
    pass


@attr.s(frozen=True)
class CommentaryProtocol(ValueToken):
    @property
    def protocol(self):
        return atf.CommentaryProtocol(self.value)

    def accept(self, visitor: "TokenVisitor") -> None:
        visitor.visit_commentary_protocol(self)


@attr.s(frozen=True, auto_attribs=True)
class Column(Token):
    number: Optional[int] = attr.ib(default=None)

    @staticmethod
    def of(number: Optional[int] = None) -> "Column":
        return Column(frozenset(), number)

    @number.validator
    def _check_number(self, _, value) -> None:
        if value is not None and value < 0:
            raise ValueError("number must not be negative")

    @property
    def value(self) -> str:
        return "&" if self.number is None else f"&{self.number}"

    @property
    def parts(self):
        return tuple()


@attr.s(frozen=True, auto_attribs=True)
class Variant(Token):
    tokens: Sequence[Token]

    @staticmethod
    def of(*args: Token) -> "Variant":
        return Variant(frozenset(), tuple(args))

    @property
    def value(self) -> str:
        return "/".join(token.value for token in self.tokens)

    @property
    def clean_value(self) -> str:
        return "/".join(token.clean_value for token in self.tokens)

    @property
    def parts(self):
        return self.tokens

    def accept(self, visitor: "TokenVisitor") -> None:
        visitor.visit_variant(self)


@attr.s(auto_attribs=True, frozen=True)
class Joiner(Token):
    _value: atf.Joiner

    @property
    def value(self):
        return self._value.value

    @property
    def parts(self):
        return tuple()

    @staticmethod
    def dot():
        return Joiner(frozenset(), atf.Joiner.DOT)

    @staticmethod
    def hyphen():
        return Joiner(frozenset(), atf.Joiner.HYPHEN)

    @staticmethod
    def colon():
        return Joiner(frozenset(), atf.Joiner.COLON)

    @staticmethod
    def plus():
        return Joiner(frozenset(), atf.Joiner.PLUS)

    @staticmethod
    def of(joiner: atf.Joiner):
        return Joiner(frozenset(), joiner)
