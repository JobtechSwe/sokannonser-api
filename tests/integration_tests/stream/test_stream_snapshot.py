import pytest

from tests.integration_tests.test_resources.helper import get_snapshot_check_number_of_results
from sokannonser.settings import NUMBER_OF_ADS

@pytest.mark.smoke
def test_snapshot(session, stream_url):
    """
    Test snapshot, should return everything
    """
    get_snapshot_check_number_of_results(session, stream_url, expected_number=NUMBER_OF_ADS)
