from typing import List, Optional, Tuple, Sequence

import pymongo
from pymongo.database import Database

from ebl.bibliography.infrastructure.bibliography import join_reference_documents
from ebl.corpus.application.corpus import TextRepository
from ebl.corpus.application.display_schemas import ChapterDisplaySchema
from ebl.corpus.application.schemas import (
    ChapterSchema,
    DictionaryLineSchema,
    LineSchema,
    ManuscriptSchema,
    TextSchema,
    ManuscriptAttestationSchema,
)
from ebl.corpus.domain.chapter import Chapter, ChapterId
from ebl.corpus.domain.chapter_display import ChapterDisplay
from ebl.corpus.domain.dictionary_line import DictionaryLine
from ebl.corpus.domain.line import Line
from ebl.corpus.domain.manuscript import Manuscript
from ebl.corpus.domain.manuscript_attestation import ManuscriptAttestation
from ebl.corpus.domain.text import Text, TextId
from ebl.corpus.infrastructure.chapter_query_filters import (
    filter_query_by_transliteration,
)
from ebl.corpus.infrastructure.manuscript_lemma_filter import (
    filter_manuscripts_by_lemma,
)
from ebl.corpus.infrastructure.queries import (
    aggregate_chapter_display,
    chapter_id_query,
    join_chapters,
    join_text,
    join_text_title,
)
from ebl.errors import NotFoundError
from ebl.fragmentarium.infrastructure.queries import is_in_fragmentarium, join_joins
from ebl.mongo_collection import MongoCollection
from ebl.transliteration.application.museum_number_schema import MuseumNumberSchema
from ebl.transliteration.domain.genre import Genre
from ebl.transliteration.domain.museum_number import MuseumNumber
from ebl.transliteration.domain.transliteration_query import TransliterationQuery
from ebl.transliteration.infrastructure.collections import (
    CHAPTERS_COLLECTION,
    TEXTS_COLLECTION,
)


def text_not_found(id_: TextId) -> Exception:
    return NotFoundError(f"Text {id_} not found.")


def chapter_not_found(id_: ChapterId) -> Exception:
    return NotFoundError(f"Chapter {id_} not found.")


def line_not_found(id_: ChapterId, number: int) -> Exception:
    return NotFoundError(f"Chapter {id_} line {number} not found.")


