from flask_restplus import Api, Namespace

api = Api(version='1.0', title='Sök Annonser',
          description='Hitta platsannonser.',
          default='sokannonser',
          default_label="Verktyg för att hitta platsannoner")

ns_platsannons = Namespace('AF-Annonser',
                           description='Sök bland AF:s annonser')
ns_auranest = Namespace('Alla Annonser',
                        description='Sök bland alla annonser på marknaden')
ns_valuestore = Namespace('Värdeförråd',
                          description='Sök i taxonomi och ontologi')

api.add_namespace(ns_platsannons, '/af')
api.add_namespace(ns_auranest, '/')
api.add_namespace(ns_valuestore, '/vf')
