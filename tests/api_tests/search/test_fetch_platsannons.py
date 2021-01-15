import sys
import os
import requests
import pytest

from tests.test_resources.helper import get_with_path_return_json
from tests.test_resources.settings import SEARCH_URL


@pytest.mark.smoke
@pytest.mark.integration
def test_fetch_ad_by_id( session):
    """
    Get an ad by a request to /search without a query,and limiting the result to one ad
    use the id of the ad when doing a request to the /ad path
    verify that the id of the ad is the same as used when doing the request
    """

    json_response = get_with_path_return_json( session, '/search', params={'limit': '1'})
    ad_id = json_response['hits'][0]['id']
    ad_response = get_with_path_return_json( session, path=f"/ad/{ad_id}", params={})
    assert ad_response['id'] == ad_id
    assert len(ad_response) == 33


@pytest.mark.integration
def test_fetch_not_found_ad_by_id( session):

    ad_id = '823069282306928230692823069282306928230692'
    r = session.get(f"{SEARCH_URL}/ad/{ad_id}", params={})
    assert r.status_code == requests.codes.not_found


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
