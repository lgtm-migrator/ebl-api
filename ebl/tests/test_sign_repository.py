# pylint: disable=W0621
import pytest


COLLECTION = 'signs'


@pytest.fixture
def sign():
    return {
        '_id': 'IGI',
        'lists': [
            'HZL288'
        ],
        'unicode': [
            74054
        ],
        'notes': [],
        'internalNotes': [],
        'literature': [],
        'values': [
            {
                'value': 'ši',
                'subIndex': 1,
                'questionable': False,
                'deprecated': False,
                'notes': [],
                'internalNotes': []
            },
            {
                'value': 'panu',
                'subIndex': 1,
                'questionable': False,
                'deprecated': False,
                'languageRestriction': 'akk',
                'notes': [],
                'internalNotes': []
            }
        ],
        'forms': []
    }


@pytest.fixture
def another_sign():
    # pylint: disable=R0801
    return {
        '_id': 'SI',
        'lists': [],
        'unicode': [],
        'notes': [],
        'internalNotes': [],
        'literature': [],
        'values': [
            {
                'value': 'ši',
                'subIndex': 2,
                'questionable': False,
                'deprecated': False,
                'notes': [],
                'internalNotes': []
            },
            {
                'value': 'hu',
                'questionable': False,
                'deprecated': False,
                'notes': [],
                'internalNotes': []
            },
        ],
        'forms': []
    }


def test_create(database, sign_repository, sign):
    sign_name = sign_repository.create(sign)

    assert database[COLLECTION].find_one({'_id': sign_name}) == sign


def test_find(database, sign_repository, sign):
    database[COLLECTION].insert_one(sign)

    assert sign_repository.find(sign['_id']) == sign


def test_sign_not_found(sign_repository):
    with pytest.raises(KeyError):
        sign_repository.find('unknown id')


def test_search(database,
                sign_repository,
                sign,
                another_sign):
    database[COLLECTION].insert_many([sign, another_sign])

    assert sign_repository.search('ši', 1) == sign
    assert sign_repository.search('hu', None) == another_sign


def test_search_not_found(sign_repository):
    assert sign_repository.search('unknown', 1) is None
