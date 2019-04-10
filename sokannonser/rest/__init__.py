from flask_restplus import Api, Namespace
from market.rest import ns_market


api = Api(version='1.0', title='Search job ads',
          description='An API for searching and retrieving job ads and for finding '
          'concepts in the Jobtech Taxonomy.',
          default='sokannonser',
          default_label="An API for searching and retrieving job ads.")

ns_platsannons = Namespace('Open AF-job ads',
                           description='Search and retrieve Arbetsförmedlingens (AF) '
                           'job ads. Used for online operations.')

ns_valuestore = Namespace('Jobtech Taxonomy',
                          description='Find concepts in the Jobtech Taxonomy.')

api.add_namespace(ns_platsannons, '/open')
api.add_namespace(ns_valuestore, '/vf')
api.add_namespace(ns_market, '/')
