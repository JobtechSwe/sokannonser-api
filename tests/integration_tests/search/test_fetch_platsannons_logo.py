import sys
import os
import pytest
import requests
from sokannonser import app
from sokannonser.repository import platsannonser
from sokannonser.settings import headers


def get_get_correct_logo_url_for_any_ad(list_of_ads):
    assert len(list_of_ads) > 0
    for hit in list_of_ads:
        ad_id = hit.get("id")
        try:
            logo_url = platsannonser.get_correct_logo_url(ad_id)
        except requests.exceptions.HTTPError:
            pass
        else:
            return True
    return False


@pytest.mark.integration
def test_fetch_org_logo_url_by_ad_id():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        # First do a search and use that ad:s ID to test fetch
        found_ads = testclient.get('/search', headers=headers, data={'limit': '100'})
        hits = found_ads.json.get("hits")
        assert len(hits) > 0

        assert get_get_correct_logo_url_for_any_ad(hits)


@pytest.mark.integration
def test_fetch_ad_logo_by_id():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        # First do a search and use that ad:s ID to test fetch
        found_ad = testclient.get('/search', headers=headers, data={'limit': '100'})
        hits = found_ad.json.get("hits")
        found_logo_url_id =  get_get_correct_logo_url_for_any_ad(hits)
        assert found_logo_url_id
        test_url = '/ad/' + str(found_logo_url_id) + '/logo'
        result = testclient.get(test_url, headers=headers, data={})
        assert result is not None
        assert result.stream is not None


@pytest.mark.skip(reason="no test data with workplace id")
@pytest.mark.integration
def test_fetch_workplace_logo_url_by_ad_id():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client():
        ad_with_workplace_id = 23478773
        ad_id = str(ad_with_workplace_id)
        found_logo_url = platsannonser.get_correct_logo_url(ad_id)
        print(found_logo_url)
        assert found_logo_url


@pytest.mark.skip(reason="no test data with workplace id")
@pytest.mark.integration
def test_fetch_wp_logo_url_only_org_logo_by_ad_id():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client():
        ad_with_workplace_id = 8417304
        ad_id = str(ad_with_workplace_id)
        found_logo_url = platsannonser.get_correct_logo_url(ad_id)
        print(found_logo_url)
        assert found_logo_url


@pytest.mark.skip(reason="no test data with workplace id")
@pytest.mark.integration
def test_fetch_missing_logo_url_by_id():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    logo_url = platsannonser.get_correct_logo_url('10526669')
    assert logo_url is None


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
