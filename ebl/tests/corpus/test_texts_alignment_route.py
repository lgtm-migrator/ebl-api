import json

import falcon
import attr
import pytest

from ebl.auth0 import Guest
from ebl.corpus.api_serializer import serialize
from ebl.tests.factories.corpus import TextFactory
from ebl.text.line import TextLine
from ebl.text.token import Word

ANY_USER = Guest()
DTO = {
    'alignment': [
        [
            [
                {
                    'value': 'ku]-nu-ši',
                    'alignment': 0
                }
            ]
        ]
    ]
}


def create_text_dto(text, include_documents=False):
    return serialize(text, include_documents)


def allow_references(text, bibliography):
    for chapter in text.chapters:
        for manuscript in chapter.manuscripts:
            for reference in manuscript.references:
                bibliography.create(reference.document, ANY_USER)


def allow_signs(signs, sign_list):
    for sign in signs:
        sign_list.create(sign)


def create_text(client, text):
    post_result = client.simulate_post(
        f'/texts',
        body=json.dumps(create_text_dto(text))
    )
    assert post_result.status == falcon.HTTP_CREATED


def test_updating_alignment(client, bibliography, sign_list, signs):
    allow_signs(signs, sign_list)
    text = TextFactory.build()
    allow_references(text, bibliography)
    create_text(client, text)
    chapter_index = 0
    updated_text = attr.evolve(text, chapters=(
        attr.evolve(text.chapters[chapter_index], lines=(
            attr.evolve(text.chapters[0].lines[0], manuscripts=(
                attr.evolve(
                    text.chapters[0].lines[0].manuscripts[0],
                    line=TextLine('1.', (Word('ku]-nu-ši', alignment=0),))
                ),
            )),
        )),
    ))

    expected_text = create_text_dto(updated_text, True)

    post_result = client.simulate_post(
        f'/texts/{text.category}/{text.index}'
        f'/chapters/{chapter_index}/alignment',
        body=json.dumps(DTO)
    )

    assert post_result.status == falcon.HTTP_OK
    assert post_result.headers['Access-Control-Allow-Origin'] == '*'
    assert post_result.json == expected_text

    get_result = client.simulate_get(
        f'/texts/{text.category}/{text.index}'
    )

    assert get_result.status == falcon.HTTP_OK
    assert get_result.json == expected_text


def test_updating_invalid_chapter(client, bibliography, sign_list, signs):
    allow_signs(signs, sign_list)
    text = TextFactory.build()
    allow_references(text, bibliography)
    create_text(client, text)

    post_result = client.simulate_post(
        f'/texts/{text.category}/{text.index}'
        f'/chapters/1/alignment',
        body=json.dumps(DTO)
    )

    assert post_result.status == falcon.HTTP_NOT_FOUND


@pytest.mark.parametrize('dto,expected_status', [
    ({'alignment': [[[]]]}, falcon.HTTP_UNPROCESSABLE_ENTITY),
    ({}, falcon.HTTP_BAD_REQUEST)
])
def test_updating_invalid_alignment(dto, expected_status, client, bibliography,
                                    sign_list, signs):
    allow_signs(signs, sign_list)
    text = TextFactory.build()
    allow_references(text, bibliography)
    create_text(client, text)

    post_result = client.simulate_post(
        f'/texts/{text.category}/{text.index}'
        f'/chapters/0/alignment',
        body=json.dumps(dto)
    )

    assert post_result.status == expected_status
