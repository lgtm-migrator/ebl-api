from typing import Tuple

import factory

from ebl.dictionary.domain.word import WordId
from ebl.fragmentarium.domain.folios import Folio, Folios
from ebl.fragmentarium.domain.fragment import Fragment, UncuratedReference
from ebl.tests.factories.record import RecordFactory
from ebl.transliteration.domain import atf
from ebl.transliteration.domain.atf import Flag
from ebl.transliteration.domain.enclosure_tokens import BrokenAway
from ebl.transliteration.domain.line import TextLine
from ebl.transliteration.domain.sign_tokens import Divider, UnidentifiedSign, \
    UnclearSign, Reading, Number
from ebl.transliteration.domain.text import Text
from ebl.transliteration.domain.tokens import UnknownNumberOfSigns, \
    Tabulation, CommentaryProtocol, Column, Variant, ValueToken
from ebl.transliteration.domain.word_tokens import Word, Joiner, InWordNewline


class FragmentFactory(factory.Factory):
    class Meta:
        model = Fragment

    number = factory.Sequence(lambda n: f'X.{n}')
    cdli_number = factory.Sequence(lambda n: f'cdli-{n}')
    bm_id_number = factory.Sequence(lambda n: f'bmId-{n}')
    accession = factory.Sequence(lambda n: f'accession-{n}')
    museum = factory.Faker('word')
    collection = factory.Faker('word')
    publication = factory.Faker('sentence')
    description = factory.Faker('text')
    script = factory.Iterator(['NA', 'NB'])
    folios = Folios((
        Folio('WGL', '1'),
        Folio('XXX', '1')
    ))


class InterestingFragmentFactory(FragmentFactory):
    collection = 'Kuyunjik'
    publication = ''
    joins: Tuple[str, ...] = tuple()
    text = Text()
    uncurated_references = (
        UncuratedReference('7(0)'),
        UncuratedReference('CAD 51', (34, 56)),
        UncuratedReference('7(1)')
    )


class TransliteratedFragmentFactory(FragmentFactory):
    text = Text((
        TextLine("1'.", (
            Word('X', parts=[UnidentifiedSign()]),
            Column(),
            Tabulation('($___$)'),
            Word('[...-ku]-nu-ši', parts=[
                ValueToken('['), UnknownNumberOfSigns(),
                Joiner(atf.Joiner.HYPHEN), Reading.of('ku'),
                ValueToken(']'), Joiner(atf.Joiner.HYPHEN),
                Reading.of('nu'), Joiner(atf.Joiner.HYPHEN),
                Reading.of('ši')
            ]),
            Variant.of(Divider(':'), Word('ku', parts=[Reading.of('ku')])),
            BrokenAway('['),
            UnknownNumberOfSigns(),
            BrokenAway(']'),
            Column(2),
            Divider(':', ('@v',), (Flag.DAMAGE,)),
            CommentaryProtocol('!qt'),
            Word('10#', parts=[Number.of(10, [], [Flag.DAMAGE])])
        )),
        TextLine("2'.", (
            BrokenAway('['),
            UnknownNumberOfSigns(),
            BrokenAway(']'),
            Word('GI₆', parts=[ValueToken('GI₆')]),
            Word('ana', parts=[Reading.of('ana')]),
            Word('u₄-š[u', parts=[Reading.of('u₄'), Joiner(atf.Joiner.HYPHEN),
                                  Reading.of('š[u')]),
            UnknownNumberOfSigns(),
            BrokenAway(']'),
        )),
        TextLine("3'.", (
            BrokenAway('['),
            UnknownNumberOfSigns(),
            Word('k]i-du', parts=[Reading.of('k]i'), Joiner(atf.Joiner.HYPHEN),
                                  Reading.of('du')]),
            Word('u', parts=[Reading.of('u')]),
            Word('ba-ma-t[i', parts=[
                Reading.of('ba'), Joiner(atf.Joiner.HYPHEN), Reading.of('ma'),
                Joiner(atf.Joiner.HYPHEN), Reading.of('t[i')
            ]),
            UnknownNumberOfSigns(),
            BrokenAway(']'),
        )),
        TextLine("6'.", (
            BrokenAway('['),
            UnknownNumberOfSigns(),
            BrokenAway(']'),
            Word('x#', parts=[UnclearSign([Flag.DAMAGE])]),
            Word('mu', parts=[Reading.of('mu')]),
            Word('ta-ma;-tu₂', parts=[
                Reading.of('ta'), Joiner(atf.Joiner.HYPHEN), Reading.of('ma'),
                InWordNewline(), Joiner(atf.Joiner.HYPHEN), Reading.of('tu₂')
            ])
        )),
        TextLine("7'.", (
            Word('šu/|BI×IS|', parts=[ValueToken('šu/|BI×IS|')]),
        ))
    ))
    signs = (
        'X KU ABZ075 ABZ207a\\u002F207b\\u0020X ABZ377n1/KU ABZ377n1 ABZ411\n'
        'MI DIŠ UD ŠU\n'
        'KI DU ABZ411 BA MA TI\n'
        'X MU TA MA UD\n'
        'ŠU/|BI×IS|'
    )
    folios = Folios((
        Folio('WGL', '3'),
        Folio('XXX', '3')
    ))
    record = factory.SubFactory(RecordFactory)


