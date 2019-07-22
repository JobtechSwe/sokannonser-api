from flask_restplus import Api, Namespace
import elasticapm
from flask import request
from jobtech.common import settings


def apm_user_context():
    def real_apm_user_context_decorator(func):
        def wrapper(*args, **kwargs):
            apikey = request.headers.get(settings.APIKEY)
            if apikey:
                elasticapm.set_user_context(user_id=apikey)
        return wrapper
    return real_apm_user_context_decorator


api = Api(version='1.3.0', title='Search job ads',
          description='An API for searching and retrieving job ads and for finding '
          'concepts in the Jobtech Taxonomy.',
          default='sokannonser',
          default_label="An API for searching and retrieving job ads.")

ns_platsannons = Namespace('Open AF-job ads',
                           description='Search and retrieve Arbetsförmedlingens (AF) '
                           'job ads. Used for online operations.')

ns_valuestore = Namespace('Jobtech Taxonomy',
                          description='Find concepts in the Jobtech Taxonomy.')

api.add_namespace(ns_platsannons, '/')
api.add_namespace(ns_valuestore, '/taxonomy')
