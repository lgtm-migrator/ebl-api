import falcon


def test_get_photo(client, photo):
    result = client.simulate_get("/fragments/K.1/photo")

    assert result.status == falcon.HTTP_OK
    assert result.headers["Content-Type"] == photo.content_type
    assert result.content == photo.data


def test_get_photo_not_found(client):
    result = client.simulate_get("/fragments/unknown/photo")

    assert result.status == falcon.HTTP_NOT_FOUND


def test_get_photo_not_allowed(guest_client):
    result = guest_client.simulate_get("/fragments/K.1/photo")

    assert result.status == falcon.HTTP_FORBIDDEN
