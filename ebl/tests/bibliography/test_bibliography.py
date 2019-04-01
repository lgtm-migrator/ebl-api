# pylint: disable=W0621
from freezegun import freeze_time
import pydash
import pytest
from ebl.errors import NotFoundError, DuplicateError


@pytest.fixture
def mongo_entry(bibliography_entry):
    return pydash.map_keys(
        bibliography_entry,
        lambda _, key: '_id' if key == 'id' else key
    )


COLLECTION = 'bibliography'


def test_create(database, bibliography, bibliography_entry, mongo_entry, user):
    bibliography.create(bibliography_entry, user)

    assert database[COLLECTION].find_one(
        {'_id': bibliography_entry['id']}
    ) == mongo_entry


def test_create_duplicate(bibliography, bibliography_entry, user):
    bibliography.create(bibliography_entry, user)
    with pytest.raises(DuplicateError):
        bibliography.create(bibliography_entry, user)


def test_find(database, bibliography, bibliography_entry, mongo_entry):
    database[COLLECTION].insert_one(mongo_entry)

    assert bibliography.find(bibliography_entry['id']) == bibliography_entry


def test_entry_not_found(bibliography):
    with pytest.raises(NotFoundError):
        bibliography.find('not found')


def test_update(bibliography, bibliography_entry, user):
    updated_entry = pydash.omit({
        **bibliography_entry,
        'title': 'New Title'
    }, 'PMID')
    bibliography.create(bibliography_entry, user)
    bibliography.update(updated_entry, user)

    assert bibliography.find(bibliography_entry['id']) == updated_entry


@freeze_time("2018-09-07 15:41:24.032")
def test_changelog(bibliography,
                   database,
                   bibliography_entry,
                   mongo_entry,
                   user,
                   make_changelog_entry):
    # pylint: disable=R0913
    updated_entry = {
        **bibliography_entry,
        'title': 'New Title'
    }
    bibliography.create(bibliography_entry, user)
    bibliography.update(updated_entry, user)

    expected_changelog = [
        make_changelog_entry(
            COLLECTION,
            bibliography_entry['id'],
            {'_id': bibliography_entry['id']},
            mongo_entry
        ),
        make_changelog_entry(
            COLLECTION,
            bibliography_entry['id'],
            mongo_entry,
            pydash.map_keys(
                updated_entry,
                lambda _, key: ('_id' if key == 'id' else key)
            )
        )
    ]

    assert [change for change in database['changelog'].find(
        {'resource_id': bibliography_entry['id']},
        {'_id': 0}
    )] == expected_changelog


def test_update_not_found(bibliography, bibliography_entry, user):
    with pytest.raises(NotFoundError):
        bibliography.update(bibliography_entry, user)