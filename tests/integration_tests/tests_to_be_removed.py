import sys

import pytest

from sokannonser import app
from tests.integration_tests.test_platsannonser_queries import test_api_key
from tests.integration_tests.test_resources.check_response import check_response_return_json


@pytest.mark.skip(reason="To be removed.")
@pytest.mark.integration
def test_freetext_query_one_param_deleted_enriched():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers, data={'q': 'gymnasielärare',
                                                                  'limit': '10'})
        json_response = check_response_return_json(result)
        # pprint(json_response)
        hits_total = json_response['total']['value']
        assert int(hits_total) > 0
        hits = json_response['hits']
        assert len(hits) <= 10
        # pprint(hits[0])

        assert 'extracted' in hits[0]['keywords']
        assert 'enriched' not in hits[0]['keywords']


@pytest.mark.skip(reason="To be removed")
@pytest.mark.integration
def test_freetext_query_one_param_found_in_enriched_pos():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers, data={'q': 'diskare',
                                                                  'limit': '100'})
        json_response = check_response_return_json(result)
        # pprint(json_response)
        # hits_total = json_response['total']
        # assert int(hits_total) > 0
        hits = json_response['hits']
        # assert len(hits) > 0
        # pprint(hits[0])
        assert 'found_in_enriched' in hits[0]


@pytest.mark.skip(reason="To be removed")
@pytest.mark.integration
def test_freetext_query_one_param_found_in_enriched_neg():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers, data={'q': 'ninja',
                                                                  'limit': '100'})
        json_response = check_response_return_json(result)
        # pprint(json_response)
        # hits_total = json_response['total']
        # assert int(hits_total) > 0
        hits = json_response['hits']
        # assert len(hits) > 0
        # pprint(hits[0])
        for hit in hits:
            assert 'found_in_enriched' in hit
            assert hit['found_in_enriched'] is False
            
