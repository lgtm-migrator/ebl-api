import falcon
from falcon.media.validators.jsonschema import validate
from ebl.errors import DataError
from ebl.require_scope import require_scope
from ebl.bibliography.bibliography_entry import CSL_JSON_SCHEMA


class BibliographyResource:
    def __init__(self, bibliography):
        self._bibliography = bibliography

    @falcon.before(require_scope, 'read:bibliography')
    def on_get(self, req, resp):
        resp.media = self._bibliography.search(
            *self._parse_search_request(req)
        )

    @staticmethod
    def _parse_search_request(req):
        author = 'author'
        year = 'year'
        title = 'title'
        allowed_params = {author, year, title}
        req_params = set(req.params.keys())
        if not req_params <= allowed_params:
            extra_params = req_params - allowed_params
            raise DataError(f'Unsupported query parameters: {extra_params}.')
        try:
            return [
                req.params.get(author),
                int(req.params[year]) if year in req.params else None,
                req.params.get(title)
            ]
        except ValueError:
            raise DataError(f'Year "{year}" is not numeric.')

    @falcon.before(require_scope, 'write:bibliography')
    @validate(CSL_JSON_SCHEMA)
    def on_put(self, req, _resp):
        self._bibliography.create(req.media, req.context['user'])


class BibliographyEntriesResource:

    def __init__(self, bibliography):
        self._bibliography = bibliography

    @falcon.before(require_scope, 'read:bibliography')
    def on_get(self, _req, resp, id_):
        resp.media = self._bibliography.find(id_)

    @falcon.before(require_scope, 'write:bibliography')
    @validate(CSL_JSON_SCHEMA)
    def on_post(self, req, _resp, id_):
        entry = {**req.media, 'id': id_}
        self._bibliography.update(entry, req.context['user'])