import os

# Elasticsearch settings
ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = os.getenv("ES_PORT", 9200)
ES_USER = os.getenv("ES_USER")
ES_PWD = os.getenv("ES_PWD")
ES_INDEX = os.getenv("ES_INDEX", "platsannons-read")
ES_AURANEST = os.getenv("ES_AURANEST", "auranest-read")
ES_TAX_INDEX = os.getenv("ES_TAX_INDEX", "taxonomy")

# APM and Debug settings
APM_SERVICE_NAME = os.getenv("APM_SERVICE_NAME")
APM_SERVICE_URL = os.getenv("APM_SERVICE_URL")
APM_SECRET = os.getenv("APM_SECRET")
APM_LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")

# API keys settings
ES_SYSTEM_INDEX = os.getenv("ES_SYSTEM_INDEX", "system")
ES_APIKEYS_DOC_ID = os.getenv("ES_APIKEYS_DOC_ID", "apikeys")

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = False
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False


# Base API URL
BASE_URL = os.getenv('BASE_URL', 'https://jobsearch.api.jobtechdev.se/')
BASE_PB_URL = os.getenv('BASE_PB_URL',
                        'https://www.arbetsformedlingen.se/For-arbetssokande/Platsbanken/annonser/')

COMPANY_LOGO_BASE_URL = os.getenv('COMPANY_LOGO_BASE_URL',
                                  'https://www.arbetsformedlingen.se/rest/arbetsgivare/rest/af/v3/')
# Header parameters
APIKEY = 'api-key'

# Query parameters
OFFSET = 'offset'
LIMIT = 'limit'
FREETEXT_QUERY = 'q'
TYPEAHEAD_QUERY = 'typehead'
FREETEXT_FIELDS = 'qfields'
SORT = 'sort'
PUBLISHED_BEFORE = 'published-before'
PUBLISHED_AFTER = 'published-after'
EXPERIENCE_REQUIRED = 'experience'
STATISTICS = 'stats'
STAT_LMT = 'stats.limit'
PARTTIME_MIN = 'parttime.min'
PARTTIME_MAX = 'parttime.max'
LONGITUDE = 'longitude'
LATITUDE = 'latitude'
POSITION = 'position'
POSITION_RADIUS = 'position.radius'
DEFAULT_POSITION_RADIUS = 5
EMPLOYER = 'employer'

MAX_OFFSET = 2000
MAX_LIMIT = 100

RESULT_MODEL = 'resultmodel'
DETAILS = 'resdet'
MIN_RELEVANCE = 'relevance-threshold'

# For taxonomy
SHOW_COUNT = 'show-count'

# For auranest
PLACE = 'place'

# For Batch
DATE = 'date'

# For all ads
SHOW_EXPIRED = 'show-expired'

result_models = [
    'pbapi', 'simple'
]
auranest_sort_options = {
    'relevance': "_score",
    'pubdate-desc': {"source.firstSeenAt": "desc"},
    'pubdate-asc':  {"source.firstSeenAt": "asc"},
    'applydate-desc':  {"application.deadline": "desc"},
    'applydate-asc':  {"application.deadline": "asc"},
}

auranest_stats_options = {
    'employers': 'employer.name.keyword',
    'sites': 'source.site.name.keyword',
    'locations': 'location.translations.sv-SE.keyword'
}
