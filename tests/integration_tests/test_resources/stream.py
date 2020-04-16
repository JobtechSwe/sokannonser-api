import json
import requests


def get_stream_check_number_of_results(session, url, expected_number, params):
    response = session.get(f"{url}/stream", params=params)
    response.raise_for_status()
    assert response.content is not None
    list_of_ads = json.loads(response.content.decode('utf8'))
    assert len(list_of_ads) == expected_number, f'expected {expected_number} but got {len(list_of_ads)} ads'


def get_stream_expect_error(session, url, params, expected_http_code):
    r = session.get(f"{url}/stream", params=params)
    status = r.status_code
    assert status == expected_http_code, f"Expected http return code to be {expected_http_code} , but got {status}"
