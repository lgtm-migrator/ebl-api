from typing import Tuple

from ebl.auth0 import User
from ebl.bibliography.domain.reference import Reference
from ebl.fragmentarium.application.fragment_repository import \
    FragmentRepository
from ebl.fragmentarium.application.transliteration_update import \
    TransliterationUpdate
from ebl.fragmentarium.domain.fragment import Fragment, FragmentNumber
from ebl.transliteration.lemmatization import Lemmatization

COLLECTION = 'fragments'


class FragmentUpdater:

    def __init__(self,
                 repository: FragmentRepository,
                 changelog,
                 bibliography):

        self._repository = repository
        self._changelog = changelog
        self._bibliography = bibliography

    def update_transliteration(self,
                               number: FragmentNumber,
                               transliteration: TransliterationUpdate,
                               user: User) -> Fragment:
        fragment = self._repository.find(number)

        updated_fragment = fragment.update_transliteration(
            transliteration,
            user
        )

        self._create_changlelog(user, fragment, updated_fragment)
        self._repository.update_transliteration(updated_fragment)

        return updated_fragment

    def update_lemmatization(self,
                             number: FragmentNumber,
                             lemmatization: Lemmatization,
                             user: User) -> Fragment:
        fragment = self._repository.find(number)
        updated_fragment = fragment.update_lemmatization(
            lemmatization
        )

        self._create_changlelog(user, fragment, updated_fragment)
        self._repository.update_lemmatization(updated_fragment)

        return updated_fragment

    def update_references(self,
                          number: FragmentNumber,
                          references: Tuple[Reference, ...],
                          user: User) -> Fragment:
        fragment = self._repository.find(number)
        self._bibliography.validate_references(references)

        updated_fragment = fragment.set_references(references)

        self._create_changlelog(user, fragment, updated_fragment)
        self._repository.update_references(updated_fragment)

        return updated_fragment

    def _create_changlelog(self,
                           user: User,
                           fragment: Fragment,
                           updated_fragment: Fragment) -> None:
        self._changelog.create(
            COLLECTION,
            user.profile,
            fragment.to_dict(),
            updated_fragment.to_dict()
        )