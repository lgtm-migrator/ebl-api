import operator
import re
from typing import List, Sequence, Dict, Optional

import pydash
import pymongo
from marshmallow import EXCLUDE

from ebl.bibliography.infrastructure.bibliography import join_reference_documents
from ebl.errors import NotFoundError
from ebl.fragmentarium.application.fragment_info_schema import FragmentInfoSchema
from ebl.fragmentarium.application.fragment_repository import FragmentRepository
from ebl.fragmentarium.application.fragment_schema import FragmentSchema
from ebl.fragmentarium.application.joins_schema import JoinSchema
from ebl.fragmentarium.application.line_to_vec import LineToVecEntry
from ebl.fragmentarium.application.museum_number_schema import MuseumNumberSchema
from ebl.fragmentarium.domain.joins import Join
from ebl.fragmentarium.domain.line_to_vec_encoding import LineToVecEncoding
from ebl.fragmentarium.domain.museum_number import MuseumNumber
from ebl.fragmentarium.infrastructure import collections
from ebl.fragmentarium.infrastructure.queries import (
    HAS_TRANSLITERATION,
    aggregate_latest,
    aggregate_needs_revision,
    aggregate_path_of_the_pioneers,
    aggregate_random,
    fragment_is,
    join_joins,
    museum_number_is,
    number_is,
)
from ebl.mongo_collection import MongoCollection


def has_none_values(dictionary: dict) -> bool:
    return not all(dictionary.values())


