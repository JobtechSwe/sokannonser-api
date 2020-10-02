import json
import logging
import random
import pytest

import tests.test_resources.settings
from sokannonser.repository.taxonomy import fetch_occupation_collections
from tests.test_resources.settings import TEST_USE_STATIC_DATA

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


def get_stream_check_number_of_results(session, url, expected_number, params):
    response = session.get(f"{url}/stream", params=params)
    _check_ok_response_and_number_of_ads(response, expected_number)


def get_with_path_return_json(session, url, path, params):
    response = session.get(f"{url}{path}", params=params)
    response.raise_for_status()
    return json.loads(response.content.decode('utf8'))


def get_stream(session, url, params):
    response = session.get(f"{url}/stream", params=params)
    response.raise_for_status()
    return json.loads(response.content.decode('utf8'))


def get_search(session, url, params):
    response = session.get(f"{url}/search", params=params)
    response.raise_for_status()
    return json.loads(response.content.decode('utf8'))


def get_search_check_number_of_results(session, url, expected_number, params):
    response = session.get(f"{url}/search", params=params)
    return _check_ok_response_and_number_of_ads(response, expected_number)


def get_raw(session, url, path, params):
    response = session.get(f"{url}{path}", params=params)
    response.raise_for_status()


def get_complete_with_headers(session, url, params, headers):
    old_headers = tests.test_resources.settings.headers_search
    session.headers.update(headers)
    response = session.get(f"{url}/complete", params=params)
    response.raise_for_status()
    session.headers.update(old_headers)
    return response


def get_search_with_headers(session, url, params, headers):
    old_headers = tests.test_resources.settings.headers_search
    session.headers.update(headers)
    response = session.get(f"{url}/search", params=params)
    session.headers.update(old_headers)
    return response


def get_stream_expect_error(session, url, path, params, expected_http_code):
    r = session.get(f"{url}{path}", params=params)
    status = r.status_code
    assert status == expected_http_code, f"Expected http return code to be {expected_http_code} , but got {status}"


def get_snapshot_check_number_of_results(session, url, expected_number):
    response = session.get(f"{url}/snapshot")
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


def _fetch_and_validate_result(session, search_url, query, resultfield, expected, non_negative=True):
    json_response = get_search(session, search_url, query)
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


def get_concept_ids_from_random_collection_with_check():
    """
    Returns a random combination of collections and associated concept ids
    where the sum of concept ids for the collections is lower than 500
    because it's not possible to search with too many clauses
    """
    all_collections = fetch_occupation_collections()

    for i in range(1000):
        list_of_concept_ids = []
        list_of_collection_ids = []
        random_collections = random.sample(all_collections, random.randint(1, len(all_collections)))
        for c in random_collections:
            list_of_collection_ids.append(c['id'])
            for tmp in list_of_concept_ids_from_collection_concept(c):
                list_of_concept_ids.append(tmp)

        if len(list_of_concept_ids) < 500:
            return list_of_concept_ids, list_of_collection_ids
    pytest.fail("no collection combination with < 500 concept ids found after 1000 retries")


def get_concept_ids_from_collection():
    """
    Returns a random combination of collections and associated concept ids
    where the sum of concept ids for the collections is lower than 500
    because it's not possible to search with too many clauses
    """
    all_collections = fetch_occupation_collections()

    list_of_concept_ids = []
    list_of_collection_ids = []
    for c in all_collections:
        list_of_collection_ids.append(c['id'])
        for tmp in list_of_concept_ids_from_collection_concept(c):
            list_of_concept_ids.append(tmp)

    return list_of_concept_ids, list_of_collection_ids


def list_of_concept_ids_from_collection_concept(concept):
    list_of_ids = []
    for item in concept['related']:
        list_of_ids.append(item['id'])
    return list_of_ids
