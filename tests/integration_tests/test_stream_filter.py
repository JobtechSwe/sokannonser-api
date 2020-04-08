import json
import pytest
import requests

import tests.integration_tests.test_resources.concept_ids.concept_ids_geo as geo
import tests.integration_tests.test_resources.concept_ids.occupation as work
import tests.integration_tests.test_resources.concept_ids.occupation_group as group
import tests.integration_tests.test_resources.concept_ids.occupation_field as field
from tests.integration_tests.test_resources.settings import headers


@pytest.mark.parametrize('date, concept_id, expected', [
    ('2000-01-01T00:00:01', work.personlig_assistent, 33),
    ('2020-01-01T00:00:01', work.personlig_assistent, 9999),
    ('2020-02-01T00:00:01', work.personlig_assistent, 9999),
    ('2020-01-01T00:00:01', work.apotekschef, 9999),
    ('2020-02-01T00:00:01', work.apotekschef, 9999),
    ('2020-02-25T07:29:41', work.mjukvaruutvecklare, 9999),
    ('2020-03-25T07:29:41', work.mjukvaruutvecklare, 9999),
    ('2020-04-25T07:29:41', work.mjukvaruutvecklare, 9999)
])
def test_filter_concept_id_for_occupation(session, url, date, concept_id, expected):
    """
    test of filtering in /stream: should return results based on date AND occupation-related concept_id
    """
    _get_stream_check_number_of_results(session, url, expected, param={'date': date, 'filter': concept_id})


@pytest.mark.parametrize('date, work_1, work_2, expected_number', [
    ('2000-01-01T00:00:01', work.account_manager, work.cykelbud, 9999),
    ('2020-01-01T00:00:01', work.mjukvaruutvecklare, group.arbetsformedlare, 9999),
    ('2020-02-01T00:00:01', work.administrativ_chef, field.militart_arbete, 9999),
    ('2020-01-01T00:00:01', group.bagare_och_konditorer, group.bartendrar, 9999),
    ('2020-02-01T00:00:01', group.apotekare, field.data_it, 9999),
    ('2020-02-25T07:29:41', group.frisorer, work.akupunktor, 9999),
    ('2020-03-25T07:29:41', field.pedagogiskt_arbete, field.halso__och_sjukvard, 9999),
    ('2020-04-25T07:29:41', field.hantverksyrken, group.hudterapeuter, 9999),
    ('2020-04-25T07:29:41', field.socialt_arbete, work.databasutvecklare, 9999)])
def test_filter_with_date_and_multiple_concept_id(session, url, date, work_1, work_2, expected_number):
    """
    test of filtering in /stream with date and 2 occupation-related concept_ids
    should return results based on both date AND (work_1 OR work_2)
    """
    _get_stream_check_number_of_results(session, url, expected_number,
                                        param={'date': date, 'filter': work_1, 'filter': work_2})


@pytest.mark.parametrize('date, work, geo, expected_number', [
    ('2000-01-01T00:00:01', work.arbetsterapeut, geo.arboga, 33),
    ('2020-01-01T00:00:01', group.apotekare, geo.dalarnas_lan, 9999),
    ('2020-02-01T00:00:01', field.militart_arbete, geo.schweiz, 9999)])
def test_filter_with_date_and_work_and_geographical(session, url, date, work, geo, expected_number):
    """
    should return results based on date AND occupation type AND location
    """
    _get_stream_check_number_of_results(session, url, expected_number,
                                        param={'date': date, 'filter': work, 'filter': geo})


@pytest.mark.parametrize('date, work, geo_1, geo_2, expected', [
    ('2000-01-01T00:00:01', work.arbetsterapeut, geo.arboga, geo.falun, 9999),
    ('2000-01-01T00:00:01', work.arbetsterapeut, geo.arboga, geo.stockholms_lan, 9999),
    ('2000-01-01T00:00:01', work.arbetsterapeut, geo.arboga, geo.norge, 9999),
    ('2020-01-01T00:00:01', group.apotekare, geo.dalarnas_lan, geo.hallands_lan, 9999),
    ('2020-01-01T00:00:01', group.apotekare, geo.dalarnas_lan, geo.linkoping, 9999),
    ('2020-01-01T00:00:01', group.apotekare, geo.dalarnas_lan, geo.sverige, 9999),
    ('2020-02-01T00:00:01', field.militart_arbete, geo.schweiz, geo.stockholm, 9999),
    ('2020-02-01T00:00:01', field.militart_arbete, geo.schweiz, geo.jonkopings_lan, 9999),
    ('2020-02-01T00:00:01', field.militart_arbete, geo.schweiz, geo.norge, 9999),
])
def test_filter_with_date_and_work_and_two_geographical(session, url, date, work, geo_1, geo_2, expected):
    """
    should return results based on date AND occupation type AND location
    """
    _get_stream_check_number_of_results(session, url, expected,
                                        param={'date': date, 'filter': work, 'filter': geo_1, 'filter': geo_2})


# are concept ids case sensitive?

# test below for comparison of number of hits for different dates
@pytest.mark.parametrize('date, expected_number', [
    ('2000-01-01T00:00:01', 1065),
    ('2020-01-01T00:00:01', 1032),
    ('2020-02-01T00:00:01', 971),
    ('2020-02-25T07:29:41', 872),
    ('2020-03-25T07:29:41', 273),
    ('2020-04-25T07:29:41', 0)])
def test_filter_date(session, url, date, expected_number):
    _get_stream_check_number_of_results(session, url, expected_number, param={'date': date})


def _get_stream_check_number_of_results(session, url, expected_number, param):
    response = session.get(f"{url}/stream", params=param)
    response.raise_for_status()
    assert response.content is not None
    list_of_ads = json.loads(response.content.decode('utf8'))
    assert len(list_of_ads) == expected_number, f'expected {expected_number} but got {len(list_of_ads)} ads'


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
    """
    returns an url

    """
    base_url = 'localhost'  # from ENV
    port = 5000  # from env
    return f"http://{base_url}:{port}"
