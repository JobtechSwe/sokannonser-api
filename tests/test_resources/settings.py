import datetime
import os

SYNONYM_INDEX = 'jae-synonym-dictionary'

# environment variables must be set
TEST_USE_STATIC_DATA = os.getenv('TEST_USE_STATIC_DATA', True)
test_api_key_search = os.getenv('TEST_API_KEY_SEARCH')
test_api_key_stream = os.getenv('TEST_API_KEY_STREAM')

NUMBER_OF_ADS = 1495
DAWN_OF_TIME = '1971-01-01T00:00:01'
current_time_stamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

headers_search = {'api-key': test_api_key_search, 'accept': 'application/json'}
headers_stream = {'api-key': test_api_key_stream, 'accept': 'application/json'}

test_url = os.getenv('TEST_URL_SEARCH', 'http://localhost')
port = os.getenv('TEST_PORT_SEARCH', 5000)

SEARCH_URL = f"{test_url}:{port}"
