import pytest

from tests.test_resources.settings import DAWN_OF_TIME, NUMBER_OF_ADS, current_time_stamp
from tests.test_resources.helper import get_search, compare
from sokannonser.settings import POSITION, POSITION_RADIUS


@pytest.mark.parametrize('params, expected_number_of_hits', [
    ({'published-before': '2020-05-01T00:00:01'}, NUMBER_OF_ADS),
    ({'published-before': current_time_stamp}, NUMBER_OF_ADS),
    ({'published-before': DAWN_OF_TIME}, 0),
    ({'published-before': '2020-01-01T00:00:01'}, 36),
    ({'published-before': '2020-03-25T07:29:41'}, 819),
    ({'published-after': '2020-01-01T00:00:01'}, 1036),
    ({'published-after': '2020-02-01T00:00:01'}, 961),
    ({'published-after': '2020-03-01T00:00:01'}, 821),
    ({'published-after': '2020-04-01T00:00:01'}, 7),
    ({'published-after': DAWN_OF_TIME}, NUMBER_OF_ADS),
    ({'published-after': current_time_stamp}, 0),
    ({'published-after': '2020-02-01T00:00:01', 'published-before': '2020-03-01T00:00:01'}, 140),
    ({'published-after': '2020-03-01T00:00:01', 'published-before': '2020-03-01T00:00:01'}, 0),
    ({'published-after': current_time_stamp, 'published-before': DAWN_OF_TIME}, 0),
])
def test_query_params_date(session, search_url, params, expected_number_of_hits):
    """
    Test 'published-before' and 'published-after' query parameters
    With a narrower time span, lower number of hits are returned
    
    """
    result = get_search(session, search_url, params)
    compare(result['total']['value'], expected_number_of_hits)


@pytest.mark.parametrize('params, expected_number_of_hits', [({'experience': 'true'}, 810),
                                                             ({'experience': 'false'}, 262),
                                                             ])
def test_query_params_experience(session, search_url, params, expected_number_of_hits):
    result = get_search(session, search_url, params)
    compare(result['total']['value'], expected_number_of_hits)


@pytest.mark.parametrize('params, expected_number_of_hits', [
    ({'parttime.min': '50'}, 872),
    ({'parttime.min': '80'}, 815),
    ({'parttime.min': '20'}, 898),
    ({'parttime.max': '80'}, 34),
    ({'parttime.max': '50'}, 10),
    ({'parttime.max': '20'}, 3)
])
def test_query_params_part_time(session, search_url, params, expected_number_of_hits):
    """
    Test 'parttime.min' and 'parttime.max' query parameters
    """
    result = get_search(session, search_url, params)
    compare(result['total']['value'], expected_number_of_hits)


@pytest.mark.parametrize('params, expected_number_of_hits', [
    ({POSITION: '59.3,18.0'}, 27),  # stockholm
    ({POSITION: '59.3,18.0', POSITION_RADIUS: 6}, 164),
    ({POSITION: '59.3,18.0', POSITION_RADIUS: 10}, 214),
    ({POSITION: '59.3,18.0', POSITION_RADIUS: 50}, 282),
    ({POSITION: '59.3,18.0', POSITION_RADIUS: 100}, 358),
    ({POSITION: '56.9,12.5', POSITION_RADIUS: 100}, 175),
    ({POSITION: '56.9,12.5', POSITION_RADIUS: 50}, 19),
    ({POSITION: '56.9,12.5', POSITION_RADIUS: 10}, 4),
    ({POSITION: '18.0,59.3'}, 0)  # lat long reversed
])
def test_query_params_geo_position(session, search_url, params, expected_number_of_hits):
    """
    Test 'position' query parameter along with 'position-radius'
    With larger radius, more hits are returned

    """
    result = get_search(session, search_url, params)
    compare(result['total']['value'], expected_number_of_hits)


@pytest.mark.parametrize('params, expected_number_of_hits',
                         [
                             ({'employer': 'västra götalandsregionen'}, 14),
                             ({'employer': 'Jobtech'}, 0),
                             ({'employer': 'Region Stockholm'}, 100),
                             # Todo: this is way too much
                             ({'employer': 'City Gross Sverige AB'}, 733),
                             ({'employer': 'City Dental i Stockholm AB'}, 751),
                             ({'employer': 'Premier Service Sverige AB'}, 732),
                             ({'employer': 'Smartbear Sweden AB'}, 734),
                             # probably too much:
                             ({'employer': 'Malmö Universitet'}, 25),
                             ({'employer': 'Göteborgs Universitet'}, 23),
                             ({'employer': 'Blekinge Läns Landsting'}, 14),
                             ({'employer': 'Skåne Läns Landsting'}, 24),
                             ({'employer': '"Skåne Läns Landsting"'}, 24),  # quoted string for employer

                         ])
def test_query_params_employer(session, search_url, params, expected_number_of_hits):
    """

    This test return too many hits
    it will return hits where company name has one of the words in the employer name (e.g. 'Sverige')
    keeping it to document current behavior

    """
    result = get_search(session, search_url, params)
    compare(result['total']['value'], expected_number_of_hits)
