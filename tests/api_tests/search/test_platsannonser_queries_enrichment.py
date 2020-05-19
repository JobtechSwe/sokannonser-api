import sys
import pytest

from tests.test_resources.helper import get_search, compare


@pytest.mark.integration
@pytest.mark.parametrize("geo, expected_number_of_hits", [
    ('kista kallhäll', 7),
    ('vara', 1),
    ('kallhäll', 1),
    ('rissne', 1),
    ('skåne län', 122),
    ('skåne', 130),
    ('+trelleborg -stockholm ystad', 0),
    ('storlien', 0),
    ('fridhemsplan', 0)
])
def test_freetext_query_location_extracted_or_enriched(session, search_url, geo, expected_number_of_hits):
    """
    Describe what the test is testing
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': geo, 'limit': '0'})
    hits_total = json_response['total']['value']
    compare(hits_total, expected_number_of_hits)
