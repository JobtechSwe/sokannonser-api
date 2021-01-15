import sys
import pytest

from tests.test_resources.helper import get_search, compare


@pytest.mark.integration
@pytest.mark.parametrize("geo, expected_number_of_hits", [
    ('kista kallhäll', 5),
    ('vara', 918),
    ('kallhäll', 0),
    ('rissne', 1),
    ('skåne län', 190),
    ('skåne', 197),
    ('+trelleborg -stockholm ystad', 5),
    ('storlien', 0),
    ('fridhemsplan', 0)
])
def test_freetext_query_location_extracted_or_enriched(session, geo, expected_number_of_hits):
    """
    Describe what the test is testing
    """
    json_response = get_search(session, params={'q': geo, 'limit': '0'})
    hits_total = json_response['total']['value']
    compare(hits_total, expected_number_of_hits)


def test_freetext_query_synonym_param(session):
    json_response = get_search(session, params={'q': 'montessori', 'limit': '0'})
    assert json_response['freetext_concepts']['skill'][0] == 'montessoripedagogik'
    compare(json_response['total']['value'], 2)
