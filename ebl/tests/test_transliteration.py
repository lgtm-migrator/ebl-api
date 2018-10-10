from ebl.fragmentarium.transliterations import Transliteration


def test_equality():
    transliteration = Transliteration('transliteration', 'notes')
    similar = Transliteration('transliteration', 'notes')
    different_notes = Transliteration('transliteration', 'different')
    different_atf = Transliteration('different', 'different')

    assert transliteration == similar
    assert transliteration != different_notes
    assert transliteration != different_atf


def test_hash():
    transliteration = Transliteration('transliteration', 'notes')

    assert hash(transliteration) == hash(('transliteration', 'notes'))


def test_atf():
    transliteration = Transliteration('transliteration', 'notes')

    assert transliteration.atf == 'transliteration'


def test_notes():
    transliteration = Transliteration('transliteration', 'notes')

    assert transliteration.notes == 'notes'

def test_filtered():
    transliteration = Transliteration.without_notes(
        '&K11111\n@reverse\n\n$ end of side\n#note\n=: foo\n1. ku\n2. $AN'
    )
    assert transliteration.filtered == ['1. ku', '2. $AN']


def test_with_signs(sign_list, signs):
    for sign in signs:
        sign_list.create(sign)

    transliteration = Transliteration.without_notes('1. šu gid₂')

    assert transliteration.with_signs(sign_list).signs == 'ŠU BU'
