import pytest
from tests.test_resources.helper import get_search
from tests.test_resources.settings import TEST_USE_STATIC_DATA


@pytest.mark.skipif(TEST_USE_STATIC_DATA)
def test_search_relevance_multiple_times(session, search_url):
    params = {'q': 'software developer',
              'country': 'i46j_HmG_v64',
              'relevance-threshold': 1,
              'offset': 0,
              'limit': 10,
              'sort': 'relevance'}

    old_total = 999999
    old_pos = 999999
    retries = 1

    for i in range(retries):
        result = get_search(session, search_url, params)
        total = result['total']
        pos = result['positions']
        print(f"Total: {total}, positions: {pos}")

        if i > 0:
            pass
            # Todo: once bug is fixed, enable checks below
            # assert old_total == total
        # assert old_pos == pos
        old_total = total
        old_pos = pos
