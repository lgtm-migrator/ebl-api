from itertools import zip_longest
from typing import Callable, Iterable, Sequence, Type, TypeVar, Union

import attr

from ebl.merger import Merger
from ebl.transliteration.domain.alignment import AlignmentError, AlignmentToken
from ebl.transliteration.domain.atf import Atf
from ebl.transliteration.domain.atf_visitor import convert_to_atf
from ebl.transliteration.domain.enclosure_visitor import set_enclosure_type
from ebl.transliteration.domain.language_visitor import set_language
from ebl.transliteration.domain.line import Line
from ebl.transliteration.domain.line_number import AbstractLineNumber
from ebl.transliteration.domain.tokens import Token
from ebl.transliteration.domain.word_tokens import Word
from ebl.transliteration.domain.lemmatization import LemmatizationToken


L = TypeVar("L", "TextLine", "Line")
T = TypeVar("T")


@attr.s(auto_attribs=True, frozen=True)
class TextLine(Line):
    line_number: AbstractLineNumber
    _content: Sequence[Token] = tuple()

    @property
    def key(self) -> str:
        tokens = "⁚".join(token.get_key() for token in self.content)
        return f"{type(self).__name__}⁞{self.atf}⟨{tokens}⟩"

    @property
    def content(self) -> Sequence:
        return self._content

    @staticmethod
    def of_iterable(
        line_number: AbstractLineNumber,
        content: Iterable[Token]
    ) -> "TextLine":
        content_with_enclosures = set_enclosure_type(content)
        content_with_language = set_language(content_with_enclosures)

        return TextLine(line_number, content_with_language)

    @property
    def atf(self) -> Atf:
        return convert_to_atf(self.line_number.atf, self.content)

    @property
    def lemmatization(self) -> Sequence[LemmatizationToken]:
        return tuple(
            (
                LemmatizationToken(token.value, token.unique_lemma)
                if isinstance(token, Word)
                else LemmatizationToken(token.value)
            )
            for token in self.content
        )

    def update_alignment(self, alignment: Sequence[AlignmentToken]) -> "Line":
        def updater(token, alignment_token):
            return token.set_alignment(alignment_token)

        return self._update_tokens(alignment, updater, AlignmentError)

    def _update_tokens(
        self,
        updates: Sequence[T],
        updater: Callable[[Token, T], Token],
        error_class: Type[Exception],
    ) -> "Line":
        if len(self.content) == len(updates):
            zipped = zip_longest(self.content, updates)
            content = tuple(updater(pair[0], pair[1]) for pair in zipped)
            return attr.evolve(self, content=content)
        else:
            raise error_class()

    def merge(self, other: L) -> Union["TextLine", L]:
        def merge_tokens():
            def map_(token):
                return token.get_key()

            def inner_merge(old: Token, new: Token) -> Token:
                return old.merge(new)

            return Merger(map_, inner_merge).merge(self.content, other.content)

        return (
            TextLine.of_iterable(other.line_number, merge_tokens())
            if isinstance(other, TextLine)
            else other
        )

    def strip_alignments(self) -> "TextLine":
        stripped_content = tuple(token.strip_alignment() for token in self.content)
        return attr.evolve(self, content=stripped_content)
