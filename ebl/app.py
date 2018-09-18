import os
from base64 import b64decode

import falcon
from falcon_auth import FalconAuthMiddleware, JWTAuthBackend

from pymongo import MongoClient
import requests

from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

from ebl.cors_component import CORSComponent

from ebl.dictionary.dictionary import MongoDictionary
from ebl.dictionary.words import WordsResource
from ebl.dictionary.word_search import WordSearch
from ebl.fragmentarium.fragmentarium import Fragmentarium
from ebl.fragmentarium.fragments import FragmentsResource
from ebl.fragmentarium.statistics import StatisticsResource
from ebl.sign_list.sign_list import SignList
from ebl.fragmentarium.fragment_search import FragmentSearch
from ebl.files.files import FilesResource
from ebl.files.file_repository import GridFsFiles
from ebl.fragmentarium.fragment_repository import MongoFragmentRepository
from ebl.changelog import Changelog
from ebl.sign_list.sign_repository import MongoSignRepository


def auth0_user_loader(token):
    return token


def create_auth0_backend():
    certificate = b64decode(os.environ['AUTH0_PEM'])
    cert_obj = load_pem_x509_certificate(certificate, default_backend())
    public_key = cert_obj.public_key()

    return JWTAuthBackend(
        auth0_user_loader,
        public_key,
        algorithm='RS256',
        auth_header_prefix='Bearer',
        audience=os.environ['AUTH0_AUDIENCE'],
        issuer=os.environ['AUTH0_ISSUER'],
        verify_claims=['signature', 'exp', 'iat'],
        required_claims=['exp', 'iat', 'openid', 'read:words']
    )


def fetch_auth0_user_profile(req):
    issuer = os.environ['AUTH0_ISSUER']
    url = f'{issuer}userinfo'
    headers = {'Authorization': req.get_header('Authorization', True)}
    return requests.get(url, headers=headers).json()


def create_app(context):
    auth_middleware = FalconAuthMiddleware(context['auth_backend'])
    api = falcon.API(middleware=[CORSComponent(), auth_middleware])

    sign_list = SignList(context['sign_repository'])

    fragmentarium = Fragmentarium(context['fragment_repository'],
                                  context['changelog'],
                                  sign_list)

    words = WordsResource(context['dictionary'], context['fetch_user_profile'])
    word_search = WordSearch(context['dictionary'])
    fragments = FragmentsResource(fragmentarium,
                                  context['fetch_user_profile'])
    fragment_search = FragmentSearch(fragmentarium)
    statistics = StatisticsResource(fragmentarium)
    files = FilesResource(context['files'])

    api.add_route('/words', word_search)
    api.add_route('/words/{object_id}', words)
    api.add_route('/fragments', fragment_search)
    api.add_route('/fragments/{number}', fragments)
    api.add_route('/images/{file_name}', files)
    api.add_route('/statistics', statistics)

    return api


def get_app():
    client = MongoClient(os.environ['MONGODB_URI'])
    database = client.get_database()

    context = {
        'auth_backend': create_auth0_backend(),
        'dictionary': MongoDictionary(database),
        'sign_repository': MongoSignRepository(database),
        'files': GridFsFiles(database),
        'fetch_user_profile': fetch_auth0_user_profile,
        'fragment_repository': MongoFragmentRepository(database),
        'changelog': Changelog(database)
    }

    return create_app(context)
