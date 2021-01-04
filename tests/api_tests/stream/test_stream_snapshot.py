import pytest

from tests.test_resources.helper import get_snapshot_check_number_of_results
from tests.test_resources.settings import NUMBER_OF_ADS


@pytest.mark.smoke
def test_snapshot(session_stream):
    """
    Test snapshot, should return everything
    """
    get_snapshot_check_number_of_results(session_stream, expected_number=NUMBER_OF_ADS)
