import json
import pytest

from tests.integration_tests.test_resources.helper import get_search, get_stream, get_snapshot_check_number_of_results
from sokannonser.settings import NUMBER_OF_ADS, UPDATED_BEFORE_DATE, DAWN_OF_TIME, current_time_stamp


@pytest.mark.live_data
@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.parametrize("query, minimum_number_of_hits", [
    ('bagare stockholm', 1),
    ('lärare stockholm', 1),
    ('lärare göteborg', 1),
    ('*lärare göteborg', 1),
    ('lärare', 50),
    ('sjuksköterska', 50),
    ('*sjuksköterska', 100),
    ('stockholm', 200),
    ('systemutvecklare +python ', 1),
    ('systemutvecklare -python ', 25),

])
def test_search(session, search_url, query, minimum_number_of_hits):
    """
    Test that queries return at least some hits.
    Exact number is not required because test should be able to run against
    the static test data as well as against prod (with dynamic number of ads)
    """
    response = get_search(session, search_url, {'q': query, 'limit': '0'})
    assert response['total'][
               'value'] >= minimum_number_of_hits, f"Expected at least {minimum_number_of_hits} hits but got only {response['total']['value']} for query: {query}"


@pytest.mark.live_data
def test_stream_filter_on_date_interval(session, stream_url):
    params = {'date': DAWN_OF_TIME, UPDATED_BEFORE_DATE: current_time_stamp}
    list_of_ads = get_stream(session, stream_url, params)
    assert len(list_of_ads) >= NUMBER_OF_ADS


@pytest.mark.live_data
def test_snapshot(session, stream_url):
    """
    Test snapshot, should return everything.
    Check that number of ads is at least as many as in static test data (prod should have more)
    """
    response = get_snapshot_check_number_of_results(session, stream_url, expected_number=None)
    list_of_ads = json.loads(response.content.decode('utf8'))
    assert len(list_of_ads) >= NUMBER_OF_ADS
