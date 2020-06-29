import pytest

from tests.test_resources.concept_ids import concept_ids_geo as geo
from tests.test_resources.helper import get_with_path_return_json, compare


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
    compare(len(results_json['hits']), expected_number_of_hits)
    compare(len(results_json['stats'][0]['values']), expected_values)


def test_stats_details(session, search_url):
    params = {'stats': 'region', 'offset': 0, 'limit': 10, 'stats.limit': 5}
    results_json = get_with_path_return_json(session, search_url, '/search', params)

    expected_results = [('Stockholms län', 289, geo.stockholms_lan, '01'),
                        ('Västra Götalands län', 173, geo.vastra_gotalands_lan, '14'),
                        ('Skåne län', 120, geo.skane_lan, '12'),
                        ('Jönköpings län', 56, geo.jonkopings_lan, '06'),
                        ('Östergötlands län', 45, geo.ostergotlands_lan, '05')]

    for index, result in enumerate(results_json['stats'][0]['values']):  # results should be sorted
        compare(result['term'], expected_results[index][0])
        compare(result['count'], expected_results[index][1])
        compare(result['concept_id'], expected_results[index][2])
        compare(result['code'], expected_results[index][3])
