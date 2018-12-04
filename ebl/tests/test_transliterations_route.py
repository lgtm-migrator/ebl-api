import json
import falcon
import pytest


def test_update_transliteration(client,
                                fragmentarium,
                                fragment,
                                user,
                                database):
    fragment_number = fragmentarium.create(fragment)
    updates = {
        'transliteration': '$ (the transliteration)',
        'notes': 'some notes'
    }
    body = json.dumps(updates)
    url = f'/fragments/{fragment_number}/transliteration'
    post_result = client.simulate_post(url, body=body)

    assert post_result.status == falcon.HTTP_OK
    assert post_result.headers['Access-Control-Allow-Origin'] == '*'

    get_result = client.simulate_get(f'/fragments/{fragment_number}')
    updated_fragment = get_result.json

    assert updated_fragment['transliteration'] == updates['transliteration']
    assert updated_fragment['notes'] == updates['notes']
    assert updated_fragment['record'][-1]['user'] == user.ebl_name

    assert database['changelog'].find_one({
        'resource_id': fragment_number,
        'resource_type': 'fragments',
        'user_profile.name': user.profile['name']
    })


def test_update_transliteration_invalid_atf(client,
                                            fragmentarium,
                                            fragment):
    fragment_number = fragmentarium.create(fragment)
    updates = {
        'transliteration': '$ this is not valid',
        'notes': ''
    }
    body = json.dumps(updates)
    url = f'/fragments/{fragment_number}/transliteration'
    post_result = client.simulate_post(url, body=body)

    assert post_result.status == falcon.HTTP_UNPROCESSABLE_ENTITY
    assert post_result.json == {
        'title': '422 Unprocessable Entity',
        'description': 'Invalid transliteration',
        'errors': [
            {
                'description': 'Invalid line',
                'lineNumber': 1,
            }
        ]
    }


def test_update_transliteration_not_found(client):
    url = '/fragments/unknown.fragment/transliteration'
    body = json.dumps({
        'transliteration': '$ (the transliteration)',
        'notes': 'some notes'
    })
    post_result = client.simulate_post(url, body=body)

    assert post_result.status == falcon.HTTP_NOT_FOUND


@pytest.mark.parametrize("body", [
    'transliteration',
    '"transliteration"',
    json.dumps({
        'transliteration': '$ (the transliteration)'
    }),
    json.dumps({
        'notes': 'some notes'
    }),
    json.dumps({
        'transliteration': 1,
        'notes': 'some notes'
    }),
    json.dumps({
        'transliteration': '$ (the transliteration)',
        'notes': 1
    })
])
def test_update_transliteration_invalid_entity(client,
                                               fragmentarium,
                                               fragment,
                                               body):
    fragment_number = fragmentarium.create(fragment)
    url = f'/fragments/{fragment_number}/transliteration'

    post_result = client.simulate_post(url, body=body)

    assert post_result.status == falcon.HTTP_BAD_REQUEST