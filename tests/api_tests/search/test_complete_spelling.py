import pytest

from tests.test_resources.helper import get_complete


@pytest.mark.parametrize("query, expected", [
    ("göteborg sjuksköterska", ['göteborg sjuksköterska']),
    ("götteborg sjuksköterska", ['göteborg sjuksköterska']),
    ("götteborg sjukssköterska", ['göteborg sjuksköterska', 'göteborg sjuksköterskan']),
    ("göteborg sjukssköterska", ['göteborg sjuksköterska', 'göteborg sjuksköterskan']),
    ("göteborg sjukssköterska läckare", ['göteborg sjuksköterska läkare', 'göteborg sjuksköterska lärare']),
    ("göteborg sjukssköterska läkkare", ['göteborg sjuksköterska läkare', 'göteborg sjuksköterska lärare']),
    ("göteborg sjukssköterska lääkare", ['göteborg sjuksköterska läkare', 'göteborg sjuksköterska lärare']),
    ("göteborg sjukssköterska läkare", ['göteborg sjuksköterska läkare', 'göteborg sjuksköterska lärare']),
    ("läckare", ['läkare']),
    ("götteborg", ['göteborg']),
    ("stokholm", ['stockholm', 'stockholm city']),
    ("stokholm ", ['stockholm', 'stockholm city']),  # trailing space
    ("stockhlm", ['stockholm', 'stockholm city']),
    ("stockhlm ", ['stockholm city']),  # trailing space
    ("stokholm lärarre", ['stockholms lärare', 'stockholm lärare', 'stockholm läkare']),
    ("göteborg sjukssköterska läckare", ['göteborg sjuksköterska lärare', 'göteborg sjuksköterska läkare']),
    ("göteborg läckare sjukssköterska ", ['göteborg lärare sjuksköterska', 'göteborg läkare sjuksköterska']),
    ("göteborg läckare sjukssköterska", ['göteborg lärare sjuksköterska', 'göteborg läkare sjuksköterska']),
    ("läckare götteborg", ['läkare göteborg']),
    ("läckare göteborg", ['läkare göteborg']),
    ("stockholm läckare göteborg", ['stockholm lärare göteborg', 'stockholm läkare göteborg']),
    ("stockhlm läckare göteborg", ['stockholm lärare göteborg', 'stockholm läkare göteborg']),
    ("stockhlm läckare göteborg ", ['stockholm lärare göteborg', 'stockholm läkare göteborg']),  # trailing space
])
def test_complete_spelling_correction_multiple_words(session, search_url, query, expected):
    """
    Test typeahead with multiple (misspelled) words
    """
    typeahead = get_complete(session, search_url, {'q': query})['typeahead']
    values = []
    for item in typeahead:
        values.append(item['value'])
    # check that expected typeahead is in one of the actual suggestions
    for e in expected:
        assert any(v == e for v in values), f"Error: expected: '{e}' not found in '{values}'. Query: {query}"