class MongoTextRepository(TextRepository):
    def __init__(self, database: Database):
        self._texts = MongoCollection(database, TEXTS_COLLECTION)
        self._chapters = MongoCollection(database, CHAPTERS_COLLECTION)

    def create_indexes(self) -> None:
        self._texts.create_index(
            [
                ("genre", pymongo.ASCENDING),
                ("category", pymongo.ASCENDING),
                ("index", pymongo.ASCENDING),
            ],
            unique=True,
        )
        self._chapters.create_index(
            [
                ("textId.genre", pymongo.ASCENDING),
                ("textId.category", pymongo.ASCENDING),
                ("textId.index", pymongo.ASCENDING),
            ]
        )
        self._chapters.create_index(
            [
                ("textId.genre", pymongo.ASCENDING),
                ("textId.category", pymongo.ASCENDING),
                ("textId.index", pymongo.ASCENDING),
                ("order", pymongo.ASCENDING),
            ]
        )
        self._chapters.create_index(
            [
                ("textId.genre", pymongo.ASCENDING),
                ("textId.category", pymongo.ASCENDING),
                ("textId.index", pymongo.ASCENDING),
                ("stage", pymongo.ASCENDING),
                ("name", pymongo.ASCENDING),
            ],
            unique=True,
        )

    def create(self, text: Text) -> None:
        self._texts.insert_one(TextSchema(exclude=["chapters"]).dump(text))

    def create_chapter(self, chapter: Chapter) -> None:
        self._chapters.insert_one(ChapterSchema().dump(chapter))

    def find(self, id_: TextId) -> Text:
        try:
            mongo_text = next(
                self._texts.aggregate(
                    [
                        {
                            "$match": {
                                "genre": id_.genre.value,
                                "category": id_.category,
                                "index": id_.index,
                            }
                        },
                        *join_reference_documents(),
                        *join_chapters(True),
                        {"$limit": 1},
                    ]
                )
            )
            return TextSchema().load(mongo_text)

        except StopIteration as error:
            raise text_not_found(id_) from error

    def find_chapter(self, id_: ChapterId) -> Chapter:
        try:
            chapter = self._chapters.find_one(
                chapter_id_query(id_), projection={"_id": False}
            )
            return ChapterSchema().load(chapter)
        except NotFoundError as error:
            raise chapter_not_found(id_) from error

    def find_chapter_for_display(self, id_: ChapterId) -> ChapterDisplay:
        try:
            text = self.find(id_.text_id)
            chapters = self._chapters.aggregate(aggregate_chapter_display(id_))
            return ChapterDisplaySchema().load(
                {
                    **next(chapters),
                    "textName": text.name,
                    "textHasDoi": text.has_doi,
                    "isSingleStage": not text.has_multiple_stages,
                }
            )
        except NotFoundError as error:
            raise text_not_found(id_.text_id) from error
        except StopIteration as error:
            raise chapter_not_found(id_) from error

    def find_line(self, id_: ChapterId, number: int) -> Line:
        try:
            chapters = self._chapters.aggregate(
                [
                    {"$match": chapter_id_query(id_)},
                    {"$unwind": "$lines"},
                    {"$replaceRoot": {"newRoot": "$lines"}},
                    {"$skip": number},
                ]
            )
            return LineSchema().load(next(chapters))
        except StopIteration as error:
            raise line_not_found(id_, number) from error

    def list(self) -> List[Text]:
        return TextSchema().load(
            self._texts.aggregate(
                [
                    *join_reference_documents(),
                    *join_chapters(False),
                    {
                        "$sort": {
                            "category": pymongo.ASCENDING,
                            "index": pymongo.ASCENDING,
                        }
                    },
                ]
            ),
            many=True,
        )

    def update(self, id_: ChapterId, chapter: Chapter) -> None:
        self._chapters.update_one(
            chapter_id_query(id_),
            {
                "$set": ChapterSchema(
                    only=[
                        "manuscripts",
                        "uncertain_fragments",
                        "lines",
                        "signs",
                        "parser_version",
                    ]
                ).dump(chapter)
            },
        )

    def query_by_transliteration(
        self, query: TransliterationQuery, pagination_index: int
    ) -> Tuple[Sequence[Chapter], int]:
        LIMIT = 30
        mongo_query = {"signs": {"$regex": query.regexp}}
        cursor = self._chapters.aggregate(
            [
                {"$match": mongo_query},
                {
                    "$lookup": {
                        "from": "texts",
                        "let": {
                            "chapterGenre": "$textId.genre",
                            "chapterCategory": "$textId.category",
                            "chapterIndex": "$textId.index",
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$genre", "$$chapterGenre"]},
                                            {"$eq": ["$category", "$$chapterCategory"]},
                                            {"$eq": ["$index", "$$chapterIndex"]},
                                        ]
                                    }
                                }
                            },
                            {"$project": {"name": 1, "_id": 0}},
                        ],
                        "as": "textNames",
                    }
                },
                {"$project": {"_id": False}},
                {"$addFields": {"textName": {"$first": "$textNames"}}},
                {"$addFields": {"textName": "$textName.name"}},
                {"$project": {"textNames": False}},
                {"$skip": LIMIT * pagination_index},
                {"$limit": LIMIT},
            ],
            allowDiskUse=True,
        )
        return ChapterSchema().load(
            filter_query_by_transliteration(query, cursor), many=True
        ), self._chapters.count_documents(mongo_query)

    def query_by_lemma(
        self, lemma: str, genre: Optional[Genre] = None
    ) -> Sequence[DictionaryLine]:
        LIMIT = 10
        lemma_query = {
            "$or": [
                {"lines.variants.reconstruction.uniqueLemma": lemma},
                {"lines.variants.manuscripts.line.content.uniqueLemma": lemma},
            ],
        }

        if genre is not None:
            lemma_query["textId.genre"] = genre.value

        lemma_lines = self._chapters.aggregate(
            [
                {"$match": lemma_query},
                {
                    "$project": {
                        "_id": False,
                        "lines": True,
                        "name": True,
                        "stage": True,
                        "textId": True,
                        "manuscripts": True,
                    }
                },
                {"$unwind": "$lines"},
                {"$match": lemma_query},
                join_text_title(),
                filter_manuscripts_by_lemma(lemma),
                {"$limit": LIMIT},
                {
                    "$project": {
                        "textId": True,
                        "textName": {"$first": "$textName.name"},
                        "chapterName": "$name",
                        "stage": True,
                        "line": "$lines",
                        "manuscripts": True,
                    }
                },
            ]
        )

        return DictionaryLineSchema().load(
            lemma_lines,
            many=True,
        )

    def query_manuscripts_by_chapter(self, id_: ChapterId) -> List[Manuscript]:
        try:
            return ManuscriptSchema().load(
                self._chapters.find_one(
                    chapter_id_query(id_), projection={"manuscripts": True}
                )["manuscripts"],
                many=True,
            )
        except NotFoundError as error:
            raise chapter_not_found(id_) from error

    def query_manuscripts_with_joins_by_chapter(
        self, id_: ChapterId
    ) -> List[Manuscript]:
        try:
            return ManuscriptSchema().load(
                self._chapters.aggregate(
                    [
                        {"$match": chapter_id_query(id_)},
                        {"$project": {"manuscripts": True}},
                        {"$unwind": "$manuscripts"},
                        {"$replaceRoot": {"newRoot": "$manuscripts"}},
                        *join_joins(),
                        *is_in_fragmentarium("museumNumber", "isInFragmentarium"),
                    ]
                ),
                many=True,
            )
        except NotFoundError as error:
            raise chapter_not_found(id_) from error

    def query_corpus_by_manuscript(
        self, museum_numbers: List[MuseumNumber]
    ) -> List[ManuscriptAttestation]:
        _museum_numbers = [
            {
                "prefix": museum_number["prefix"],
                "number": museum_number["number"],
                "suffix": museum_number["suffix"],
            }
            for museum_number in MuseumNumberSchema().dump(museum_numbers, many=True)
        ]
        cursor = self._chapters.aggregate(
            [
                {"$unwind": "$manuscripts"},
                {
                    "$set": {
                        "museumNumbers": {
                            "prefix": "$manuscripts.museumNumber.prefix",
                            "number": "$manuscripts.museumNumber.number",
                            "suffix": "$manuscripts.museumNumber.suffix",
                        }
                    }
                },
                {
                    "$match": {"museumNumbers": {"$in": _museum_numbers}},
                },
                {
                    "$replaceRoot": {
                        "newRoot": {
                            "chapterId": {
                                "textId": "$textId",
                                "stage": "$stage",
                                "name": "$name",
                            },
                            "manuscript": "$manuscripts",
                        }
                    }
                },
                *join_text(),
                {"$unwind": "$text"},
            ]
        )
        return ManuscriptAttestationSchema().load(cursor, many=True)
