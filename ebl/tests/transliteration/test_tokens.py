import pytest

import ebl.transliteration.domain.atf as atf
from ebl.transliteration.domain.alignment import AlignmentError, AlignmentToken
from ebl.transliteration.domain.language import Language
from ebl.transliteration.domain.lemmatization import LemmatizationError, \
    LemmatizationToken
from ebl.transliteration.domain.tokens import (DEFAULT_NORMALIZED,
                                               DocumentOrientedGloss, Erasure,
                                               LanguageShift, LineContinuation,
                                               Side,
                                               UnknownNumberOfSigns,
                                               Tabulation,
                                               CommentaryProtocol, Divider,
                                               ValueToken, Column, Word,
                                               Variant, UnidentifiedSign,
                                               UnclearSign)

TOKENS = [
    UnknownNumberOfSigns('...'),
    LanguageShift('%sux'),
    DocumentOrientedGloss('{(')
]


def test_value_token():
    value = 'value'
    token = ValueToken(value)
    equal = ValueToken(value)
    other = ValueToken('anothervalue')

    assert token.value == value
    assert token.get_key() == f'ValueToken⁝{value}'
    assert token.lemmatizable is False
    assert token.to_dict() == {
        'type': 'Token',
        'value': token.value
    }

    assert token == equal
    assert hash(token) == hash(equal)

    assert token != other
    assert hash(token) != hash(other)


@pytest.mark.parametrize("value,expected_language,normalized", [
    (r'%sux', Language.SUMERIAN, DEFAULT_NORMALIZED),
    (r'%es', Language.EMESAL, DEFAULT_NORMALIZED),
    (r'%sb', Language.AKKADIAN, DEFAULT_NORMALIZED),
    (r'%n', Language.AKKADIAN, True),
    (r'%foo', Language.UNKNOWN, DEFAULT_NORMALIZED)
])
def test_language_shift(value, expected_language, normalized):
    shift = LanguageShift(value)
    equal = LanguageShift(value)
    other = ValueToken(r'%bar')

    assert shift.value == value
    assert shift.get_key() == f'LanguageShift⁝{value}'
    assert shift.lemmatizable is False
    assert shift.normalized == normalized
    assert shift.language == expected_language
    assert shift.to_dict() == {
        'type': 'LanguageShift',
        'value': shift.value,
        'normalized': normalized,
        'language': shift.language.name
    }

    assert shift == equal
    assert hash(shift) == hash(equal)

    assert shift != other
    assert hash(shift) != hash(other)

    assert shift != ValueToken(value)


def test_document_oriented_gloss():
    value = '{('
    gloss = DocumentOrientedGloss(value)
    equal = DocumentOrientedGloss(value)
    other = DocumentOrientedGloss(')}')

    assert gloss.value == value
    assert gloss.get_key() == f'DocumentOrientedGloss⁝{value}'
    assert gloss.side == Side.LEFT
    assert gloss.lemmatizable is False
    assert gloss.to_dict() == {
        'type': 'DocumentOrientedGloss',
        'value': gloss.value
    }

    assert other.side == Side.RIGHT

    assert gloss == equal
    assert hash(gloss) == hash(equal)

    assert gloss != other
    assert hash(gloss) != hash(other)


@pytest.mark.parametrize("token", TOKENS)
def test_set_unique_lemma_incompatible(token):
    lemma = LemmatizationToken('other-value')
    with pytest.raises(LemmatizationError):
        token.set_unique_lemma(lemma)


@pytest.mark.parametrize("token", TOKENS)
def test_set_unique_lemma_with_lemma(token):
    lemma = LemmatizationToken(token.value, tuple())
    with pytest.raises(LemmatizationError):
        token.set_unique_lemma(lemma)


@pytest.mark.parametrize("token", TOKENS)
def test_set_unique_lemma_no_lemma(token):
    lemma = LemmatizationToken(token.value)
    assert token.set_unique_lemma(lemma) == token


@pytest.mark.parametrize("token", TOKENS)
def test_set_alignment_incompatible(token):
    alignment = AlignmentToken('other-value', None)
    with pytest.raises(AlignmentError):
        token.set_alignment(alignment)


@pytest.mark.parametrize("token", TOKENS)
def test_set_non_empty_alignment(token):
    alignment = AlignmentToken(token.value, 0)
    with pytest.raises(AlignmentError):
        token.set_alignment(alignment)


@pytest.mark.parametrize("token", TOKENS)
def test_set_alignment_no_alignment(token):
    alignment = AlignmentToken(token.value, None)
    assert token.set_alignment(alignment) == token


@pytest.mark.parametrize('old', TOKENS)
@pytest.mark.parametrize('new', TOKENS)
def test_merge(old, new):
    merged = old.merge(new)
    assert merged == new


def test_erasure():
    value = '°'
    side = Side.LEFT
    erasure = Erasure(value, side)

    assert erasure.value == value
    assert erasure.get_key() == f'Erasure⁝{value}'
    assert erasure.lemmatizable is False
    assert erasure.to_dict() == {
        'type': 'Erasure',
        'value': erasure.value,
        'side': side.name
    }


