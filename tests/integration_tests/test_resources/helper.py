import json


def get_stream_check_number_of_results(session, url, expected_number, params):
    response = session.get(f"{url}/stream", params=params)
    _check_ok_response_and_number_of_ads(response, expected_number)


def get_search_check_number_of_results(session, url, expected_number, params):
    response = session.get(f"{url}/search", params=params)
    return _check_ok_response_and_number_of_ads(response, expected_number)


def get_stream_expect_error(session, url, path, params, expected_http_code):
    r = session.get(f"{url}{path}", params=params)
    status = r.status_code
    assert status == expected_http_code, f"Expected http return code to be {expected_http_code} , but got {status}"


def get_snapshot_check_number_of_results(session, url, expected_number):
    response = session.get(f"{url}/snapshot")
    return _check_ok_response_and_number_of_ads(response, expected_number)


def _check_ok_response_and_number_of_ads(response, expected_number):
    response.raise_for_status()
    assert response.content is not None
    list_of_ads = json.loads(response.content.decode('utf8'))
    if '/search' in response.url:
        list_of_ads = list_of_ads['hits']
    assert len(list_of_ads) == expected_number, f'expected {expected_number} but got {len(list_of_ads)} ads'

    for ad in list_of_ads:
        assert isinstance(ad['id'], str)
        checks = []
        checks.append(ad['id'])
        checks.append(ad['headline'])
        checks.append(ad['description'])
        checks.append(ad['occupation'])
        checks.append(ad['workplace_address']['country'])
        for c in checks:
            assert c is not None, ad['id']
    return response


def check_freetext_concepts(free_text_concepts, list_of_expected):
    assert free_text_concepts['skill'] == list_of_expected[0]
    assert free_text_concepts['occupation'] == list_of_expected[1]
    assert free_text_concepts['location'] == list_of_expected[2]
    assert free_text_concepts['skill_must'] == list_of_expected[3]
    assert free_text_concepts['occupation_must'] == list_of_expected[4]
    assert free_text_concepts['location_must'] == list_of_expected[5]
    assert free_text_concepts['skill_must_not'] == list_of_expected[6]
    assert free_text_concepts['occupation_must_not'] == list_of_expected[7]
    assert free_text_concepts['location_must_not'] == list_of_expected[8]
