import datetime
import os

SYNONYM_INDEX = 'jae-synonym-dictionary'

# environment variables must be set
TEST_USE_STATIC_DATA = os.getenv('TEST_USE_STATIC_DATA', True)
test_api_key_search = os.getenv('TEST_API_KEY_SEARCH')
test_api_key_stream = os.getenv('TEST_API_KEY_STREAM')
test_api_key_scraped = os.getenv('TEST_API_KEY_SCRAPED')

NUMBER_OF_ADS = 1072
NUMBER_OF_SCRAPED_ADS = 510
DAWN_OF_TIME = '1971-01-01T00:00:01'
current_time_stamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

headers_search = {'api-key': test_api_key_search, 'accept': 'application/json'}
headers_stream = {'api-key': test_api_key_stream, 'accept': 'application/json'}
headers_scraped = {'api-key': test_api_key_scraped, 'accept': 'application/json'}
