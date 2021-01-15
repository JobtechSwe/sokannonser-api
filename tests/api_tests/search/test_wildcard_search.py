import pytest

from tests.test_resources.helper import get_search, compare

test_data = [
    ('murar*', 2),
    ('systemutvecklar*', 7),
    ('*utvecklare', 64),
    ('utvecklare*', 33),
    ('*utvecklare*', 0),  # double wildcard does not work
    ('Anläggningsarbetar*', 3),
    ('Arbetsmiljöingenjö*', 2),
    ('Beläggningsarbetar*', 0),
    ('Behandlingsassisten*', 8),
    ('Bilrekonditionerar*', 0),
    ('Eventkoordinato*', 0),
    ('Fastighetsförvaltar*', 4),
    ('Fastighetsskötar*', 1),
    ('Fastighet*', 64),
    ('Kundtjänstmedarbetar*', 3),
    ('*undtjänstmedarbetare', 3),
    ('Kundtjänst*', 38),
    ('sjukskö*', 187),
    ('*sköterska', 199),
    ('sköterska*', 3),
    ('skötersk*', 6),
    ('sjukvårds*tion', 0),
    ('sj', 1),  # minimum 3 characters
    ('sj*', 0),  # minimum 3 characters
    ('sju*', 327)
]


@pytest.mark.smoke
@pytest.mark.parametrize("query, expected_number_of_hits", test_data)
@pytest.mark.integration
def test_wildcard_search_exact_match( session, query, expected_number_of_hits):
    """
    Test different wildcard queries
    check that the number of results is exactly as expected
    """
    response_json = get_search(session,  {'q': query, 'limit': '0'})
    compare(response_json['total']['value'], expected_number_of_hits, msg=f"Query: {query}")

@pytest.mark.parametrize("query, minimum_number_of_hits", test_data)
@pytest.mark.integration
def test_wildcard_search_minimum_match( session, query, minimum_number_of_hits):
    """
    Test different wildcard queries
    check that the number of results is equal to or higher than 'minimum_number_of_hits'
    """
    response_json = get_search(session,  {'q': query, 'limit': '0'})
    compare(response_json['total']['value'], minimum_number_of_hits, msg=f"Query: {query}")
