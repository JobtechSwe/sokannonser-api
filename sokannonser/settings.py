import os

# Elasticsearch settings
ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = os.getenv("ES_PORT", 9200)
ES_INDEX = os.getenv("ES_INDEX", "platsannons")
ES_TAX_INDEX = os.getenv("ES_TAX_INDEX", "taxonomy")

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# Header parameters
APIKEY = 'api-key'
APIKEY_BACKDOOR = 'apa'  # TODO: Remove before production
# Query parameters
OFFSET = 'offset'
LIMIT = 'limit'
FREETEXT_QUERY = 'q'
SORT = 'sortera'
PUBLISHED_BEFORE = 'publicerad-innan'
PUBLISHED_AFTER = 'publicerad-efter'
OCCUPATION = 'yrkesroll'
GROUP = 'yrkesgrupp'
FIELD = 'yrkesomrade'
SKILL = 'kompetens'
PLACE = 'plats'
MUNICIPALITY = 'kommun'
REGION = 'lan'
PLACE_RADIUS = 'plats.radie'
WORKTIME_EXTENT = 'arbetstidsomfattning'
DATASET = 'dataset'

# For taxonomy
LANGUAGE = 'sprak'
SHOW_COUNT = 'visa-antal'

taxonomy_type = {
    OCCUPATION: 'jobterm',
    GROUP: 'jobgroup',
    FIELD: 'jobfield',
    SKILL: 'skill',
    MUNICIPALITY: 'municipality',
    REGION: 'region',
    WORKTIME_EXTENT: 'worktime_extent',
    PLACE: 'place',
    LANGUAGE: 'language',
}

reverse_taxonomy_type = {item[1]: item[0] for item in taxonomy_type.items()}

RESULT_MODEL = 'resultatmodell'

result_models = [
    'pbapi', 'simple'
]
sort_options = {
    'relevance': "_score",
    'date-desc': {"publiceringsdatum": "desc"},
    'date-asc':  {"publiceringsdatum": "asc"},
}
