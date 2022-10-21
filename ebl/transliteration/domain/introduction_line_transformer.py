from typing import Sequence

from lark.lexer import Token
from lark.visitors import Transformer, v_args

from ebl.bibliography.domain.reference import BibliographyId
from ebl.transliteration.domain.language import Language
from ebl.transliteration.domain.line import ControlLine, EmptyLine
from ebl.transliteration.domain.markup import (
    BibliographyPart,
    EmphasisPart,
    LanguagePart,
    MarkupPart,
    ParagraphSeparatorPart,
    StringPart,
)
from ebl.transliteration.domain.note_line import NoteLine
from ebl.transliteration.domain.tokens import Token as EblToken


class IntroductionLineTransformer(Transformer):
    def markup(self, children) -> Sequence[MarkupPart]:
        return tuple(children)

    @v_args(inline=True)
    def ebl_atf_introduction_line__language_part(
        self, language: Token, transliteration: Sequence[EblToken]
    ) -> LanguagePart:
        return LanguagePart.of_transliteration(
            Language.of_atf(f"%{language}"), transliteration
        )

    @v_args(inline=True)
    def ebl_atf_introduction_line__emphasis_part(self, text: str) -> EmphasisPart:
        return EmphasisPart(text)

    @v_args(inline=True)
    def ebl_atf_introduction_line__string_part(self, text: str) -> StringPart:
        return StringPart(text)
    
    @v_args(inline=True)
    def ebl_atf_introduction_line__text(self, children) -> StringPart:
        return "".join(children)

    @v_args(inline=True)
    def ebl_atf_introduction_line__bibliography_part(
        self, id_, pages
    ) -> BibliographyPart:
        return BibliographyPart.of(
            BibliographyId("".join(id_.children)), "".join(pages.children)
        )

    def ebl_atf_introduction_line__paragraph_part(
        self, _
    ) -> ParagraphSeparatorPart:
        return ParagraphSeparatorPart("PARAGRAPH")

    def empty_line(self, _):
        return EmptyLine()

    @v_args(inline=True)
    def control_line(self, prefix, content):
        return ControlLine(prefix, content)

    def introduction_line(self, children):
        return tuple(children)
