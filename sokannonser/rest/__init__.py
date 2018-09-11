from flask_restplus import Api

api = Api(version='1.0', title='Sök Annonser',
          description='Hitta platsannonser.',
          default='sokannonser',
          default_label="Verktyg för att hitta platsannoner")
