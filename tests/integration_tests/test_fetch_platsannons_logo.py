import sys
import os
import pytest
from pprint import pprint
from sokannonser import app
from sokannonser.repository import platsannonser

test_api_key = os.getenv('TEST_API_KEY')


@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_fetch_org_logo_url_by_ad_id():
    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        # First do a search and use that ad:s ID to test fetch
        found_ads = testclient.get('/search', headers=headers, data={'limit': '100'})
        hits = found_ads.json.get("hits")
        # print(hits)
        assert len(hits) > 0

        found_logo_url = False
        for hit in hits:
            ad_id = hit.get("id")
            # print(ad_id)
            logo_url = platsannonser.get_correct_logo_url(ad_id)
            if logo_url:
                found_logo_url = True
                print(logo_url)
                break

        assert found_logo_url


@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_fetch_wp_logo_url_by_ad_id():
    app.testing = True
    with app.test_client():
        ad_with_workplace_id = 23478773
        ad_id = str(ad_with_workplace_id)

        found_logo_url = platsannonser.get_correct_logo_url(ad_id)
        print(found_logo_url)
        assert found_logo_url


@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_fetch_wp_logo_url_only_org_logo_by_ad_id():
    app.testing = True
    with app.test_client():
        ad_with_workplace_id = 8417304
        ad_id = str(ad_with_workplace_id)

        found_logo_url = platsannonser.get_correct_logo_url(ad_id)
        print(found_logo_url)
        assert found_logo_url


@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_fetch_missing_logo_url_by_id():
    logo_url = platsannonser.get_correct_logo_url('10526669')
    assert logo_url is None


@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_fetch_ad_logo_by_id():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:

        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        # First do a search and use that ad:s ID to test fetch
        found_ad = testclient.get('/search', headers=headers, data={'limit': '100'})
        hits = found_ad.json.get("hits")
        # print(hits)
        assert len(hits) > 0

        found_logo_url_id = 0
        for hit in hits:
            ad_id = hit.get("id")

            logo_url = platsannonser.get_correct_logo_url(ad_id)
            if logo_url:
                found_logo_url_id = ad_id
                # print(logo_url)
                # print(found_logo_url_id)
                break
            # else:
            #     print('Not found', ad_id)

        test_url = '/ad/' + str(found_logo_url_id) + '/logo'
        print(test_url)
        result = testclient.get(test_url, headers=headers, data={})
        # pprint(result.stream)

        assert result is not None
        assert result.stream is not None


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
