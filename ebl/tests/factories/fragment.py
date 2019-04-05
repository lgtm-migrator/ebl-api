from typing import Tuple
import factory

from ebl.fragment.folios import Folios, Folio
from ebl.fragment.fragment import Fragment, UncuratedReference
from ebl.text.line import TextLine
from ebl.text.text import Text
from ebl.text.token import Token, Word

from ebl.tests.factories.record import RecordFactory


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
            Token('[...'),
            Word('-ku]-nu-ši'),
            Token('[...]')
        )),
        TextLine("2'.", (
            Token('[...]'),
            Word('GI₆'),
            Word('ana'),
            Word('u₄-š[u'),
            Token('...]')
        )),
        TextLine("3'.", (
            Token('[...'),
            Word('k]i-du'),
            Word('u'),
            Word('ba-ma-t[i'),
            Token('...]')
        )),
        TextLine("6'.", (
            Token('[...]'),
            Word('x'),
            Word('mu'),
            Word('ta-ma-tu₂')
        )),
        TextLine("7'.", (
            Word('šu/|BI×IS|'),
        ))
    ))
    signs = (
        'KU NU IGI\n'
        'MI DIŠ UD ŠU\n'
        'KI DU U BA MA TI\n'
        'X MU TA MA UD\n'
        'ŠU/|BI×IS|'
    )
    folios = Folios((
        Folio('WGL', '3'),
        Folio('XXX', '3')
    ))
    record = factory.SubFactory(RecordFactory)