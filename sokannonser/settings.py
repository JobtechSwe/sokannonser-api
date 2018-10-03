import os

# Elasticsearch settings
ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = os.getenv("ES_PORT", 9200)
ES_USER = os.getenv("ES_USER")
ES_PWD = os.getenv("ES_PWD")
ES_INDEX = os.getenv("ES_INDEX", "platsannons")
ES_AURANEST = os.getenv("ES_AURANEST", "auranest")
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
TYPEAHEAD_QUERY = 'complete'
SORT = 'sortera'
PUBLISHED_BEFORE = 'publicerad-innan'
PUBLISHED_AFTER = 'publicerad-efter'
PLACE_RADIUS = 'plats.radie'
DATASET = 'dataset'

MAX_OFFSET = 2000
MAX_LIMIT = 1000

DATASET_AF = 'arbetsförmedlingen'
DATASET_AURA = 'auranest'
AVAILABLE_DATASETS = [DATASET_AF, DATASET_AURA]


# For taxonomy
SHOW_COUNT = 'visa-antal'


RESULT_MODEL = 'resultatmodell'

result_models = [
    'pbapi', 'simple'
]
sort_options = {
    'relevance': "_score",
    'pubdate-desc': {"publiceringsdatum": "desc"},
    'pubdate-asc':  {"publiceringsdatum": "asc"},
    'applydate-desc':  {"sista_ansokningsdatum": "desc"},
    'applydate-asc':  {"sista_ansokningsdatum": "asc"},
}
auranest_sort_options = {
    'relevance': "_score",
    'pubdate-desc': {"source.firstSeenAt": "desc"},
    'pubdate-asc':  {"source.firstSeenAt": "asc"},
    'applydate-desc':  {"application.deadline": "desc"},
    'applydate-asc':  {"application.deadline": "asc"},
}
