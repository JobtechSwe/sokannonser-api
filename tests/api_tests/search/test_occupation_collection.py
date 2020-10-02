import pytest
import requests
from tests.test_resources.helper import get_search, get_concept_ids_from_random_collection_with_check, \
    get_concept_ids_from_collection, list_of_concept_ids_from_collection_concept
from sokannonser.repository.taxonomy import fetch_occupation_collections


@pytest.mark.smoke
@pytest.mark.parametrize("collection", fetch_occupation_collections())
def test_name_and_collection_param(session, search_url, collection):
    """
    Fetch collections from Taxonomy and test them one by one
    Do a search with 'occupation-name' (using concept ids from collection) and save number of ads in result
    Do a search with 'occupation-collection' and save number of ads in result
    Verify that the number of ads are identical regardless of which param is used
    """

    # Search with 'occupation-name'
    list_of_concept_ids = list_of_concept_ids_from_collection_concept(collection)
    params = {'occupation-name': list_of_concept_ids}
    result_json_name = get_search(session, search_url, params)
    number_of_ads_name = result_json_name['total']['value']

    # search with 'occupation-collection'
    params = {'occupation-collection': collection['id']}
    result_json_collection = get_search(session, search_url, params)
    number_of_ads_collection = result_json_collection['total']['value']

    assert number_of_ads_collection == number_of_ads_name, collection['preferred_label']


@pytest.mark.slow
@pytest.mark.parametrize("collection", fetch_occupation_collections())
def test_name_and_collection_param_compare_ids(session, search_url, collection):
    """
    Fetch collections from Taxonomy and test them one by one
    Do a search with 'occupation-name' (using concept ids from collection) and save ids of ads
    Do a search with 'occupation-collection' and save ids of ads
    Verify that the ids of ads are identical regardless of which param is used
    """
    limit = 100
    list_of_ad_ids_name = []
    list_of_ad_ids_coll = []
    # Search with 'occupation-name'
    list_of_concept_ids = list_of_concept_ids_from_collection_concept(collection)
    params = {'occupation-name': list_of_concept_ids}
    result_json_name = get_search(session, search_url, params)
    number_of_ads_name = result_json_name['total']['value']

    for offset in range(0, number_of_ads_name, limit):
        params = {'occupation-name': list_of_concept_ids, 'offset': offset, 'limit': limit}
        json_response = get_search(session, search_url, params)
        for hit in json_response['hits']:
            list_of_ad_ids_name.append(hit['id'])

    # search with 'occupation-collection'
    params = {'occupation-collection': collection['id']}
    result_json_collection = get_search(session, search_url, params)
    number_of_ads_collection = result_json_collection['total']['value']
    for offset in range(0, number_of_ads_collection, limit):
        params = {'occupation-collection': collection['id'], 'offset': offset, 'limit': limit}
        json_response_coll = get_search(session, search_url, params)
        for hit in json_response_coll['hits']:
            list_of_ad_ids_coll.append(hit['id'])

    # results should be identical
    assert list_of_ad_ids_name == list_of_ad_ids_coll, collection['preferred_label']


@pytest.mark.slow
def test_name_and_collection_param_multiple_collections(session, search_url):
    """
    Fetch collections from Taxonomy and select 1 or more randomly

    Do a search with 'occupation-name' (using concept ids from collection) for the concept ids in
    each collection and save ad ids
    Do a search with 'occupation-collection' using a list of collection ids and save ad ids
    Verify that the ids of ads are identical regardless of which param is used
    """
    limit = 100
    list_of_ad_ids_coll = []
    list_of_ad_ids_name = []
    list_of_concept_ids, list_of_collection_ids = get_concept_ids_from_random_collection_with_check()

    # search with 'occupation-name' to find out how many ads there are
    params = {'occupation-name': list_of_concept_ids}
    result_json_collection = get_search(session, search_url, params)
    number_of_ads_name = result_json_collection['total']['value']
    # get all ads in chunks of 100 and save the ids
    for offset in range(0, number_of_ads_name, limit):
        params = {'occupation-name': list_of_concept_ids, 'offset': offset, 'limit': limit}
        json_response = get_search(session, search_url, params)
        for hit in json_response['hits']:
            list_of_ad_ids_name.append(hit['id'])

    # search with a list of 'occupation-collection' to find out how many ads there are
    params = {'occupation-collection': list_of_collection_ids}
    result_json_collection = get_search(session, search_url, params)
    number_of_ads_collection = result_json_collection['total']['value']
    # get all ads in chunks of 100 and save the ids
    for offset in range(0, number_of_ads_collection, limit):
        params = {'occupation-collection': list_of_collection_ids, 'offset': offset, 'limit': limit}
        json_response_coll = get_search(session, search_url, params)
        for hit in json_response_coll['hits']:
            list_of_ad_ids_coll.append(hit['id'])
    # results should identical regardless of which param is used
    assert list_of_ad_ids_name.sort() == list_of_ad_ids_coll.sort()
    assert list_of_ad_ids_name == list_of_ad_ids_coll


def test_empty_collection(session, search_url):
    params = {'occupation-collection': []}
    result_json = get_search(session, search_url, params)
    assert result_json['total']['value'] > 1000  # should return all ads


def test_collection_and_freetext(session, search_url):
    """
    Fetch collections from Taxonomy and test them one by one
    Do a search with 'occupation-name' (using concept ids from collection) and save number of ads in result
    Do a search with 'occupation-collection' and save number of ads in result
    Verify that the number of ads are identical regardless of which param is used
    """
    collection_id = 'UdVa_jRr_9DE'

    # search with 'occupation-collection'
    params = {'occupation-collection': collection_id}
    result_json_collection = get_search(session, search_url, params)
    number_of_ads_collection = result_json_collection['total']['value']

    params = {'q': 'systemutvecklare +tandläkare'}
    result_json_collection = get_search(session, search_url, params)
    number_of_ads_q = result_json_collection['total']['value']

    params = {'occupation-collection': collection_id, 'q': 'systemutvecklare +tandläkare'}
    result_json_combo = get_search(session, search_url, params)
    number_of_ads_combo = result_json_combo['total']['value']

    assert number_of_ads_collection > 0
    assert number_of_ads_q > 0
    assert number_of_ads_combo == 0  # current behavior
    assert number_of_ads_collection > number_of_ads_q  # assumption that a collection should return more hits than a query


def test_too_many_collections(session, search_url):
    """
    Do a search with too many 'occupation-collection'
    There should be a "500 Internal server error" caused by
    "RequestError(400, 'search_phase_execution_exception', 'failed to create query: maxClauseCount is set to 1024')"
    """
    list_of_concept_ids, list_of_collection_ids = get_concept_ids_from_collection()
    params = {'occupation-collection': list_of_collection_ids}
    try:
        r = get_search(session, search_url, params)
    except requests.exceptions.HTTPError as e:
        assert e.response.status_code == requests.codes.internal_server_error
    else:
        pytest.fail(f"should have failed with http 500 INTERNAL SERVER ERROR. Response: {r}")
