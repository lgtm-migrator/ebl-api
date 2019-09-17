from typing import Sequence

import pydash

from ebl.fragment.value import SignMap, Value


class SignList:

    def __init__(self, sign_repository):
        self._repository = sign_repository

    def create(self, sign):
        return self._repository.create(sign)

    def find(self, sign_name):
        return self._repository.find(sign_name)

    def search(self, reading, sub_index):
        return self._repository.search(reading, sub_index)

    def map_readings(
        self, values: Sequence[Sequence[Value]]
    ) -> Sequence[Sequence[str]]:
        def sign_to_pair(sign):
            return [
                [(value.value, value.sub_index), sign.name]
                for value in sign.values
            ]

        sign_map: SignMap = (
            pydash
            .chain(values)
            .flatten()
            .flat_map(lambda reading: reading.keys)
            .thru(self._repository.search_many)
            .flat_map(sign_to_pair)
            .from_pairs()
            .value()
        )

        return [
            [
                reading.to_sign(sign_map)
                for reading in row
            ]
            for row in values
        ]
