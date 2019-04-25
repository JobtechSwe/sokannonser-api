import sys
import os
import pytest
from pprint import pprint
from sokannonser import app

test_api_key = os.getenv('TEST_API_KEY_PLATSANNONSER')

@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_one_param():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/open/search', headers=headers, data={'q': 'gymnasielärare', 'limit': '1'})
        json_response = result.json
        # pprint(json_response)
        hits_total = json_response['total']
        assert int(hits_total) > 0

@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_deprecated_ads_should_not_be_in_result():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        for offset in range(0,2000, 100):
            # print(offs)
            result = testclient.get('/open/search', headers=headers, data={'offset': offset, 'limit': '100'})
            json_response = result.json
            # # pprint(json_response)
            hits = json_response['hits']
            assert len(hits) > 0
            for hit in hits:
                assert hit['removed'] is False



@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_one_param_deleted_enriched():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/open/search', headers=headers, data={'q': 'gymnasielärare', 'limit': '10'})
        json_response = result.json
        # pprint(json_response)
        hits_total = json_response['total']
        assert int(hits_total) > 0
        hits = json_response['hits']
        assert len(hits) > 0
        # pprint(hits[0])

        assert 'extracted' in hits[0]['keywords']
        assert 'enriched' not in hits[0]['keywords']


@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_one_param_found_in_enriched_pos():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/open/search', headers=headers, data={'q': 'diskare', 'limit': '100'})
        # result = testclient.get('/open/search', headers=headers, data={ 'municipality': '1290',
        #                                                                 'q': 'springare',
        #                                                                 'occupation': 'rGGf_KLs_To7',
        #                                                                'limit': '100'})
        json_response = result.json
        pprint(json_response)
        # hits_total = json_response['total']
        # assert int(hits_total) > 0
        hits = json_response['hits']
        # assert len(hits) > 0
        pprint(hits[0])
        assert 'found_in_enriched' in hits[0]


@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_one_param_found_in_enriched_neg():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/open/search', headers=headers, data={'q': 'ninja', 'limit': '100'})
        json_response = result.json
        pprint(json_response)
        # hits_total = json_response['total']
        # assert int(hits_total) > 0
        hits = json_response['hits']
        # assert len(hits) > 0
        # pprint(hits[0])
        for hit in hits:
            assert 'found_in_enriched' in hit
            assert hit['found_in_enriched'] is False



@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_two_params():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/open/search', headers=headers, data={'q': 'gymnasielärare lokförare', 'limit': '0'})
        json_response = result.json
        # pprint(json_response)
        hits_total = json_response['total']
        assert int(hits_total) > 0


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])