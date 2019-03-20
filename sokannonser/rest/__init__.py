from flask_restplus import Api, Namespace

api = Api(version='1.0', title='Search job ads',
          description='An API for searching and retrieving job ads and for finding '
          'concepts in the Jobtech Taxonomy.',
          default='sokannonser',
          default_label="An API for searching and retrieving job ads.")

ns_platsannons = Namespace('AF-job ads',
                           description='Search and retrieve Arbetsförmedlingens (AF) '
                           'job ads. Used for online operations.')
ns_auranest = Namespace('All job ads',
                        description='Search and retrieve ~97% of all job ads.')

ns_open = Namespace('Open-API',
                    description='Search and retrieve Arbetsförmedlingens (AF) job ads.')

ns_bulk = Namespace('Bulk loader', description='Endpoint for downloading all ads in '
                    'zip-file formt.')

ns_valuestore = Namespace('Jobtech Taxonomy',
                          description='Find concepts in the Jobtech Taxonomy.')

api.add_namespace(ns_open, '/open')
api.add_namespace(ns_bulk, '/bulk')
api.add_namespace(ns_platsannons, '/af')
api.add_namespace(ns_auranest, '/')
api.add_namespace(ns_valuestore, '/vf')
