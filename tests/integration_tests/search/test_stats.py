import pytest

from tests.integration_tests.test_resources.concept_ids import concept_ids_geo as geo
from tests.integration_tests.test_resources.helper import get_with_path_return_json


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.parametrize("limit, stats_limit, expected_number_of_hits, expected_values", [
    (10, 0, 10, 5),
    (10, 10, 10, 10),
    (10, 15, 10, 15)
])
def test_stats(session, search_url, limit, stats_limit, expected_number_of_hits, expected_values):
    params = {'stats': 'region', 'offset': 0, 'limit': limit, 'stats.limit': stats_limit}
    results_json = get_with_path_return_json(session, search_url, '/search', params)
    assert len(results_json['hits']) == expected_number_of_hits, f"wrong number of hits"
    assert len(results_json['stats'][0]['values']) == expected_values, f"wrong number of entries in [values]"


def test_stats_details(session, search_url):
    params = {'stats': 'region', 'offset': 0, 'limit': 10, 'stats.limit': 5}
    results_json = get_with_path_return_json(session, search_url, '/search', params)

    expected_results = [('Stockholms län', 289, geo.stockholms_lan, '01'),
                        ('Västra Götalands län', 173, geo.vastra_gotalands_lan, '14'),
                        ('Skåne län', 120, geo.skane_lan, '12'),
                        ('Jönköpings län', 56, geo.jonkopings_lan, '06'),
                        ('Östergötlands län', 45, geo.ostergotlands_lan, '05')]

    for index, result in enumerate(results_json['stats'][0]['values']):  # results should be sorted
        assert result['term'] == expected_results[index][0]
        assert result['count'] == expected_results[index][1]
        assert result['concept_id'] == expected_results[index][2]
        assert result['code'] == expected_results[index][3]
