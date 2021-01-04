import json
import pytest

from tests.test_resources.helper import get_stream, get_snapshot_check_number_of_results
from sokannonser.settings import UPDATED_BEFORE_DATE
from tests.test_resources.settings import NUMBER_OF_ADS, DAWN_OF_TIME, current_time_stamp


def test_stream_filter_on_date_interval(session_stream):
    params = {'date': DAWN_OF_TIME, UPDATED_BEFORE_DATE: current_time_stamp}
    list_of_ads = get_stream(session_stream, params)
    assert len(list_of_ads) >= NUMBER_OF_ADS


def test_snapshot(session_stream):
    """
    Test snapshot, should return everything.
    Check that number of ads is at least as many as in static test data (prod should have more)
    """
    response = get_snapshot_check_number_of_results(session_stream, expected_number=None)
    list_of_ads = json.loads(response.content.decode('utf8'))
    assert len(list_of_ads) >= NUMBER_OF_ADS
