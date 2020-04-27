import sys

import pytest

from sokannonser import app
from sokannonser.settings import headers
from tests.integration_tests.test_resources.check_response import check_response_return_json


@pytest.mark.skip("lacking enrichment - does not find field 'keywords'")
@pytest.mark.integration
def test_freetext_query_one_param_deleted_enriched():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    app.testing = True
    with app.test_client() as testclient:
        result = testclient.get('/search', headers=headers, data={'q': 'gymnasielärare', 'limit': '10'})
        json_response = check_response_return_json(result)
        assert int(json_response['total']['value']) > 0
        hits = json_response['hits']
        assert len(hits) <= 10
        try:
            keywords = hits[0]['keywords']
        except KeyError:
            print("KeyError - could not find field 'keywords'")
            raise
        assert 'extracted' in keywords
        assert 'enriched' not in keywords

@pytest.mark.skip("lacking enrichment - Field 'found_in_enriched' was not found")
@pytest.mark.integration
def test_freetext_query_one_param_found_in_enriched_pos():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        result = testclient.get('/search', headers=headers, data={'q': 'diskare', 'limit': '100'})
        json_response = check_response_return_json(result)
        hits = json_response['hits']
        assert len(hits) > 0
        assert 'found_in_enriched' in hits[0]

@pytest.mark.skip("lacking enrichment - Field 'found_in_enriched' was not found")
@pytest.mark.integration
def test_freetext_query_one_param_found_in_enriched_neg():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        result = testclient.get('/search', headers=headers, data={'q': 'sjuksköterska'})
        json_response = check_response_return_json(result)
        hits = json_response['hits']
        assert len(hits) > 0
        for hit in hits:
            assert 'found_in_enriched' in hit, "field 'found_in_enriched' was not found"
            assert hit['found_in_enriched'] is False, "field 'found_in_enriched' was not False as expected"
