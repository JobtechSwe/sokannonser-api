import pytest

from tests.integration_tests.test_resources.helper import get_search

test_data = [
    ('murar*', 0),
    ('systemutvecklar*', 10),
    ('*utvecklare', 37),
    ('utvecklare*', 18),
    ('*utvecklare*', 0),  # double wildcard does not work
    ('Anläggningsarbetar*', 0),
    ('Arbetsmiljöingenjö*', 2),
    ('Beläggningsarbetar*', 0),
    ('Behandlingsassisten*', 3),
    ('Bilrekonditionerar*', 1),
    ('Eventkoordinato*', 0),
    ('Fastighetsförvaltar*', 2),
    ('Fastighetsskötar*', 6),
    ('Fastighet*', 48),
    ('Kundtjänstmedarbetar*', 6),
    ('*undtjänstmedarbetare', 6),
    ('Kundtjänst*', 37),
    ('sjukskö*', 118),
    ('*sköterska', 138),
    ('sköterska*', 2),
    ('skötersk*', 6),
    ('sjukvårds*tion', 0),
    ('sj', 0),  # minimum 3 characters
    ('sj*', 0),  # minimum 3 characters
    ('sju*', 229)
]


@pytest.mark.smoke
@pytest.mark.parametrize("query, expected_number_of_hits", test_data)
@pytest.mark.integration
def test_wildcard_search_exact_match(session, search_url, query, expected_number_of_hits):
    """
    Test different wildcard queries
    check that the number of results is exactly as expected
    """
    response = get_search(session, search_url, {'q': query, 'limit': '0'})
    assert response['total'][
               'value'] == expected_number_of_hits, f"Expected {expected_number_of_hits} hits but got only {response['total']['value']} for query: {query}"


@pytest.mark.live_data
@pytest.mark.parametrize("query, minimum_number_of_hits", test_data)
@pytest.mark.integration
def test_wildcard_search_minimum_match(session, search_url, query, minimum_number_of_hits):
    """
    Test different wildcard queries
    check that the number of results is equal to or higher than 'minimum_number_of_hits'
    """
    response = get_search(session, search_url, {'q': query, 'limit': '0'})
    assert response['total'][
               'value'] >= minimum_number_of_hits, f"Expected {minimum_number_of_hits} hits but got only {response['total']['value']} for query: {query}"
