import sys
import json
import pytest
import requests
from tests.test_resources.scraped import get_scraped
from tests.test_resources.settings import NUMBER_OF_SCRAPED_ADS


@pytest.mark.parametrize("offset, wrong_offset",
                         [(100, False), (1000, False), (2000, False), (2001, True), (-1, True), (0, False),
                          (-2001, True)])
def test_too_big_offset(session_scraped, scraped_url, offset, wrong_offset):
    print('===================', sys._getframe().f_code.co_name, '================== ')
    response = get_scraped(session_scraped, scraped_url, params={'offset': offset, 'limit': '0'},
                           check_for_http_error=False)
    response_json = json.loads(response.content.decode('utf8'))
    if wrong_offset:
        assert response.status_code == requests.codes.bad_request
        assert "argument must be within the range 0 - 2000" in response_json['errors']['offset']
        assert 'Input payload validation failed' in str(response.text)
    else:
        response.raise_for_status()


@pytest.mark.scraped
@pytest.mark.parametrize("limit", [2, 5, 9, 10, 11, 22, 99, 100])
def test_offset(session_scraped, scraped_url, limit):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    for offset in range(0, NUMBER_OF_SCRAPED_ADS, limit):
        json_response = get_scraped(session_scraped, scraped_url, params={'offset': offset, 'limit': limit})
        hits = json_response['hits']
        for hit in hits:
            assert hit['id'] is not None
        if NUMBER_OF_SCRAPED_ADS - offset >= limit:
            expected = limit
        else:
            expected = NUMBER_OF_SCRAPED_ADS % limit
        assert len(hits) == expected
