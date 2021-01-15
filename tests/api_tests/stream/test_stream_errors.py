import pytest
import requests

import tests.test_resources
from sokannonser.settings import LOCATION_CONCEPT_ID, OCCUPATION_CONCEPT_ID, ABROAD
from tests.test_resources.concept_ids import concept_ids_geo as geo, occupation as work, occupation_group as group

from tests.test_resources.helper import get_stream_expect_error, get_stream_check_number_of_results, get_stream, \
    check_ads_for_country_in_address
from tests.test_resources.settings import DAWN_OF_TIME


@pytest.mark.parametrize("wrong_date", ['2020-13-25T00:00:00', '20-00-25T00:00:00', '0001-00-01', 'T11:28:00'])
def test_wrong_date_format(session_stream, wrong_date):
    get_stream_expect_error(session_stream, params={'date': wrong_date}, expected_http_code=requests.codes.bad_request)


@pytest.mark.parametrize('path', ['/stream', '/snapshot'])
def test_filter_wrong_api_key_expect_unauthorized_response(session_stream, path):
    """
    test that a 'unauthorized' response (http 401) is returned when doing a request with an incorrect api key
    """
    session_stream.headers.update({'api-key': 'wrong key'})
    params = {LOCATION_CONCEPT_ID: geo.stockholm}
    expected_http_code = requests.codes.unauthorized
    try:
        get_stream_expect_error(session_stream, params, expected_http_code)
    finally:  # restore headers in session_stream object
        session_stream.headers.update(tests.test_resources.settings.headers_stream)


@pytest.mark.parametrize('type, value', [
    (OCCUPATION_CONCEPT_ID, work.bartender),
    (LOCATION_CONCEPT_ID, geo.stockholm)])
def test_filter_without_date_expect_bad_request_response(session_stream, type, value):
    """
    test that a 'bad request' response (http 400) is returned when doing a request without date parameter
    """
    get_stream_expect_error(session_stream, params={type: value}, expected_http_code=requests.codes.bad_request)


@pytest.mark.parametrize('work, expected_number_of_hits', [
    (group.mjukvaru__och_systemutvecklare_m_fl_, 88),
    (group.mjukvaru__och_systemutvecklare_m_fl_.lower(), 0)])
def test_filter_with_lowercase_concept_id(session_stream, work, expected_number_of_hits):
    """
    compare correct concept_id with a lower case version
    """
    params = {'date': DAWN_OF_TIME, OCCUPATION_CONCEPT_ID: work}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


@pytest.mark.parametrize("abroad", [True, False])
def test_work_abroad(session, abroad):
    """
    Check that param 'arbete-utomlands' returns http 400 BAD REQUEST for stream
    """
    get_stream_expect_error(session, {ABROAD: abroad}, expected_http_code=requests.codes.bad_request)
