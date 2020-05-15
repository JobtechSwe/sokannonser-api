import sys

import pytest

# from sokannonser import app
from sokannonser.repository import platsannonser


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
