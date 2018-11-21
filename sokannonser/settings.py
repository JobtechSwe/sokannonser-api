import os
from valuestore import taxonomy

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

# Ad proxy URL
AD_PROXY_URL = 'http://api.arbetsformedlingen.se/af/v0/platsannonser/'
# Base API URL
BASE_URL = os.getenv('BASE_URL', 'https://base.url')

# Header parameters
APIKEY = 'api-key'
APIKEY_BACKDOOR = 'apa'  # TODO: Remove before production

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
POSITION_RADIUS = 'position.radius'

MAX_OFFSET = 2000
MAX_LIMIT = 1000

RESULT_MODEL = 'resultmodel'

# For taxonomy
SHOW_COUNT = 'show-count'

# For all ads
SHOW_EXPIRED = 'show-expired'

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
stats_options = {
    taxonomy.OCCUPATION: "yrkesroll.kod.keyword",
    taxonomy.GROUP: "yrkesgrupp.kod.keyword",
    taxonomy.FIELD: "yrkesomrade.kod.keyword",
}
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
