import os

# Elasticsearch settings
ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = os.getenv("ES_PORT", 9200)
ES_USER = os.getenv("ES_USER")
ES_PWD = os.getenv("ES_PWD")
ES_INDEX = os.getenv("ES_INDEX", "platsannons-read")
ES_STREAM_INDEX = os.getenv("ES_BULK_INDEX", "platsannons-stream")
ES_AURANEST = os.getenv("ES_AURANEST", "auranest-read")
ES_TAX_INDEX = os.getenv("ES_TAX_INDEX", "taxonomy")

# APM and Debug settings
APM_SERVICE_NAME = os.getenv("APM_SERVICE_NAME")
APM_SERVICE_URL = os.getenv("APM_SERVICE_URL")
APM_SECRET = os.getenv("APM_SECRET")
APM_LOG_LEVEL = os.getenv("APM_LOG_LEVEL", "WARNING")

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = False
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# Base API URL
BASE_URL = os.getenv('BASE_URL', 'https://jobsearch.api.jobtechdev.se/')
BASE_PB_URL = os.getenv('BASE_PB_URL',
                        'https://arbetsformedlingen.se/platsbanken/annonser/')

COMPANY_LOGO_BASE_URL = os.getenv('COMPANY_LOGO_BASE_URL',
                                  'https://www.arbetsformedlingen.se/rest/arbetsgivare/rest/af/v3/')
COMPANY_LOGO_FETCH_DISABLED = os.getenv('COMPANY_LOGO_FETCH_DISABLED', 'false').lower() == 'true'
# Header parameters
APIKEY = 'api-key'
# Feature toggles
X_FEATURE_FREETEXT_BOOL_METHOD = 'x-feature-freetext-bool-method'
X_FEATURE_ALLOW_EMPTY_TYPEAHEAD = 'x-feature-allow-empty-typeahead'
X_FEATURE_INCLUDE_SYNONYMS_TYPEAHEAD = 'x-feature-include-synonyms-typeahead'
X_FEATURE_SPELLCHECK_TYPEAHEAD = 'x-feature-spellcheck-typeahead'
X_FEATURE_DISABLE_SMART_FREETEXT = 'x-feature-disable-smart-freetext'
X_FEATURE_SUGGEST_EXTRA_WORD = 'x-feature-suggest-extra-word'

# Query parameters
OFFSET = 'offset'
LIMIT = 'limit'
FREETEXT_QUERY = 'q'
TYPEAHEAD_QUERY = 'typehead'
FREETEXT_LAST_WORD_SPACE = 'space'
CONTEXTUAL_TYPEAHEAD = 'contextual'
UNSPECIFIED_SWEDEN_WORKPLACE = 'unspecified-sweden-workplace'
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

DEFAULT_FREETEXT_BOOL_METHOD = 'and'

MAX_OFFSET = 2000
MAX_LIMIT = 100
MAX_TAXONOMY_LIMIT = 8000
MAX_COMPLETE_LIMIT = 50

RESULT_MODEL = 'resultmodel'
DETAILS = 'resdet'
MIN_RELEVANCE = 'relevance-threshold'

# For taxonomy
SHOW_COUNT = 'show-count'
TAX_DESCRIPTION = 'DEPRECATED, use https://taxonomy.api.jobtechdev.se/v1/taxonomy/swagger-ui/index.html instead'

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
    'pubdate-asc': {"source.firstSeenAt": "asc"},
    'applydate-desc': {"application.deadline": "desc"},
    'applydate-asc': {"application.deadline": "asc"},
}

auranest_stats_options = {
    'employers': 'employer.name.keyword',
    'sites': 'source.site.name.keyword',
    'locations': 'location.translations.sv-SE.keyword'
}

# sweden country concept id: /v1/taxonomy/main/concepts?id=i46j_HmG_v64'
SWEDEN_CONCEPT_ID = 'i46j_HmG_v64'


# for tests:
number_of_ads = 1065
test_api_key = os.getenv('TEST_API_KEY')
headers = {'api-key': test_api_key, 'accept': 'application/json'}

API_VERSION = '1.13.1'

