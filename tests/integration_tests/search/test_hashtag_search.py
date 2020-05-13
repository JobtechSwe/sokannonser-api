import pytest

from sokannonser import app
from sokannonser.settings import headers


@pytest.mark.smoke
@pytest.mark.parametrize("query, expected_number_of_hits", [
    ('#corona', 1),
    ('corona', 1),
    ('#jobbjustnu', 6),
    ('jobbjustnu', 1),
    ('#metoo', 1),
    ('metoo', 0),
    ('#wedo', 1),
    ('wedo', 0)
])
@pytest.mark.integration
def test_hashtag_search(query, expected_number_of_hits):
    app.testing = True
    with app.test_client() as testclient:
        results = testclient.get('/search', headers=headers, data={'q': query})
        assert 'hits' in results.json
        actual_number = len(results.json['hits'])
        assert actual_number == expected_number_of_hits, f"wrong number of hits for query '{query}'"
