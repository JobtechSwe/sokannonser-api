import pytest

from tests.test_resources.helper import get_with_path_return_json, compare


@pytest.mark.smoke
@pytest.mark.parametrize("query, expected_number_of_hits", [
    ('#corona', 0),
    ('corona', 0),
    ('#jobbjustnu', 6),
    ('jobbjustnu', 1),
    ('#metoo', 1),
    ('metoo', 0),
    ('#wedo', 1),
    ('wedo', 0)
])
@pytest.mark.integration
def test_hashtag_search(session, search_url, query, expected_number_of_hits):
    response_json = get_with_path_return_json(session, search_url, '/search', params={'q': query})
    compare(response_json['total']['value'], expected_number_of_hits, msg=f"Query: {query}")