def test_line_continuation():
    value = '→'
    continuation = LineContinuation(value)

    assert continuation.value == value
    assert continuation.get_key() == f'LineContinuation⁝{value}'
    assert continuation.lemmatizable is False
    assert continuation.to_dict() == {
        'type': 'LineContinuation',
        'value': continuation.value
    }


def test_unknown_number_of_signs():
    value = '...'
    unknown_number_of_signs = UnknownNumberOfSigns(value)

    assert unknown_number_of_signs.value == value
    assert unknown_number_of_signs.get_key() == f'UnknownNumberOfSigns⁝{value}'
    assert unknown_number_of_signs.lemmatizable is False
    assert unknown_number_of_signs.to_dict() == {
        'type': 'UnknownNumberOfSigns',
        'value': value
    }


def test_tabulation():
    value = '($___$)'
    tabulation = Tabulation(value)

    assert tabulation.value == value
    assert tabulation.get_key() == f'Tabulation⁝{value}'
    assert tabulation.lemmatizable is False
    assert tabulation.to_dict() == {
        'type': 'Tabulation',
        'value': value
    }


@pytest.mark.parametrize('protocol_enum', atf.CommentaryProtocol)
def test_commentary_protocol(protocol_enum):
    value = protocol_enum.value
    protocol = CommentaryProtocol(value)

    assert protocol.value == value
    assert protocol.get_key() == f'CommentaryProtocol⁝{value}'
    assert protocol.lemmatizable is False
    assert protocol.protocol == protocol_enum
    assert protocol.to_dict() == {
        'type': 'CommentaryProtocol',
        'value': value
    }


def test_divider():
    value = ':'
    modifiers = ('@v', )
    flags = (atf.Flag.UNCERTAIN,)
    divider = Divider(value, modifiers, flags)

    expected_value = ':@v?'
    assert divider.value == expected_value
    assert divider.get_key() == f'Divider⁝{expected_value}'
    assert divider.lemmatizable is False
    assert divider.to_dict() == {
        'type': 'Divider',
        'value': expected_value,
        'divider': value,
        'modifiers': list(modifiers),
        'flags': ['?']
    }


def test_column():
    column = Column()

    expected_value = '&'
    assert column.value == expected_value
    assert column.get_key() == f'Column⁝{expected_value}'
    assert column.lemmatizable is False
    assert column.to_dict() == {
        'type': 'Column',
        'value': expected_value,
        'number': None
    }


def test_column_with_number():
    column = Column(1)

    expected_value = '&1'
    assert column.value == expected_value
    assert column.get_key() == f'Column⁝{expected_value}'
    assert column.lemmatizable is False
    assert column.to_dict() == {
        'type': 'Column',
        'value': expected_value,
        'number': 1
    }


def test_invalid_column():
    with pytest.raises(ValueError):
        Column(-1)


def test_variant():
    word = Word('sal')
    divider = Divider(':')
    variant = Variant.of(word, divider)

    expected_value = 'sal/:'
    assert variant.value == expected_value
    assert variant.get_key() == f'Variant⁝{expected_value}'
    assert variant.lemmatizable is False
    assert variant.to_dict() == {
        'type': 'Variant',
        'value': expected_value,
        'tokens': [word.to_dict(), divider.to_dict()]
    }


def test_unidentified_sign():
    sign = UnidentifiedSign()

    expected_value = 'X'
    assert sign.value == expected_value
    assert sign.get_key() == f'UnidentifiedSign⁝{expected_value}'
    assert sign.flags == tuple()
    assert sign.lemmatizable is False
    assert sign.to_dict() == {
        'type': 'UnidentifiedSign',
        'value': expected_value,
        'flags': []
    }


def test_unidentified_sign_with_flags():
    flags = [atf.Flag.DAMAGE]
    sign = UnidentifiedSign(flags)

    expected_value = 'X#'
    assert sign.value == expected_value
    assert sign.get_key() == f'UnidentifiedSign⁝{expected_value}'
    assert sign.flags == tuple(flags)
    assert sign.lemmatizable is False
    assert sign.to_dict() == {
        'type': 'UnidentifiedSign',
        'value': expected_value,
        'flags': ['#']
    }


def test_unclear_sign():
    sign = UnclearSign()

    expected_value = 'x'
    assert sign.value == expected_value
    assert sign.get_key() == f'UnclearSign⁝{expected_value}'
    assert sign.flags == tuple()
    assert sign.lemmatizable is False
    assert sign.to_dict() == {
        'type': 'UnclearSign',
        'value': expected_value,
        'flags': []
    }


def test_unclear_sign_with_flags():
    flags = [atf.Flag.CORRECTION]
    sign = UnclearSign(flags)

    expected_value = 'x!'
    assert sign.value == expected_value
    assert sign.get_key() == f'UnclearSign⁝{expected_value}'
    assert sign.flags == tuple(flags)
    assert sign.lemmatizable is False
    assert sign.to_dict() == {
        'type': 'UnclearSign',
        'value': expected_value,
        'flags': ['!']
    }