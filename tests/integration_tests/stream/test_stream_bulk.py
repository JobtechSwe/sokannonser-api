import pytest

from tests.integration_tests.test_resources.stream import get_stream_check_number_of_results






@pytest.mark.parametrize('date, expected_number', [
    ('2000-01-01T00:00:01', 1065),
    ('2020-01-01T00:00:01', 1032),
    ('2020-02-01T00:00:01', 971),
    ('2020-02-25T07:29:41', 872),
    ('2020-03-14T07:29:41', 556),
    ('2020-03-25T07:29:41', 273),
    ('2020-03-27T07:29:41', 186),
    ('2020-03-31T07:29:41', 74),
    ('2020-04-25T07:29:41', 0)])
def test_bulk(session, url, date, expected_number):
    """
    Test basic stream with filtering on date
    """
    get_stream_check_number_of_results(session, url, expected_number, params={'date': date})
