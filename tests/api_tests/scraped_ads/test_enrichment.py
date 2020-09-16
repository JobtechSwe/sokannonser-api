import sys

import pytest

from tests.test_resources.scraped import get_scraped, get_actual_ad_ids, check_ids


@pytest.mark.parametrize("query, expected_ids", [
    ('stresstålig', [19769, 43643, 19764, 43645, 19765, 43655]),
    ('barnmorskor',['17701']),
])
def test_enrichment(session_scraped, scraped_url, query, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'q': query, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)