import pytest

from sokannonser import app
from sokannonser.settings import headers


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.parametrize("limit, stats_limit, expected_number_of_hits", [
    (10, 10, 10),
    (10, 15, 10),
    (15, 15, 15),
    (15, 20, 15),
    (20, 20, 20),
])
def test_stats(limit, stats_limit, expected_number_of_hits):
    app.testing = True
    with app.test_client() as testclient:
        data = {'stats': 'region', 'offset': 0, 'limit': limit, 'stats.limit': stats_limit}
        results = testclient.get('/search', headers=headers, data=data)
        assert len(results.json['hits']) == expected_number_of_hits, f"wrong number of hits"
