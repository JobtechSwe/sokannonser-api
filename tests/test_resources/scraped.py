import json


def get_scraped(session, url, params, check_for_http_error=True):
    response = session.get(f"{url}/joblinks", params=params)
    if check_for_http_error:
        response.raise_for_status()
        return json.loads(response.content.decode('utf8'))
    return response


def check_required_ad_fields_not_none(hit):
    assert hit['id'] is not None
    assert hit['external_id'] is not None
    assert hit['webpage_url'] is not None
    assert hit['headline'] is not None
    assert hit['hashsum'] is not None
    assert len(hit) == 10


def check_ids(actual, expected):
    assert len(actual) == len(expected)
    for ad_id in expected:
        assert ad_id in actual, f"expected id {ad_id} was not found in the query result"

def get_actual_ad_ids(json_response):
    actual_ids = []
    for hit in json_response['hits']:
        actual_ids.append(hit['id'])
    print(actual_ids)
    return actual_ids

