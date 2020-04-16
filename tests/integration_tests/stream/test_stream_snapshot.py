import pytest

from tests.integration_tests.test_resources.stream import get_snapshot_check_number_of_results

@pytest.mark.smoke
def test_snapshot(session, url):
    """
    Test snapshot with filtering on date
    """
    get_snapshot_check_number_of_results(session, url, expected_number=1065)
