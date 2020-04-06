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


"""
Bygg och anläggning 40
Chefer och verksamhetsledare 32
Data/IT 85
Försäljning, inköp, marknadsföring 103
Hantverksyrken 6
Hotell, restaurang, storhushåll 55
Hälso- och sjukvård 194
Industriell tillverkning 37
Installation, drift, underhåll 42
Kropps- och skönhetsvård 5
Kultur, media, design 10
Militärt arbete 1
Naturbruk 7
Naturvetenskapligt arbete 11
Pedagogiskt arbete 135
Sanering och renhållning 24
Socialt arbete 95
Säkerhetsarbete 11
Tekniskt arbete 41
Transport 47"""


@pytest.mark.parametrize('date, occupation_field, expected_number', [
    ('2000-01-01T00:00:01', 'Hantverksyrken', 9999),
    ('2000-01-01T00:00:01', 'Hantverksyrken', 9999),
    ('2020-01-01T00:00:01', 'Hantverksyrken', 9999),
    ('2020-01-01T00:00:01', 'Data/IT', 9999),
    ('2020-02-01T00:00:01', 'Data/IT', 9999),
    ('2020-03-25T07:29:41', 'Försäljning, inköp, marknadsföring', 9999),
    ('2020-04-25T07:29:41', 'Hälso- och sjukvård', 9999)
])
def test_filter(session, url, date, occupation_field, expected_number):
    filter_param = {'date': date, 'occupation': occupation_field}
    response = session.get(f"{url}/stream", params=filter_param)
    response.raise_for_status()
    list_of_ads = json.loads(response.content.decode('utf8'))
    assert expected_number == len(list_of_ads), f'expected {expected_number} but got {len(list_of_ads)} ads'
    print(f'{len(list_of_ads)} for occupation {occupation_field}')

    # the query only seems to filter on date, not on occupation_field.
    # number of hits with 'occupation' param is the same as without it


# test below for comaprison of number of hits for different dates
@pytest.mark.parametrize('date, expected_number', [
    ('2000-01-01T00:00:01', 1065),
    ('2020-01-01T00:00:01', 1032),
    ('2020-02-01T00:00:01', 971),
    ('2020-03-25T07:29:41', 273),
    ('2020-04-25T07:29:41', 0)])
def test_filter_with_date_and_occupation_field(session, url, date, expected_number):
    date_param = {'date': date}
    response = session.get(f"{url}/stream", params=date_param)
    response.raise_for_status()
    list_of_ads = json.loads(response.content.decode('utf8'))
    assert expected_number == len(list_of_ads), f'expected {expected_number} but got {len(list_of_ads)} ads'
