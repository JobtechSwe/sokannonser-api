import pytest

from tests.test_resources.helper import get_complete


@pytest.mark.parametrize("query, expected_typeahead", [
    ("göteborg sjuksköterska", 'göteborg sjuksköterska'),
    ("götteborg sjuksköterska", 'göteborg sjuksköterska'),
    ("götteborg sjukssköterska", 'göteborg sjuksköterska'),
    ("göteborg sjukssköterska", 'göteborg sjuksköterska'),
    ("göteborg sjukssköterska läckare", 'göteborg sjuksköterska läkare'),
    ("göteborg läckare sjukssköterska ", 'göteborg läkare sjuksköterska'),
    ("göteborg sjukssköterska läkkare", 'göteborg sjuksköterska läkare'),
    ("göteborg sjukssköterska lääkare", 'göteborg sjuksköterska läkare'),
    ("göteborg sjukssköterska läkare", 'göteborg sjuksköterska läkare'),
    ("läckare", 'läkare'),
    ("götteborg", 'göteborg'),
    ("stokholm", 'stockholm'),
    ("stokholm ", 'stockholm'),
    ("stokholm lärarre", 'stockholm lärare'),  #  stockholms
    ("göteborg sjukssköterska läckare", 'göteborg sjuksköterska läkare'),  # lärare
    ("göteborg läckare sjukssköterska ", 'göteborg läkare sjuksköterska'),  # lärare
    ("götteborg läckare sjukssköterska ", 'göteborg läkare sjuksköterska'),  # götteborg
    ("läckare götteborg", 'läkare göteborg'),
    ("läckare göteborg", 'läkare göteborg'),
    ("stockholm läckare göteborg", 'lärare göteborg'),
])
def test_complete_speling_correction_multiple_words(session, search_url, query, expected_typeahead):
    """
    Test typeahead with two (misspelled) words
    """

    response_json = get_complete(session, search_url, {'q': query})
    first_typeahead = response_json['typeahead'][0]['value']
    assert first_typeahead == expected_typeahead, f"expected: '{expected_typeahead}' but got '{first_typeahead}'"
