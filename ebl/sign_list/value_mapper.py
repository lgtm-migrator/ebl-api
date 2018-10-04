import re
import unicodedata


BROKEN_PATTERN = r'x'
WITH_SIGN_PATTERN = r'[^\(/\|]+\((.+)\)|'
NUMBER_PATTERN = r'\d+'
GRAPHEME_PATTERN =\
    r'\|?(\d*[.x×%&+@]?\(?[A-ZṢŠṬ₀-₉]+([@~][a-z0-9]+)*\)?)+\|?'
READING_PATTERN = r'([^₀-₉ₓ/]+)([₀-₉ₓ]+)?'
VARIANT_PATTERN = r'([^/]+)(?:/([^/]+))+'
UNKNOWN_SIGN = '?'
BROKEN_SIGN = 'X'


def unicode_to_int(string):
    return int(unicodedata.normalize('NFKC', string))


def get_group(group):
    return lambda match: match.group(group)


def create_value_mapper(sign_repository):
    def map_(value):
        factories = [
            (BROKEN_PATTERN, lambda _: BROKEN_SIGN),
            (WITH_SIGN_PATTERN, lambda match: match.group(1)),
            (NUMBER_PATTERN, map_number),
            (GRAPHEME_PATTERN, lambda match: match.group(0)),
            (READING_PATTERN, map_reading),
            (VARIANT_PATTERN, map_variant)
        ]

        return next((
            factory(match)
            for match, factory in [
                (re.fullmatch(pattern, value), factory)
                for pattern, factory in factories
            ]
            if match
        ), UNKNOWN_SIGN)

    def map_number(match):
        value = match.group(0)
        return search_or_default(value, 1, value)

    def map_reading(match):
        value = match.group(1)
        sub_index = (
            unicode_to_int(match.group(2))
            if match.group(2)
            else 1
        )
        return search_or_default(value, sub_index, UNKNOWN_SIGN)

    def map_variant(match):
        return '/'.join([
            map_(part)
            for part
            in match.group(0).split('/')
        ])

    def search_or_default(value, sub_index, default):
        sign = sign_repository.search(value, sub_index)
        return sign['_id'] if sign else default

    return map_