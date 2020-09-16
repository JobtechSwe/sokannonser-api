import sys

import pytest
import requests

from tests.test_resources.scraped import get_scraped, get_actual_ad_ids
from tests.test_resources.settings import NUMBER_OF_SCRAPED_ADS


@pytest.mark.parametrize("expected_number_of_hits", [0, 1, 18, 19, 35, 36, 100])
def test_limit_with_query(session_scraped, scraped_url, expected_number_of_hits):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    q = 'Sjuksköterska'
    hits_in_test_data = 35
    json_response = get_scraped(session_scraped, scraped_url,
                                params={'q': q, 'limit': expected_number_of_hits})
    assert json_response['total']['value'] == hits_in_test_data
    if expected_number_of_hits > hits_in_test_data:
        expected_number_of_hits = hits_in_test_data
    assert len(json_response['hits']) == expected_number_of_hits


@pytest.mark.parametrize("limit, expected_number_of_hits", [(0, 0), (-0, 0), (1, 1), (99, 99), (100, 100)])
def test_limit_no_query(session_scraped, scraped_url, limit, expected_number_of_hits):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'limit': limit})
    actual_ids = get_actual_ad_ids(json_response)
    assert len(actual_ids) == expected_number_of_hits
    assert json_response['total']['value'] == NUMBER_OF_SCRAPED_ADS
    assert len(json_response['hits']) == expected_number_of_hits


@pytest.mark.parametrize("wrong_limit", [101, -1, -1024, 1024])
def test_limit_wrong(session_scraped, scraped_url, wrong_limit):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    try:
        response = get_scraped(session_scraped, scraped_url, params={'limit': wrong_limit})
    except requests.exceptions.HTTPError:
        pass
    else:
        pytest.fail(f"Expected http 400 BAD request but got response: {response}")


@pytest.mark.parametrize("limit, expected_number_of_hits", [(0, 0), (-0, 0), (1, 1), (99, 99), (100, 100)])
def test_limit(session_scraped, scraped_url, limit, expected_number_of_hits):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'limit': limit})
    actual_ids = get_actual_ad_ids(json_response)
    assert len(actual_ids) == expected_number_of_hits
    assert json_response['total']['value'] == NUMBER_OF_SCRAPED_ADS
    assert len(json_response['hits']) == expected_number_of_hits