class LemmatizedFragmentFactory(TransliteratedFragmentFactory):
    text = Text((
        TextLine("1'.", (
            Word('X', parts=[UnidentifiedSign()]),
            Column(),
            Tabulation('($___$)'),
            Word('[...-ku]-nu-ši', parts=[
                ValueToken('['), UnknownNumberOfSigns(),
                Joiner(atf.Joiner.HYPHEN), Reading.of('ku'),
                ValueToken(']'), Joiner(atf.Joiner.HYPHEN),
                Reading.of('nu'), Joiner(atf.Joiner.HYPHEN),
                Reading.of('ši')
            ]),
            Variant.of(Divider(':'), Word('ku', parts=[Reading.of('ku')])),
            BrokenAway('['),
            UnknownNumberOfSigns(),
            BrokenAway(']'),
            Column(2),
            Divider(':', ('@v',), (Flag.DAMAGE,)),
            CommentaryProtocol('!qt'),
            Word('10#', parts=[Number.of(10, [], [Flag.DAMAGE])])
        )),
        TextLine("2'.", (
            BrokenAway('['),
            UnknownNumberOfSigns(),
            Word('GI₆', unique_lemma=(WordId('ginâ I'),),
                 parts=[ValueToken('GI₆')]),
            Word('ana', unique_lemma=(WordId('ana I'),),
                 parts=[Reading.of('ana')]),
            Word('u₄-š[u', unique_lemma=(WordId("ūsu I"),),
                 parts=[Reading.of('u₄'), Joiner(atf.Joiner.HYPHEN),
                        Reading.of('š[u')]),
            UnknownNumberOfSigns(),
            BrokenAway(']'),
        )),
        TextLine("3'.", (
            BrokenAway('['),
            UnknownNumberOfSigns(),
            Word('k]i-du', unique_lemma=(WordId('kīdu I'),), parts=[
                Reading.of('k]i'), Joiner(atf.Joiner.HYPHEN),
                Reading.of('du')
            ]),
            Word('u', unique_lemma=(WordId('u I'),),
                 parts=[Reading.of('u')]),
            Word('ba-ma-t[i', unique_lemma=(WordId('bamātu I'),), parts=[
                Reading.of('ba'), Joiner(atf.Joiner.HYPHEN),
                Reading.of('ma'), Joiner(atf.Joiner.HYPHEN),
                Reading.of('t[i')
            ]),
            UnknownNumberOfSigns(),
            BrokenAway(']'),
        )),
        TextLine("6'.", (
            BrokenAway('['),
            UnknownNumberOfSigns(),
            BrokenAway(']'),
            Word('x#', parts=[UnclearSign([Flag.DAMAGE])]),
            Word('mu', unique_lemma=(WordId('mu I'),),
                 parts=[Reading.of('mu')]),
            Word('ta-ma;-tu₂', unique_lemma=(WordId('tamalāku I'),), parts=[
                Reading.of('ta'), Joiner(atf.Joiner.HYPHEN), Reading.of('ma'),
                InWordNewline(), Joiner(atf.Joiner.HYPHEN), Reading.of('tu', 2)
            ])
        )),
        TextLine("7'.", (
            Word('šu/|BI×IS|', parts=[ValueToken('šu/|BI×IS|')]),
        ))
    ))
