from pymongo.errors import DuplicateKeyError
from ebl.errors import NotFoundError, DuplicateError


class MongoRepository:

    def __init__(self, database, collection):
        self._database = database
        self.collection = collection

    def get_collection(self):
        return self._database[self.collection]

    def create(self, document):
        try:
            return self.get_collection().insert_one(document).inserted_id
        except DuplicateKeyError:
            raise DuplicateError(f'Resource {document["_id"]} already exists.')

    def find(self, object_id):
        document = self.get_collection().find_one({'_id': object_id})

        if document is None:
            raise NotFoundError(f'Resource {object_id} not found.')
        else:
            return document
