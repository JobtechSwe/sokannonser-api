import json
import logging
import random

import requests

from sokannonser.repository.taxonomy import fetch_occupation_collections
from tests.test_resources.concept_ids import concept_ids_geo as geo
from tests.test_resources.settings import TEST_USE_STATIC_DATA, SEARCH_URL, STREAM_URL

log = logging.getLogger(__name__)


def _log_failed_comparison(message):
    log.warning(message)


def compare_typeahead(actual_typeahead, expected_typeahead):
    try:
        for index, suggestion in enumerate(actual_typeahead):
            error_msg = f"Comparison of {suggestion['value']} and {expected_typeahead[index]} failed"
            assert suggestion['value'] == expected_typeahead[index]
    except AssertionError as ex:
        _handle_failed_comparison(ex, error_msg)


def compare_suggestions(actual, expected, query):
    if len(actual) >= 50:
        # if 50 or more we can't be sure of order and content of suggestions
        return
    try:
        msg = f"\nQuery: {query}"
        compare(len(actual), len(expected), msg)
        for s in expected:
            msg = f"Did not find {s} in {actual} "
            assert s in actual
    except AssertionError as ex:
        _handle_failed_comparison(ex, msg)


def compare_synonyms(synonyms, complete_values, expect_success):
    msg = ''
    try:
        for s in synonyms:
            if expect_success:
                msg = f"Synonym '{s}' not found in response"
                assert s in complete_values
            else:
                msg = f"Synonym '{s}' was found in response"
                assert s not in complete_values
    except AssertionError as ex:
        _handle_failed_comparison(ex, msg)


def compare(actual, expected, msg=""):
    error_msg = f"expected {expected} but got {actual}. " + msg
    try:
        assert actual == expected
    except AssertionError as ex:
        print(f"Expected: {expected} but got {actual}")
        _handle_failed_comparison(ex, error_msg)


def _handle_failed_comparison(ex, msg="Error in comparison"):
    if TEST_USE_STATIC_DATA:
        log.error(msg)
        raise ex  # static test data == strict comparision
    else:  # staging and prod will have live data which will return a different number of results
        log.warning(f"Live data, ignore error. {msg}")


def check_len_more_than(check_this, compare_to):
    check_value_more_than(len(check_this), compare_to)


def check_value_more_than(check_this, compare_to):
    error_msg = f"{check_this} was not larger than {compare_to}."
    try:
        assert check_this > compare_to
    except AssertionError as ex:
        _handle_failed_comparison(ex, error_msg)


def get_stream_check_number_of_results(session, expected_number, params):
    response = session.get(f"{STREAM_URL}/stream", params=params)
    _check_ok_response_and_number_of_ads(response, expected_number)


def get_with_path_return_json(session, path, params):
    response = session.get(f"{SEARCH_URL}/{path}", params=params)
    response.raise_for_status()
    return json.loads(response.content.decode('utf8'))


def get_stream(session, params):
    response = session.get(f"{STREAM_URL}/stream", params=params)
    response.raise_for_status()
    return json.loads(response.content.decode('utf8'))


def get_search(session, params,):
    response = session.get(f"{SEARCH_URL}/search", params=params)
    response.raise_for_status()
    return json.loads(response.content.decode('utf8'))

def get_search_expect_error(session, params, expected_http_code):
    response = session.get(f"{SEARCH_URL}/search", params=params)
    assert response.status_code == expected_http_code, f"Expected http return code to be {expected_http_code} , but got {response.status_code}"
    return response

def get_search_check_number_of_results(session, expected_number, params):
    response = session.get(f"{SEARCH_URL}/search", params=params)
    return _check_ok_response_and_number_of_ads(response, expected_number)


def get_complete(session,  params):
    response = session.get(f"{SEARCH_URL}/complete", params=params)
    response.raise_for_status()
    return json.loads(response.content.decode('utf8'))


def get_complete_with_headers(session, params, headers):
    response = session.get(f"{SEARCH_URL}/complete", params=params, headers=headers)
    response.raise_for_status()
    return json.loads(response.content.decode('utf8'))

