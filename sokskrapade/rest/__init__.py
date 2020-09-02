from flask_restx import Api, Namespace, reqparse, inputs
from sokannonser import settings

OCCUPATION = 'occupation-name'
GROUP = 'occupation-group'
FIELD = 'occupation-field'
SKILL = 'skill'
PLACE = 'place'
MUNICIPALITY = 'municipality'
REGION = 'region'
COUNTRY = 'country'


def lowercase_maxlength(value):
    if value is None:
        raise ValueError('string type must be non-null')
    if len(value) > 255:
        raise ValueError('parameter can not be longer than 255 characters')

    return str(value).lower()


QF_CHOICES = ['occupation', 'skill', 'location', 'employer']

api = Api(version=settings.API_VERSION, title='Search Scraped Ads',
          description='An API for searching scraped ads',
          default='sokskrapade',
          default_label="An API for searching scraped ads")


ns_skrapade = Namespace('Search scraped ads', description='Endpoint for scraped ads')
api.add_namespace(ns_skrapade, '/')

jl_query = reqparse.RequestParser()
jl_query.add_argument(settings.LIMIT, type=inputs.int_range(0, 1000), default=10)
jl_query.add_argument(OCCUPATION, action='append')
jl_query.add_argument(GROUP, action='append')
jl_query.add_argument(FIELD, action='append')
jl_query.add_argument(MUNICIPALITY, action='append')
jl_query.add_argument(REGION, action='append')
jl_query.add_argument(COUNTRY, action='append')
jl_query.add_argument(settings.FREETEXT_QUERY, type=lowercase_maxlength)
