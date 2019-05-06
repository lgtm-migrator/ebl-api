from ebl.corpus.api_serializer import serialize, deserialize
from ebl.tests.factories.bibliography import ReferenceWithDocumentFactory, \
    ReferenceFactory
from ebl.tests.factories.corpus import ManuscriptFactory, \
    ManuscriptLineFactory, LineFactory, ChapterFactory, TextFactory


def create(include_documents):
    references = ((ReferenceWithDocumentFactory if include_documents
                   else ReferenceFactory).build(), )
    manuscript = ManuscriptFactory.build(references=references)
    manuscript_line = ManuscriptLineFactory.build()
    line = LineFactory.build(manuscripts=(manuscript_line, ))
    chapter = ChapterFactory.build(manuscripts=(manuscript, ), lines=(line, ))
    text = TextFactory.build(chapters=(chapter, ))
    dto = {
        'category': text.category,
        'index': text.index,
        'name': text.name,
        'numberOfVerses': text.number_of_verses,
        'approximateVerses': text.approximate_verses,
        'chapters': [
            {
                'classification': chapter.classification.value,
                'stage': chapter.stage.value,
                'version': chapter.version,
                'name': chapter.name,
                'order': chapter.order,
                'manuscripts': [
                    {
                        'id': manuscript.id,
                        'siglumDisambiguator': manuscript.siglum_disambiguator,
                        'museumNumber': manuscript.museum_number,
                        'accession': manuscript.accession,
                        'periodModifier': manuscript.period_modifier.value,
                        'period': manuscript.period.long_name,
                        'provenance': manuscript.provenance.long_name,
                        'type': manuscript.type.long_name,
                        'notes': manuscript.notes,
                        'references': [
                            reference.to_dict(include_documents)
                            for reference in references
                        ]
                    }
                ],
                'lines': [
                    {
                        'number': line.number.to_value(),
                        'reconstruction': line.reconstruction,
                        'manuscripts': [{
                            'manuscriptId': manuscript_line.manuscript_id,
                            'labels': [label.to_value()
                                       for label in manuscript_line.labels],
                            'number': manuscript_line.line.prefix[:-1],
                            'atf': (manuscript_line.line
                                    .atf[len(manuscript_line
                                             .line.prefix) + 1:])
                        }]
                    }
                ]
            }
        ]
    }

    return text, dto


def test_serialize():
    text, dto = create(True)
    assert serialize(text) == dto


def test_deserialize():
    text, dto = create(False)
    assert deserialize(dto) == text