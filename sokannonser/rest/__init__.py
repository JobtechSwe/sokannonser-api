from flask_restx import Api, Namespace

api = Api(version='1.8.1', title='Search job ads',
          description='An API for searching and retrieving job ads and for finding '
          'concepts in the Jobtech Taxonomy.',
          default='sokannonser',
          default_label="An API for searching and retrieving job ads.")

ns_platsannons = Namespace('Open AF-job ads',
                           description='Search and retrieve Arbetsförmedlingens (AF) '
                           'job ads. Used for online operations.')

ns_valuestore = Namespace('Jobtech Taxonomy',
                          description='DEPRECATED, use https://taxonomy.api.jobtechdev.se/v1/taxonomy/swagger-ui/index.html instead')

api.add_namespace(ns_platsannons, '/')
api.add_namespace(ns_valuestore, '/taxonomy')
