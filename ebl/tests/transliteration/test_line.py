import pytest  # pyre-ignore

from ebl.transliteration.domain.lemmatization import LemmatizationToken
from ebl.transliteration.domain.line import (
    ControlLine,
    EmptyLine,
)
from ebl.transliteration.domain.tokens import ValueToken


def test_empty_line() -> None:
    line = EmptyLine()

    assert line.content == tuple()
    assert line.lemmatization == tuple()
    assert line.key == "EmptyLine⁞⟨⟩"
    assert line.atf == ""


def test_control_line() -> None:
    prefix = "#"
    content = "only"
    line = ControlLine(prefix, content)

    assert line.prefix == prefix
    assert line.content == (ValueToken.of(content),)
    assert line.lemmatization == (LemmatizationToken(content),)


@pytest.mark.parametrize(
    "line,lemmatization", [
        (ControlLine("#", ' a comment'), (LemmatizationToken(' a comment'),)),
        (EmptyLine(), tuple()),
    ]
)
def test_update_lemmatization(line,lemmatization) -> None:
    assert line.update_lemmatization(lemmatization) == line
