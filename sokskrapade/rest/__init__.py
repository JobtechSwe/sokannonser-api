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


swagger_doc_params = {
    settings.FREETEXT_QUERY: "Fields to freetext search in, in addition to default "
    "freetext search",
    OCCUPATION: "One or more occupational concept ID according to the taxonomy",
    GROUP: "One or more occupational group concept ID according to the taxonomy",
    FIELD: "One or more occupational area concept ID according to the taxonomy",
    MUNICIPALITY: "One or more municipality concept ID according to the taxonomy",
    REGION: "One or more region concept ID according to the taxonomy",
    COUNTRY: "One or more country concept ID according to the taxonomy",
}

swagger_filter_doc_params = {
    settings.LIMIT: "Number of results to fetch (0-%d)" % 2000,
}

jl_query = reqparse.RequestParser()
jl_query.add_argument(settings.LIMIT, type=inputs.int_range(0, 100), default=10)
jl_query.add_argument(OCCUPATION, action='append')
jl_query.add_argument(GROUP, action='append')
jl_query.add_argument(FIELD, action='append')
jl_query.add_argument(MUNICIPALITY, action='append')
jl_query.add_argument(REGION, action='append')
jl_query.add_argument(COUNTRY, action='append')
jl_query.add_argument(settings.FREETEXT_QUERY, type=lowercase_maxlength)
