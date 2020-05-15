import pytest

from tests.test_resources.helper import get_search


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.parametrize("query, minimum_number_of_hits", [
    ('bagare stockholm', 1),
    ('lärare stockholm', 1),
    ('lärare göteborg', 1),
    ('*lärare göteborg', 1),
    ('lärare', 50),
    ('sjuksköterska', 50),
    ('*sjuksköterska', 100),
    ('stockholm', 200),
    ('systemutvecklare +python ', 1),
    ('systemutvecklare -python ', 25),
])
def test_search(session, search_url, query, minimum_number_of_hits):
    """
    Test that queries return at least some hits.
    Exact number is not required because test should be able to run against
    the static test data as well as against prod (with dynamic number of ads)
    """
    response = get_search(session, search_url, {'q': query, 'limit': '0'})
    assert response['total'][
               'value'] >= minimum_number_of_hits, f"Expected at least {minimum_number_of_hits} hits but got only {response['total']['value']} for query: {query}"
