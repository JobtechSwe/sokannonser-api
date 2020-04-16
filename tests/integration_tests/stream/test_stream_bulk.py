import pytest

from tests.integration_tests.test_resources.stream import get_stream_check_number_of_results

@pytest.mark.skip("to be defined how it should work")
@pytest.mark.parametrize('date, expected_number', [
    ('2000-01-01T00:00:01', 1065),  # all ads
    ('2020-01-01T00:00:01', 1032),
    ('2020-03-31T07:29:41', 74),
    ('2020-04-25T07:29:41', 0)])
def test_bulk(session, url, date, expected_number):
    """
    Test snapshot with filtering on date
    """
    params = {'date': date, 'snapshot': True}
    get_stream_check_number_of_results(session, url, expected_number, params)
