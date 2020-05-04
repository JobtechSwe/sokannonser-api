import pytest

from sokannonser import app
from sokannonser.settings import headers
from tests.integration_tests.test_resources.concept_ids import concept_ids_geo as geo


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.parametrize("limit, stats_limit, expected_number_of_hits, expected_values", [
    (10, 0, 10, 5),
    (10, 10, 10, 10),
    (10, 15, 10, 15)
])
def test_stats(limit, stats_limit, expected_number_of_hits, expected_values):
    app.testing = True
    with app.test_client() as testclient:
        data = {'stats': 'region', 'offset': 0, 'limit': limit, 'stats.limit': stats_limit}
        results_json = testclient.get('/search', headers=headers, data=data).json
        assert len(results_json['hits']) == expected_number_of_hits, f"wrong number of hits"
        assert len(results_json['stats'][0]['values']) == expected_values, f"wrong number of entries in [values]"


def test_stats_details():
    app.testing = True
    with app.test_client() as testclient:
        i = 0
        data = {'stats': 'region', 'offset': 0, 'limit': 10, 'stats.limit': 5}
        results_json = testclient.get('/search', headers=headers, data=data).json
        assert len(results_json['hits']) == 10, f"wrong number of hits"
        assert len(results_json['stats'][0]['values']) == 5, f"wrong number of entries in [values]"

        expected_results = [('Stockholms län', 289, geo.stockholms_lan, '01'),
                            ('Västra Götalands län', 173, geo.vastra_gotalands_lan, '14'),
                            ('Skåne län', 120, geo.skane_lan, '12'),
                            ('Jönköpings län', 56, geo.jonkopings_lan, '06'),
                            ('Östergötlands län', 45, geo.ostergotlands_lan, '05')]

        for r in results_json['stats'][0]['values']:  # results should be sorted
            assert r['term'] == expected_results[i][0]
            assert r['count'] == expected_results[i][1]
            assert r['concept_id'] == expected_results[i][2]
            assert r['code'] == expected_results[i][3]
            i += 1
