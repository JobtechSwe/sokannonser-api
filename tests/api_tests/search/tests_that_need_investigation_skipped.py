import sys

import pytest

# from sokannonser import app
from tests.test_resources.helper import get_search


# The tests in this file were skipped with the messages "to be removed".
# Needs more investigation. Do we have enough coverage of enrichement?

@pytest.mark.skip("lacking enrichment - does not find field 'keywords'")
@pytest.mark.integration
def test_freetext_query_one_param_deleted_enriched(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_search(session, search_url, {'q': 'gymnasielärare', 'limit': '100'})
    hits = json_response['hits']
    assert len(hits) > 0
    for hit in hits:
        try:
            keywords = hit['keywords']
        except KeyError:
            print("KeyError - could not find field 'keywords'")
            raise
        else:
            assert 'extracted' in keywords
            assert 'enriched' not in keywords


@pytest.mark.skip("lacking enrichment - Field 'found_in_enriched' was not found")
@pytest.mark.integration
def test_freetext_query_one_param_found_in_enriched_pos(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_search(session, search_url,
                               {'q': 'diskare', 'limit': '100'})
    hits = json_response['hits']
    assert len(hits) > 0, "no hits found"
    for hit in hits:
        assert 'found_in_enriched' in hit


@pytest.mark.skip("lacking enrichment - Field 'found_in_enriched' was not found")
@pytest.mark.integration
def test_freetext_query_one_param_found_in_enriched_neg(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_search(session, search_url, {'q': 'sjuksköterska', 'limit': '100'})
    hits = json_response['hits']
    assert len(hits) > 0
    for hit in hits:
        assert 'found_in_enriched' in hit, "field 'found_in_enriched' was not found"
        assert hit['found_in_enriched'] is False, "field 'found_in_enriched' was not False as expected"