class MongoFragmentRepository(FragmentRepository):
    def __init__(self, database):
        self._fragments = MongoCollection(database, collections.FRAGMENTS_COLLECTION)
        self._joins = MongoCollection(database, collections.JOINS_COLLECTION)

    def create_indexes(self) -> None:
        self._fragments.create_index(
            [
                ("museumNumber.prefix", pymongo.ASCENDING),
                ("museumNumber.number", pymongo.ASCENDING),
                ("museumNumber.suffix", pymongo.ASCENDING),
            ],
            unique=True,
        )
        self._fragments.create_index([("accession", pymongo.ASCENDING)])
        self._fragments.create_index([("cdliNumber", pymongo.ASCENDING)])
        self._fragments.create_index([("folios.name", pymongo.ASCENDING)])
        self._fragments.create_index(
            [
                ("text.lines.content.value", pymongo.ASCENDING),
                ("text.lines.content.uniqueLemma.0", pymongo.ASCENDING),
            ]
        )
        self._fragments.create_index([("text.lines.type", pymongo.ASCENDING)])
        self._fragments.create_index([("record.type", pymongo.ASCENDING)])
        self._fragments.create_index(
            [
                ("publication", pymongo.ASCENDING),
                ("joins", pymongo.ASCENDING),
                ("collection", pymongo.ASCENDING),
            ]
        )
        self._joins.create_index(
            [
                ("fragments.museumNumber.prefix", pymongo.ASCENDING),
                ("fragments.museumNumber.number", pymongo.ASCENDING),
                ("fragments.museumNumber.suffix", pymongo.ASCENDING),
            ]
        )

    def count_transliterated_fragments(self):
        return self._fragments.count_documents(HAS_TRANSLITERATION)

    def count_lines(self):
        result = self._fragments.aggregate(
            [{"$group": {"_id": None, "total": {"$sum": "$text.numberOfLines"}}}]
        )
        try:
            return next(result)["total"]
        except StopIteration:
            return 0

    def create(self, fragment):
        return self._fragments.insert_one(
            {
                "_id": str(fragment.number),
                **FragmentSchema(exclude=["joins"]).dump(fragment),
            }
        )

    def create_join(self, joins: Sequence[Sequence[Join]]) -> None:
        self._joins.insert_one(
            {
                "fragments": [
                    {
                        **JoinSchema(exclude=["is_in_fragmentarium"]).dump(join),
                        "group": index,
                    }
                    for index, group in enumerate(joins)
                    for join in group
                ]
            }
        )

    def query_by_museum_number(self, number: MuseumNumber):
        data = self._fragments.aggregate(
            [
                {"$match": museum_number_is(number)},
                *join_reference_documents(),
                *join_joins(),
            ]
        )
        try:
            return FragmentSchema(unknown=EXCLUDE).load(next(data))
        except StopIteration as error:
            raise NotFoundError(f"Fragment {number} not found.") from error

    def query_by_id_and_page_in_references(self, id_: str, pages: str):
        match: dict = {"references": {"$elemMatch": {"id": id_}}}
        if pages:
            match["references"]["$elemMatch"]["pages"] = {
                "$regex": fr".*?(^|[^\d]){pages}([^\d]|$).*?"
            }
        cursor = self._fragments.find_many(match, projection={"joins": False})
        return self._map_fragments(cursor)

    def query_by_fragment_cdli_or_accession_number(self, number):
        cursor = self._fragments.find_many(
            number_is(number), projection={"joins": False}
        )

        return self._map_fragments(cursor)

    def query_random_by_transliterated(self):
        cursor = self._fragments.aggregate(
            [*aggregate_random(), {"$project": {"joins": False}}]
        )

        return self._map_fragments(cursor)

    def query_path_of_the_pioneers(self):
        cursor = self._fragments.aggregate(
            [*aggregate_path_of_the_pioneers(), {"$project": {"joins": False}}]
        )

        return self._map_fragments(cursor)

    def query_transliterated_numbers(self):
        cursor = self._fragments.find_many(
            HAS_TRANSLITERATION, projection=["museumNumber"]
        ).sort("_id", pymongo.ASCENDING)

        return MuseumNumberSchema(many=True).load(
            fragment["museumNumber"] for fragment in cursor
        )

    def query_transliterated_line_to_vec(self) -> List[LineToVecEntry]:
        cursor = self._fragments.find_many(HAS_TRANSLITERATION, {"text": False})
        return [
            LineToVecEntry(
                MuseumNumberSchema().load(fragment["museumNumber"]),
                fragment["script"],
                tuple(
                    LineToVecEncoding.from_list(line_to_vec)
                    for line_to_vec in fragment["lineToVec"]
                ),
            )
            for fragment in cursor
        ]

    def query_by_transliterated_sorted_by_date(self):
        cursor = self._fragments.aggregate(
            [*aggregate_latest(), {"$project": {"joins": False}}]
        )
        return self._map_fragments(cursor)

    def query_by_transliterated_not_revised_by_other(self):
        cursor = self._fragments.aggregate(
            [*aggregate_needs_revision(), {"$project": {"joins": False}}],
            allowDiskUse=True,
        )
        return FragmentInfoSchema(many=True).load(cursor)

    def query_by_transliteration(self, query):
        cursor = self._fragments.find_many(
            {"signs": {"$regex": query.regexp}}, limit=100, projection={"joins": False}
        )
        return self._map_fragments(cursor)

    def update_transliteration(self, fragment):
        self._fragments.update_one(
            fragment_is(fragment),
            {
                "$set": FragmentSchema(
                    only=("text", "notes", "signs", "record", "line_to_vec")
                ).dump(fragment)
            },
        )

    def update_genres(self, fragment):
        self._fragments.update_one(
            fragment_is(fragment),
            {"$set": FragmentSchema(only=("genres",)).dump(fragment)},
        )

    def update_lemmatization(self, fragment):
        self._fragments.update_one(
            fragment_is(fragment),
            {"$set": FragmentSchema(only=("text",)).dump(fragment)},
        )

    def query_next_and_previous_folio(self, folio_name, folio_number, number):
        sort_ascending = {"$sort": {"key": 1}}
        sort_descending = {"$sort": {"key": -1}}

        def create_pipeline(*parts):
            return [
                {"$match": {"folios.name": folio_name}},
                {"$unwind": "$folios"},
                {
                    "$project": {
                        "name": "$folios.name",
                        "number": "$folios.number",
                        "key": {"$concat": ["$folios.number", "-", "$_id"]},
                    }
                },
                {"$match": {"name": folio_name}},
                *parts,
                {"$limit": 1},
            ]

        def get_numbers(pipeline):
            cursor = self._fragments.aggregate(pipeline)
            try:
                entry = next(cursor)
                return {"fragmentNumber": entry["_id"], "folioNumber": entry["number"]}
            except StopIteration:
                return None

        first = create_pipeline(sort_ascending)
        previous = create_pipeline(
            {"$match": {"key": {"$lt": f"{folio_number}-{number}"}}}, sort_descending
        )
        next_ = create_pipeline(
            {"$match": {"key": {"$gt": f"{folio_number}-{number}"}}}, sort_ascending
        )
        last = create_pipeline(sort_descending)

        result = {
            "previous": get_numbers(previous) or get_numbers(last),
            "next": get_numbers(next_) or get_numbers(first),
        }

        if has_none_values(result):
            raise NotFoundError("Could not retrieve any fragments")
        else:
            return result

    def query_next_and_previous_fragment(
        self, museum_number: MuseumNumber
    ) -> Dict[str, MuseumNumber]:
        def retrieve_all_museum_number_by_prefix(regex: str):
            return self._fragments.aggregate(
                [
                    {"$project": {"_id": 0, "museumNumber": 1}},
                    {
                        "$match": {
                            "museumNumber.prefix": {"$regex": regex, "$options": "i"}
                        }
                    },
                ]
            )

        def find_adjacent_museum_number_from_list(
            museum_number: MuseumNumber, cursor, revert_order=False
        ):
            comp = operator.lt if not revert_order else operator.gt
            current_prev = None
            current_next = None
            for current_cursor in cursor:
                current_museum_number = MuseumNumberSchema().load(
                    current_cursor["museumNumber"]
                )
                if comp(current_museum_number, museum_number) and (
                    not current_prev or current_museum_number > current_prev
                ):
                    current_prev = current_museum_number
                if comp(museum_number, current_museum_number) and (
                    not current_next or current_museum_number < current_next
                ):
                    current_next = current_museum_number
            return current_prev, current_next

        def find_prev_and_next(
            museum_number: MuseumNumber, regex: str, revert_order=False
        ):
            cursor = retrieve_all_museum_number_by_prefix(regex)
            return find_adjacent_museum_number_from_list(
                museum_number, cursor, revert_order
            )

        def get_prefix_order_number(prefix: str) -> int:
            for order_elem in ORDER:
                regex, order_number = order_elem
                if match := re.match(regex, prefix.lower()):
                    return order_number
            raise ValueError("Prefix doesn't match any of the expected Prefixes")

        def get_adjacent_prefix(prefix: str, counter: int) -> str:
            return ORDER[(get_prefix_order_number(prefix) + counter) % len(ORDER)][0]

        ORDER = [
            ("^k$", 0),
            ("^sm$", 1),
            ("^dt$", 2),
            ("^rm$", 3),
            (r"^rm\-ii$", 4),
            (r"^\d*$", 5),
            ("^bm$", 6),
            ("^cbs$", 7),
            ("^um$", 8),
            ("^n$", 9),
            (r"^[abcdefghijlmopqrstuvwxyz]$|^((?!^\d*$).)*$", 10),
        ]
        prefix = museum_number.prefix
        query = ORDER[get_prefix_order_number(prefix)][0]

        prev, next = find_prev_and_next(museum_number, query)

        def is_order_reverted(
            order_number: int, adjacent_order_number: int, prev_or_next: int
        ):
            if prev_or_next == 1:
                return adjacent_order_number < order_number
            else:
                return adjacent_order_number > order_number

        def iterate_until_found(
            adjacent_museum_number: Optional[MuseumNumber], counter: int
        ) -> MuseumNumber:
            order_number = get_prefix_order_number(prefix)
            for i in range(len(ORDER)):
                if not adjacent_museum_number:
                    regex_query = get_adjacent_prefix(prefix, (i + 1) * counter)
                    current_query_order = pydash.find_index(
                        ORDER, lambda x: x[0] == regex_query
                    )
                    is_reverted = is_order_reverted(
                        order_number, current_query_order, counter
                    )
                    adjacent_museum_number = find_prev_and_next(
                        museum_number, regex_query, is_reverted
                    )[0 if counter == -1 else 1]
                else:
                    return adjacent_museum_number
            raise NotFoundError("Could not retrieve any fragments")

        return {
            "previous": iterate_until_found(prev, -1),
            "next": iterate_until_found(next, 1),
        }

    def update_references(self, fragment):
        self._fragments.update_one(
            fragment_is(fragment),
            {"$set": FragmentSchema(only=("references",)).dump(fragment)},
        )

    def _map_fragments(self, cursor):
        return FragmentSchema(unknown=EXCLUDE, many=True).load(cursor)
