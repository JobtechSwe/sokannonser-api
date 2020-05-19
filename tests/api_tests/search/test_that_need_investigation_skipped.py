import sys

import pytest

# from sokannonser import app
from sokannonser.repository import taxonomy
from sokannonser.rest.model import fields
from tests.test_resources.helper import get_search, _fetch_and_validate_result_old, _fetch_and_validate_result, compare

# The tests in this file were skipped with the messages "to be removed".
# Needs more investigation. Do we have enough coverage of enrichement?
from tests.test_resources.settings import TEST_USE_STATIC_DATA


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


@pytest.mark.integration
@pytest.mark.skip("app.testclient.get return 0 hits. Without len check for hits, the test pretends to pass")
def test_country_old(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result_old({taxonomy.REGION: '199'},
                                   [fields.WORKPLACE_ADDRESS_REGION_CODE], ['199'])
    _fetch_and_validate_result_old({taxonomy.REGION: '-199'},
                                   [fields.WORKPLACE_ADDRESS_REGION_CODE], ['199'], False)


@pytest.mark.skip("investigate why it doesn't work")
@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.parametrize("region, non_negative", [('199', True), ('-199', False)])
def test_country(session, search_url, region, non_negative):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result(session, search_url, {taxonomy.REGION: region},
                               [fields.WORKPLACE_ADDRESS_REGION_CODE], ['199'], non_negative)


@pytest.mark.skip("investigate why it doesn't work")
@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.parametrize("query, path, expected",
                         [({taxonomy.OCCUPATION: "D7Ns_RG6_hD2",
                            taxonomy.MUNICIPALITY: "0180", "limit": 100},
                           [fields.OCCUPATION + ".concept_id",
                            fields.WORKPLACE_ADDRESS_MUNICIPALITY],
                           ["D7Ns_RG6_hD2", "0180"]),
                          ])
@pytest.mark.integration
def test_occupation_location_combo(session, search_url, query, path, expected):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    _fetch_and_validate_result(session, search_url, query, path, expected)


@pytest.mark.skip(
    reason="Temporarily disabled. Needs fix according to Trello Card #137, Multipla ord i ett yrke")  # Missing test data?
@pytest.mark.integration
def test_freetext_query_ssk(session, search_url, ):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    query = 'stockholm grundutbildad sjuksköterska'
    json_response = get_search(session, search_url, params={'q': query, 'limit': '0'})
    expected = '???'
    compare(json_response['total']['value'], expected=expected)


@pytest.mark.skip("Test does not find expected ad")
@pytest.mark.integration
@pytest.mark.parametrize("synonym", ['montessori'])
def test_freetext_query_synonym_param(session, search_url, synonym):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': synonym, 'limit': '1'})
    hits_total = json_response['total']['value']
    compare(hits_total, 1)
    # todo: Should get hits enriched with 'montessoripedagogik'. ad 23891324 in testdata should match
