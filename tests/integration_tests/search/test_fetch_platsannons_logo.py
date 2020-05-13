import sys
import os
import pytest
import requests
from sokannonser.repository import platsannonser
from tests.integration_tests.test_resources.helper import get_with_path_return_json


def get_correct_logo_url_for_any_ad(list_of_ads):
    assert len(list_of_ads) > 0
    for hit in list_of_ads:
        ad_id = hit.get("id")
        try:
            logo_url = platsannonser.get_correct_logo_url(ad_id)
        except requests.exceptions.HTTPError:
            pass
        else:
            return logo_url
    return False  # if no logo_url is found in list_of_ads


@pytest.mark.live_data
@pytest.mark.integration
def test_fetch_org_logo_url_by_ad_id(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_with_path_return_json(session, search_url, '/search', params={'limit': '100'})
    hits = json_response['hits']
    assert len(hits) > 0
    assert get_correct_logo_url_for_any_ad(hits)


@pytest.mark.integration
def test_fetch_ad_logo_by_id(session, search_url):
    """
    Search for 100 hits
    Find the first logo url in those hits
    GET that logo url
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_with_path_return_json(session, search_url, '/search', params={'limit': '100'})
    hits = json_response['hits']
    assert len(hits) > 0
    found_logo_url = get_correct_logo_url_for_any_ad(hits)
    assert found_logo_url

    result = requests.get(found_logo_url)
    result.raise_for_status()
    assert result is not None
    assert len(result.content) > 1  # image


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
