from collections import Sequence

from ebl.auth0 import User
from ebl.changelog import Changelog
from ebl.dictionary.application.word_repository import WordRepository
from ebl.dictionary.domain.word import WordId

COLLECTION = 'words'


class Dictionary:

    def __init__(self, repository: WordRepository, changelog: Changelog):
        self._repository = repository
        self._changelog = changelog

    def create(self, word) -> WordId:
        return self._repository.create(word)

    def find(self, id_):
        return self._repository.query_by_id(id_)

    def search(self, query: str) -> Sequence:
        return self._repository.query_by_lemma_form_or_meaning(query)

    def search_lemma(self, query: str) -> Sequence:
        return self._repository.query_by_lemma_prefix(query)

    def update(self, word, user: User) -> None:
        old_word = self.find(word['_id'])
        self._changelog.create(
            COLLECTION,
            user.profile,
            old_word,
            word
        )
        self._repository.update(word)