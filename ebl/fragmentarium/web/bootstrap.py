import falcon

from ebl.context import Context
from ebl.dictionary.application.dictionary import Dictionary
from ebl.fragmentarium.application.annotations_service import AnnotationsService
from ebl.fragmentarium.application.fragment_finder import FragmentFinder
from ebl.fragmentarium.application.fragment_matcher import FragmentMatcher
from ebl.fragmentarium.application.fragmentarium import Fragmentarium
from ebl.fragmentarium.web.annotations import AnnotationResource
from ebl.fragmentarium.web.folio_pager import FolioPagerResource
from ebl.fragmentarium.web.folios import FoliosResource
from ebl.fragmentarium.web.fragment_genre import FragmentGenreResource
from ebl.fragmentarium.web.fragment_matcher import FragmentMatcherResource
from ebl.fragmentarium.web.fragment_pager import make_fragment_pager_resource
from ebl.fragmentarium.web.fragment_search import FragmentSearch
from ebl.fragmentarium.web.fragments import FragmentsResource
from ebl.fragmentarium.web.genres import GenresResource
from ebl.fragmentarium.web.lemmatizations import LemmatizationResource
from ebl.fragmentarium.web.photo import PhotoResource
from ebl.fragmentarium.web.references import ReferencesResource
from ebl.fragmentarium.web.statistics import make_statistics_resource
from ebl.fragmentarium.web.transliterations import TransliterationResource
from ebl.fragmentarium.web.introductions import IntroductionResource
from ebl.corpus.web.chapters import ChaptersByManuscriptResource
from ebl.corpus.application.corpus import Corpus


def create_fragmentarium_routes(api: falcon.App, context: Context):
    context.fragment_repository.create_indexes()
    fragmentarium = Fragmentarium(context.fragment_repository)
    finder = FragmentFinder(
        context.get_bibliography(),
        context.fragment_repository,
        Dictionary(context.word_repository, context.changelog),
        context.photo_repository,
        context.folio_repository,
        context.parallel_line_injector,
    )
    updater = context.get_fragment_updater()
    annotations_service = AnnotationsService(
        context.ebl_ai_client,
        context.annotations_repository,
        context.photo_repository,
        context.changelog,
        context.fragment_repository,
        context.photo_repository,
        context.cropped_sign_images_repository,
    )
    corpus = Corpus(
        context.text_repository,
        context.get_bibliography(),
        context.changelog,
        context.sign_repository,
        context.parallel_line_injector,
    )

    statistics = make_statistics_resource(context.cache, fragmentarium)
    fragments = FragmentsResource(finder)
    fragment_genre = FragmentGenreResource(updater)

    fragment_matcher = FragmentMatcherResource(
        FragmentMatcher(context.fragment_repository)
    )
    fragment_search = FragmentSearch(
        fragmentarium,
        finder,
        context.get_transliteration_query_factory(),
        context.cache,
    )
    genres = GenresResource()
    lemmatization = LemmatizationResource(updater)
    references = ReferencesResource(updater)
    transliteration = TransliterationResource(
        updater, context.get_transliteration_update_factory()
    )
    introduction = IntroductionResource(updater)
    annotations = AnnotationResource(annotations_service)
    fragment_pager = make_fragment_pager_resource(finder, context.cache)
    folio_pager = FolioPagerResource(finder)
    photo = PhotoResource(finder)
    folios = FoliosResource(finder)
    chapters = ChaptersByManuscriptResource(corpus, finder)

    routes = [
        ("/fragments", fragment_search),
        ("/fragments/{number}/match", fragment_matcher),
        ("/fragments/{number}/genres", fragment_genre),
        ("/fragments/{number}", fragments),
        ("/fragments/{number}/pager", fragment_pager),
        ("/fragments/{number}/lemmatization", lemmatization),
        ("/fragments/{number}/references", references),
        ("/fragments/{number}/transliteration", transliteration),
        ("/fragments/{number}/introduction", introduction),
        ("/fragments/{number}/annotations", annotations),
        ("/fragments/{number}/photo", photo),
        ("/fragments/{number}/corpus", chapters),
        ("/genres", genres),
        ("/statistics", statistics),
        ("/fragments/{number}/pager/{folio_name}/{folio_number}", folio_pager),
        ("/folios/{name}/{number}", folios),
    ]

    for uri, resource in routes:
        api.add_route(uri, resource)