def get_complete_expect_error(session, params, expected_http_code):
    response = session.get(f"{SEARCH_URL}/complete", params=params)
    assert response.status_code == expected_http_code, f"Expected http return code to be {expected_http_code} , but got {response.status_code}"
    return response


def get_stream_expect_error(session, params, expected_http_code):
    r = session.get(f"{STREAM_URL}/stream", params=params)
    status = r.status_code
    assert status == expected_http_code, f"Expected http return code to be {expected_http_code} , but got {status}"


def get_snapshot_check_number_of_results(session, expected_number):
    response = session.get(f"{STREAM_URL}/snapshot")
    return _check_ok_response_and_number_of_ads(response, expected_number)


def _check_ok_response_and_number_of_ads(response, expected_number):
    response.raise_for_status()
    assert response.content is not None
    list_of_ads = json.loads(response.content.decode('utf8'))
    if '/search' in response.url:
        list_of_ads = list_of_ads['hits']
    if expected_number is not None:
        compare(len(list_of_ads), expected_number)
    _check_list_of_ads(list_of_ads)
    return response


def _check_list_of_ads(list_of_ads):
    for ad in list_of_ads:
        assert isinstance(ad['id'], str)
        checks = []
        checks.append(ad['id'])
        if not ad['removed']:
            checks.append(ad['headline'])
            checks.append(ad['description'])
            checks.append(ad['occupation'])
            checks.append(ad['workplace_address']['country'])
            for c in checks:
                assert c is not None, ad


def check_freetext_concepts(free_text_concepts, list_of_expected):
    assert free_text_concepts['skill'] == list_of_expected[0]
    assert free_text_concepts['occupation'] == list_of_expected[1]
    assert free_text_concepts['location'] == list_of_expected[2]
    assert free_text_concepts['skill_must'] == list_of_expected[3]
    assert free_text_concepts['occupation_must'] == list_of_expected[4]
    assert free_text_concepts['location_must'] == list_of_expected[5]
    assert free_text_concepts['skill_must_not'] == list_of_expected[6]
    assert free_text_concepts['occupation_must_not'] == list_of_expected[7]
    assert free_text_concepts['location_must_not'] == list_of_expected[8]


def _fetch_and_validate_result(session, query, resultfield, expected, non_negative=True):
    json_response = get_search(session, query)
    hits = json_response['hits']
    check_len_more_than(hits, 0)
    for hit in hits:
        for i in range(len(resultfield)):
            if non_negative:
                assert _get_nested_value(resultfield[i], hit) == expected[i]
            else:
                assert not _get_nested_value(resultfield[i], hit) == expected[i]


def _get_nested_value(path, dictionary):
    keypath = path.split('.')
    value = None
    for i in range(len(keypath)):
        element = dictionary.get(keypath[i])
        if isinstance(element, dict):
            dictionary = element
        else:
            value = element
            break
    return value


def get_random_occupation_collection_id_and_concept_ids():
    # returns a randomized list of collection ids and and a list of all the related concept ids
    collections = get_occupation_collection_id_and_concept_ids()
    random_collections = random.sample(collections, random.randint(1, len(collections)))

    all_collection_ids = []
    all_concept_ids = []
    for c in random_collections:
        all_collection_ids.append(c[0])
        for c_id in c[1]:
            all_concept_ids.append(c_id)
    return all_collection_ids, all_collection_ids


def get_occupation_collection_id_and_concept_ids():
    """
    returns a list of tuples
    first element: collection id
    second element: a list of concept ids related to the collection id
    """
    list_of_collections_with_id = []
    collection = fetch_occupation_collections()
    all_keys = list(collection.keys())
    for k in all_keys:
        list_of_collections_with_id.append((k, collection[k]))

    return list_of_collections_with_id


def get_search_with_headers( params, headers):
    r = requests.get(SEARCH_URL + '/search', params, headers=headers)
    r.raise_for_status()
    return json.loads(r.content.decode('utf8'))


def check_ads_for_country_in_address(hits, abroad):
    for hit in hits:
        country = hit['workplace_address']['country']
        country_concept_id = hit['workplace_address']['country_concept_id']
        assert (country == 'Sverige') != abroad
        assert (country_concept_id == 'i46j_HmG_v64') != abroad
