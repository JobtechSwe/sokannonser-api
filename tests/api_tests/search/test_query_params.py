import pytest

from tests.test_resources.settings import DAWN_OF_TIME, NUMBER_OF_ADS, current_time_stamp
from tests.test_resources.helper import get_search, compare
from sokannonser.settings import POSITION, POSITION_RADIUS


@pytest.mark.parametrize('params, expected_number_of_hits', [
    ({'published-before': '2020-12-23T00:00:01'}, NUMBER_OF_ADS),
    ({'published-before': current_time_stamp}, NUMBER_OF_ADS),
    ({'published-before': DAWN_OF_TIME}, 0),
    ({'published-before': '2020-11-01T00:00:01'}, 116),
    ({'published-before': '2020-11-25T07:29:41'}, 289),
    ({'published-after': '2020-11-01T00:00:01'}, 1379),
    ({'published-after': '2020-12-01T00:00:01'}, 1094),
    ({'published-after': '2020-12-10T00:00:01'}, 739),
    ({'published-after': '2020-12-22T00:00:01'}, 4),
    ({'published-after': DAWN_OF_TIME}, NUMBER_OF_ADS),
    ({'published-after': current_time_stamp}, 0),
    ({'published-after': '2020-12-15T00:00:01', 'published-before': '2020-12-20T00:00:01'}, 368),
    ({'published-after': '2020-12-01T00:00:01', 'published-before': '2020-12-10T00:00:01'}, 355),
    ({'published-after': '2020-12-11T00:00:01', 'published-before': '2020-12-15T00:00:01'}, 153),
    ({'published-after': current_time_stamp, 'published-before': DAWN_OF_TIME}, 0),
])
def test_query_params_date(session, params, expected_number_of_hits):
    """
    Test 'published-before' and 'published-after' query parameters
    With a narrower time span, lower number of hits are returned
    
    """
    result = get_search(session, params)
    compare(result['total']['value'], expected_number_of_hits)


@pytest.mark.parametrize('params, expected_number_of_hits', [({'experience': 'true'}, 1193),
                                                             ({'experience': 'false'}, 302),
                                                             ])
def test_query_params_experience(session, params, expected_number_of_hits):
    result = get_search(session, params)
    compare(result['total']['value'], expected_number_of_hits)


@pytest.mark.parametrize('params, expected_number_of_hits', [
    ({'parttime.min': '50'}, 1272),
    ({'parttime.min': '80'}, 1236),
    ({'parttime.min': '20'}, 1297),
    ({'parttime.max': '80'}, 26),
    ({'parttime.max': '50'}, 10),
    ({'parttime.max': '20'}, 4)
])
def test_query_params_part_time(session, params, expected_number_of_hits):
    """
    Test 'parttime.min' and 'parttime.max' query parameters
    """
    result = get_search(session, params)
    compare(result['total']['value'], expected_number_of_hits)


@pytest.mark.parametrize('params, expected_number_of_hits', [
    ({POSITION: '59.3,18.0'}, 27),  # stockholm
    ({POSITION: '59.3,18.0', POSITION_RADIUS: 6}, 250),
    ({POSITION: '59.3,18.0', POSITION_RADIUS: 10}, 313),
    ({POSITION: '59.3,18.0', POSITION_RADIUS: 50}, 398),
    ({POSITION: '59.3,18.0', POSITION_RADIUS: 100}, 495),
    ({POSITION: '56.9,12.5', POSITION_RADIUS: 100}, 233),
    ({POSITION: '56.9,12.5', POSITION_RADIUS: 50}, 26),
    ({POSITION: '56.9,12.5', POSITION_RADIUS: 10}, 7),
    ({POSITION: '18.0,59.3'}, 0)  # lat long reversed
])
def test_query_params_geo_position(session, params, expected_number_of_hits):
    """
    Test 'position' query parameter along with 'position-radius'
    With larger radius, more hits are returned

    """
    result = get_search(session, params)
    compare(result['total']['value'], expected_number_of_hits)


@pytest.mark.parametrize('params, expected_number_of_hits',
                         [
                             ({'employer': 'västra götalandsregionen'}, 17),
                             ({'employer': 'Jobtech'}, 0),
                             ({'employer': 'Region Stockholm'}, 128),
                             # Todo: this is way too much
                             ({'employer': 'City Gross Sverige AB'}, 1033),
                             ({'employer': 'City Dental i Stockholm AB'}, 1064),
                             ({'employer': 'Premier Service Sverige AB'}, 1035),
                             ({'employer': 'Smartbear Sweden AB'}, 1032),
                             # probably too much:
                             ({'employer': 'Malmö Universitet'}, 46),
                             ({'employer': 'Göteborgs Universitet'}, 44),
                             ({'employer': 'Blekinge Läns Landsting'}, 8),
                             ({'employer': 'Skåne Läns Landsting'}, 24),
                             ({'employer': '"Skåne Läns Landsting"'}, 24),  # quoted string for employer

                         ])
def test_query_params_employer(session, params, expected_number_of_hits):
    """
    This test return too many hits
    it will return hits where company name has one of the words in the employer name (e.g. 'Sverige')
    keeping it to document current behavior
    """
    result = get_search(session, params)
    compare(result['total']['value'], expected_number_of_hits)
