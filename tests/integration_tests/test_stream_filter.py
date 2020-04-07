import os
import requests
import json
import pytest

number_of_ads = 1065
test_api_key = os.getenv('TEST_API_KEY')
headers = {'api-key': test_api_key, 'accept': 'application/json'}


@pytest.fixture
def session(scope="session"):
    """
    creates a Session object which will persist over the entire test run ("session").
    http connections will be reused (higher performance, less resource usage)
    Returns a Session object
    """
    s = requests.sessions.Session()
    s.headers.update(headers)
    return s


@pytest.fixture
def url(scope="session"):
    base_url = 'localhost'  # from ENV
    port = 5000  # from env
    return f"http://{base_url}:{port}"


# todo: adjust expected_number to reality
@pytest.mark.parametrize('date, concept_id, expected_number', [
    ('2000-01-01T00:00:01', 'PaxQ_o1G_wWH', 9999),
    ('2020-01-01T00:00:01', 'PaxQ_o1G_wWH', 9999),
    ('2020-02-01T00:00:01', 'PaxQ_o1G_wWH', 9999),
    ('2020-01-01T00:00:01', 'yhCP_AqT_tns', 9999),
    ('2020-02-01T00:00:01', 'yhCP_AqT_tns', 9999),
    ('2020-02-25T07:29:41', 'MVqp_eS8_kDZ', 9999),
    ('2020-03-25T07:29:41', 'MVqp_eS8_kDZ', 9999),
    ('2020-04-25T07:29:41', '6Hq3_tKo_V57', 9999)
])
def test_filter_with_date_and_concept_id(session, url, date, concept_id, expected_number):
    """
    test of filtering in /stream
    should return results based on both date and occupation_field
    :param session:
    :param url:
    :param date:
    :param occupation_field:
    :param expected_number:
    :return:
    """
    list_of_ads = _get_stream(session, url, param={'date': date, 'filter': concept_id})
    assert len(list_of_ads) == expected_number, f'expected {expected_number} but got {len(list_of_ads)} ads'

    # the query only seems to filter on date, not on occupation_field.
    # number of hits with 'occupation' param is the same as without it


# are concept ids case sensitive?

# test below for comparison of number of hits for different dates
@pytest.mark.parametrize('date, expected_number', [
    ('2000-01-01T00:00:01', 1065),
    ('2020-01-01T00:00:01', 1032),
    ('2020-02-01T00:00:01', 971),
    ('2020-03-25T07:29:41', 273),
    ('2020-04-25T07:29:41', 0)])
def test_filter_date(session, url, date, expected_number):
    list_of_ads = _get_stream(session, url, param={'date': date})
    assert expected_number == len(list_of_ads), f'expected {expected_number} but got {len(list_of_ads)} ads'


def _get_stream(session, url, param):
    response = session.get(f"{url}/stream", params=param)
    response.raise_for_status()
    assert response.content is not None
    return json.loads(response.content.decode('utf8'))
