import falcon  # pyre-ignore[21]
from falcon.media.validators.jsonschema import validate  # pyre-ignore[21]

from ebl.corpus.web.alignments import create_chapter_index
from ebl.corpus.web.api_serializer import deserialize_lines, serialize
from ebl.corpus.web.text_utils import create_text_id
from ebl.corpus.web.texts import LINE_DTO_SCHEMA
from ebl.users.web.require_scope import require_scope

LINES_DTO_SCHEMA = {
    "type": "object",
    "properties": {"lines": {"type": "array", "items": LINE_DTO_SCHEMA}},
    "required": ["lines"],
}


class LinesResource:
    def __init__(self, corpus):
        self._corpus = corpus

    @falcon.before(require_scope, "write:texts")
    @validate(LINES_DTO_SCHEMA)  # pyre-ignore[56]
    def on_post(
        self,
        req: falcon.Request,  # pyre-ignore[11]
        resp: falcon.Response,  # pyre-ignore[11]
        category: str,
        index: str,
        chapter_index: str,
    ) -> None:
        self._corpus.update_lines(
            create_text_id(category, index),
            create_chapter_index(chapter_index),
            deserialize_lines(req.media["lines"]),
            req.context.user,
        )
        updated_text = self._corpus.find(create_text_id(category, index))
        resp.media = serialize(updated_text)
