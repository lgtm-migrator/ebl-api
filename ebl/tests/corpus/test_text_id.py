import pytest

from ebl.transliteration.domain.text_id import TextId
from ebl.transliteration.domain.genre import Genre


@pytest.mark.parametrize(
    "text_id,expected",
    [
        (TextId(Genre.LITERATURE, 0, 0), "L 0.0"),
        (TextId(Genre.LEXICOGRAPHY, 5, 8), "Lex V.8"),
        (TextId(Genre.MEDICINE, 1, 3), "Med I.3"),
    ],
)
def test_str(text_id, expected) -> None:
    assert str(text_id) == expected
