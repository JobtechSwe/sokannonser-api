import pytest

from tests.integration_tests.test_resources.helper import get_with_path_return_json


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
def test_hashtag_search(session, search_url, query, expected_number_of_hits):
    json_response = get_with_path_return_json(session, search_url, '/search', params={'q': query})
    actual_number = len(json_response['hits'])
    assert actual_number == expected_number_of_hits, f"wrong number of hits for query '{query}'"
