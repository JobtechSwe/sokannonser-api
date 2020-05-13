import json
import pytest

from tests.integration_tests.test_resources.helper import get_stream, get_snapshot_check_number_of_results
from sokannonser.settings import NUMBER_OF_ADS, UPDATED_BEFORE_DATE, DAWN_OF_TIME, current_time_stamp


@pytest.mark.skip("stream filtering is not in production yet")
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
