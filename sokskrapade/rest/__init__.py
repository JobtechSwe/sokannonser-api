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
FREETEXT_QUERY = 'q'
OFFSET = 'offset'
LIMIT = 'limit'
API_VERSION = '1.0.0'


def lowercase_maxlength(value):
    if not value:
        raise ValueError('string type must be non-null')
    if len(value) > 255:
        raise ValueError('parameter can not be longer than 255 characters')

    return str(value).lower()


QF_CHOICES = ['occupation', 'skill', 'location', 'employer']

api = Api(version=API_VERSION, title='Joblinks',
          description="The Swedish Public Employment Service together with some of Sweden's largest "
                      "job-board sites are maintaining this API as joint effort. The dataset that are "
                      "searchable in this API is named Joblinks and contains references and metadata "
                      "linked to the job-ads provided by job-boards.",
          default='joblinks',
          default_label="An API for searching scraped ads")

ns_skrapade = Namespace('Joblinks', description='Endpoint for Joblinks')
api.add_namespace(ns_skrapade, '/')

jl_query = reqparse.RequestParser()
jl_query.add_argument(GROUP, action='append')
jl_query.add_argument(MUNICIPALITY, action='append')
jl_query.add_argument(REGION, action='append')
jl_query.add_argument(COUNTRY, action='append')
jl_query.add_argument(FREETEXT_QUERY, type=lowercase_maxlength)
jl_query.add_argument(OFFSET, type=inputs.int_range(0, 2000), default=0)
jl_query.add_argument(LIMIT, type=inputs.int_range(0, 100), default=10)
