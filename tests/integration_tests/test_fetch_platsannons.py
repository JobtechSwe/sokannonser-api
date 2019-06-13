import sys
import os
import pytest
from pprint import pprint
from sokannonser import app

test_api_key = os.getenv('TEST_API_KEY')


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_fetch_ad_by_id():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        # First do a search and use that ad:s ID to test fetch
        found_ad = testclient.get('/search', headers=headers, data={'limit': '1'})
        ad_id = found_ad.json.get("hits")[0].get("id")
        result = testclient.get('/ad/' + ad_id, headers=headers, data={})
        ad_result = result.json
        # pprint(ad_result)

        assert 'id' in ad_result
        assert ad_result['id'] == ad_id

        # assert 'keywords' in ad_result
        # assert 'enriched' not in ad_result['keywords']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_fetch_not_found_ad_by_id():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        ad_id = '823069282306928230692823069282306928230692'

        result = testclient.get('/ad/' + ad_id, headers=headers, data={})
        assert result.status_code == 404
        # ad_result = result.json


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
