import sys
import os
import pytest

from sokannonser import app
from tests.integration_tests.test_resources.check_response import check_response_return_json

test_api_key = os.getenv('TEST_API_KEY')
headers = {'api-key': test_api_key, 'accept': 'application/json'}


@pytest.mark.skip("Test does not find expected ad")
@pytest.mark.integration
@pytest.mark.parametrize("synonym", ['montessori'])
def test_freetext_query_synonym_param(synonym):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        # todo: Should get hits enriched with 'montessoripedagogik'. ad 23891324 in testdata should match
        result = testclient.get('/search', headers=headers, data={'q': synonym, 'limit': '1'})
        json_response = check_response_return_json(result)
        hits_total = json_response['total']['value']
        assert int(hits_total) > 0, f"no synonyms for query '{synonym}'"


@pytest.mark.skip(" Missing test data?")
@pytest.mark.integration
@pytest.mark.parametrize("geo", ['+trelleborg -stockholm ystad', 'kista kallhäll'])
def test_freetext_query_location_extracted_or_enriched(geo):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    # query_location = 'kista kallhäll'
    # query_location = 'vara'
    # query_location = 'kallhäll'
    # query_location = 'rissne'
    # query_location = 'storlien'
    # query_location = 'fridhemsplan'
    # query_location = 'skåne län'
    # query_location = '+trelleborg -stockholm ystad'
    # query_location = 'skåne'

    app.testing = True
    with app.test_client() as testclient:
        result = testclient.get('/search', headers=headers, data={'q': geo, 'limit': '0'})
        json_response = check_response_return_json(result)
        hits_total = json_response['total']['value']
        print(hits_total)
        assert int(hits_total) > 0, f"no hit for '{geo}' "
