import pytest
from tests.test_resources.helper import get_search, compare


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.parametrize("query, expected_number_of_hits, identifier", [
    ('"gymnasielärare"', 11, 'a'),
    ("'gymnasielärare'", 11, 'b'),
    ("\"gymnasielärare\"", 11, 'c'),
    ("\'gymnasielärare\'", 11, 'd'),
    ("""gymnasielärare""", 11, 'e'),
    ('''gymnasielärare''', 11, 'f'),
    ('gymnasielärare', 11, 'g'),
    ("gymnasielärare""", 11, 'h'),
    ("gymnasielärare\"", 11, 'i'),
    ("gymnasielärare\'", 11, 'j'),
    (r"""gymnasielärare""", 11, 'k'),
    (r'''gymnasielärare''', 11, 'l'),
    ("gymnasielärare lärare", 45, 'm'),
    ("""'gymnasielärare'""", 11, 'n'),
    ('''"gymnasielärare" "lärare"''', 45, 'o'),
    ('''"gymnasielärare lärare"''', 45, 'p'),
    ("\"gymnasielärare\"", 11, 'q'),
    ("\"gymnasielärare", 11, 'r'),
    ('''"gymnasielärare"''', 11, 't'),
    ("gymnasielärare", 11, 'u'),
    ('gymnasielärare', 11, 'v'),
])
def test_query_with_different_quotes(session, query, expected_number_of_hits, identifier):
    json_response = get_search(session, params={'q': query, 'limit': '0'})
    compare(json_response['total']['value'], expected_number_of_hits, msg=f'Query: {query}')
