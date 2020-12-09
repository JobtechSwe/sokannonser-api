import pytest

from tests.test_resources.helper import get_complete


@pytest.mark.parametrize("query, expected_typeahead", [
    ("göteborg sjuksköterska", 'göteborg sjuksköterska'),
    ("götteborg sjuksköterska", 'göteborg sjuksköterska'),
    ("götteborg sjukssköterska", 'göteborg sjuksköterska'),
    ("göteborg sjukssköterska", 'göteborg sjuksköterska'),
    ("göteborg sjukssköterska läckare", 'göteborg sjuksköterska lärare'),
    ("göteborg läckare sjukssköterska ", 'göteborg lärare sjuksköterska'),
    ("göteborg sjukssköterska läkkare", 'göteborg sjuksköterska lärare'),
    ("göteborg sjukssköterska lääkare", 'göteborg sjuksköterska lärare'),
    ("göteborg sjukssköterska läkare", 'göteborg sjuksköterska lärare'),
    ("läckare", 'läkare'),  # läKare
    ("götteborg", 'göteborg'),
    ("stokholm", 'stockholm'),
    ("stokholm ", 'stockholm'),
    ("stokholm lärarre", 'stockholms lärare'),
    ("göteborg sjukssköterska läckare", 'göteborg sjuksköterska lärare'),  # lärare
    ("göteborg läckare sjukssköterska ", 'göteborg lärare sjuksköterska'),  # lärare
    ("götteborg läckare sjukssköterska ", 'götteborg lärare sjuksköterska'),  # götteborg
    ("läckare götteborg", 'lärare göteborg'),
    ("läckare göteborg", 'lärare göteborg')
])
def test_complete_speling_correction_multiple_words(session, search_url, query, expected_typeahead):
    """
    Test typeahead with two (misspelled) words
    """

    response_json = get_complete(session, search_url, {'q': query})
    first_typeahead = response_json['typeahead'][0]['value']
    assert first_typeahead == expected_typeahead, f"expected: '{expected_typeahead}' but got '{first_typeahead}'"
