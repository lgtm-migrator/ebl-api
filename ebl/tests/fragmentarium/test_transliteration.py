import pytest

from ebl.atf.atf import Atf
from ebl.fragmentarium.application.transliteration_update import \
    TransliterationUpdate
from ebl.transliteration.atf_parser import parse_atf
from ebl.transliteration.text import Text
from ebl.transliteration.transliteration_error import TransliterationError


def test_atf():
    atf = Atf('1. kur')
    transliteration = TransliterationUpdate(atf)

    assert transliteration.atf == atf


def test_notes():
    notes = 'notes'
    transliteration = TransliterationUpdate(notes=notes)

    assert transliteration.notes == notes


def test_signs():
    signs = 'X'
    transliteration = TransliterationUpdate(signs=signs)

    assert transliteration.signs == signs


@pytest.mark.parametrize('transliteration,expected', [
    (TransliterationUpdate(), Text()),
    (TransliterationUpdate(Atf('1. kur')), parse_atf(Atf('1. kur')))
])
def test_parse(transliteration, expected):
    assert transliteration.parse() == expected


def test_parse_invalid():
    transliteration = TransliterationUpdate(Atf('1. ö invalid atf'))
    with pytest.raises(TransliterationError):
        transliteration.parse()


def test_validate_valid_signs(transliteration_factory, sign_list, signs):
    TransliterationUpdate(Atf('1. šu gid₂'), signs='ŠU BU')


def test_invalid_atf():
    with pytest.raises(TransliterationError,
                       match='Invalid transliteration') as excinfo:
        TransliterationUpdate(Atf('$ this is not valid'))

    assert excinfo.value.errors == [
        {
            'description': 'Invalid line',
            'lineNumber': 1
        }
    ]


def test_validate_invalid_value(sign_list):
    with pytest.raises(TransliterationError,
                       match='Invalid transliteration') as excinfo:
        TransliterationUpdate(Atf('1. invalid values'), signs='? ?')

    assert excinfo.value.errors == [
        {
            'description': 'Invalid value',
            'lineNumber': 1
        }
    ]


def test_validate_multiple_errors(sign_list):
    with pytest.raises(TransliterationError,
                       match='Invalid transliteration') as excinfo:
        TransliterationUpdate(
            Atf('1. invalid values\n$ (valid)\n2. more invalid values'),
            signs='? ?\n? ? ?'
        )

    assert excinfo.value.errors == [
        {
            'description': 'Invalid value',
            'lineNumber': 1
        },
        {
            'description': 'Invalid value',
            'lineNumber': 3
        }
    ]