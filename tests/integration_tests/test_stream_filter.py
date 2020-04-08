import json
import pytest
import requests

from tests.integration_tests.test_resources.settings import headers
from sokannonser.settings import OCCUPATION_CONCEPT_ID, LOCATION_CONCEPT_ID, OCCUPATION_LIST

import tests.integration_tests.test_resources.concept_ids.concept_ids_geo as geo
import tests.integration_tests.test_resources.concept_ids.occupation as work
import tests.integration_tests.test_resources.concept_ids.occupation_group as group
import tests.integration_tests.test_resources.concept_ids.occupation_field as field


@pytest.mark.parametrize('date, concept_id, expected', [
    ('2000-01-25T07:29:41', group.arbetsformedlare, 5),
    ('2000-01-25T07:29:41', work.mjukvaruutvecklare, 12)])
def test_check_number_of_ads(session, url, date, concept_id, expected):
    """
    Returns number of hits in the db. Looks a bit low for 'mjukvarutvecklare', but let's accept it for now
    """
    _get_stream_check_number_of_results(session, url, expected, param={'date': date, OCCUPATION_CONCEPT_ID: concept_id})


@pytest.mark.parametrize('date, work_1, work_2, expected', [
    ('2000-01-25T07:29:41', work.mjukvaruutvecklare, group.arbetsformedlare, 12),  # last param is used
    ('2000-01-25T07:29:41', group.arbetsformedlare, work.mjukvaruutvecklare, 12)])
def test_compare_order_of_occupation_params(session, url, date, work_1, work_2, expected):
    """
    Expected behaviour:
    - date AND (work_1 OR work_2).
    - same result from both queries
    Actual behaviour:
    - looks like only last param is used
    """
    _get_stream_check_number_of_results(session, url, expected, param={'date': date, OCCUPATION_CONCEPT_ID: work_1,
                                                                       OCCUPATION_CONCEPT_ID: work_2})


@pytest.mark.parametrize('date, concept_id, expected', [
    ('2000-01-01T00:00:01', work.personlig_assistent, 54),
    ('2020-01-01T00:00:01', work.personlig_assistent, 54),
    ('2020-02-01T00:00:01', work.personlig_assistent, 51),
    ('2020-03-01T00:00:01', work.personlig_assistent, 46),
    ('2020-03-15T00:00:01', work.personlig_assistent, 33),
    ('2020-04-01T00:00:01', work.personlig_assistent, 0),
    ('2020-01-01T00:00:01', work.apotekschef, 2),
    ('2020-02-01T00:00:01', work.apotekschef, 2),
    ('1990-02-25T07:29:41', work.mjukvaruutvecklare, 12),
    ('2020-02-25T07:29:41', work.mjukvaruutvecklare, 10),
    ('2020-03-25T07:29:41', work.mjukvaruutvecklare, 2),
    ('2020-04-25T07:29:41', work.mjukvaruutvecklare, 0),
    ('2000-01-25T07:29:41', group.arbetsformedlare, 5)

])
def test_filter_concept_id_for_one_occupation(session, url, date, concept_id, expected):
    """
    test of filtering in /stream: should return results based on date AND occupation-related concept_id
    """
    _get_stream_check_number_of_results(session, url, expected, param={'date': date, OCCUPATION_CONCEPT_ID: concept_id})


@pytest.mark.parametrize('date, work_1, work_2, expected', [
    ('2000-01-01T00:00:01', work.account_manager, work.cykelbud, 1),  # only 1 ad?
    ('1458-01-01T00:00:01', work.mjukvaruutvecklare, group.arbetsformedlare, 5),
    ('2020-01-01T00:00:01', work.mjukvaruutvecklare, group.arbetsformedlare, 5),
    ('2020-02-01T00:00:01', work.administrativ_chef, field.militart_arbete, 1),
    ('2020-01-01T00:00:01', group.bagare_och_konditorer, group.bartendrar, 2),
    ('2020-02-01T00:00:01', group.apotekare, field.data_it, 75),
    ('2020-02-25T07:29:41', group.frisorer, work.akupunktor, 1),
    ('2020-03-25T07:29:41', field.pedagogiskt_arbete, field.halso__och_sjukvard, 54),
    ('2020-04-25T07:29:41', field.hantverksyrken, group.hudterapeuter, 0),
    ('2020-04-25T07:29:41', field.socialt_arbete, work.databasutvecklare, 0)])
def test_filter_with_date_and_two_occupations(session, url, date, work_1, work_2, expected):
    """
    test of filtering in /stream with date and 2 occupation-related concept_ids
    should return results based on both date AND (work_1 OR work_2)
    """
    _get_stream_check_number_of_results(session, url, expected,
                                        param={'date': date, OCCUPATION_CONCEPT_ID: work_1,
                                               OCCUPATION_CONCEPT_ID: work_2})


@pytest.mark.parametrize('date, work_1, work_2, work_3, expected', [
    ('2000-01-01T00:00:01', work.account_manager, work.cykelbud, work.databasutvecklare, 1),  # check
    ('2020-01-01T00:00:01', work.mjukvaruutvecklare, work.databasutvecklare, group.arbetsformedlare, 5),
    ('2020-02-01T00:00:01', work.administrativ_chef, work.apotekschef, field.militart_arbete, 1),
    ('2020-01-01T00:00:01', group.bagare_och_konditorer, group.bartendrar, group.hovmastare_och_servitorer, 6),
    ('2020-02-01T00:00:01', group.apotekare, group.ambulanssjukskoterskor_m_fl_, field.data_it, 75),
    ('2020-02-25T07:29:41', group.frisorer, group.hudterapeuter, work.akupunktor, 1),
    ('1980-03-25T07:29:41', field.pedagogiskt_arbete, field.halso__och_sjukvard, field.kropps__och_skonhetsvard, 5),
    ('2020-03-25T07:29:41', field.pedagogiskt_arbete, field.halso__och_sjukvard, field.kropps__och_skonhetsvard, 0),
    ('2000-04-25T07:29:41', field.hantverksyrken, field.data_it, group.hudterapeuter, 1),
    ('2020-04-25T07:29:41', field.hantverksyrken, field.data_it, group.hudterapeuter, 0),
    ('2009-04-25T07:29:41', field.hantverksyrken, field.data_it, group.hudterapeuter, 1),
    ('1920-04-25T07:29:41', field.socialt_arbete, field.bygg_och_anlaggning, work.databasutvecklare, 1),
    ('2020-04-25T07:29:41', field.socialt_arbete, field.bygg_och_anlaggning, work.databasutvecklare, 0)
])
def test_filter_with_date_and_three_occupations(session, url, date, work_1, work_2, work_3, expected):
    """
    test of filtering in /stream with date and 2 occupation-related concept_ids
    should return results based on date AND (work_1 OR work_2 OR work 3)
    """
    _get_stream_check_number_of_results(session, url, expected,
                                        param={'date': date, OCCUPATION_CONCEPT_ID: work_1,
                                               OCCUPATION_CONCEPT_ID: work_2, OCCUPATION_CONCEPT_ID: work_3})


@pytest.mark.parametrize('date, work, geo, expected', [
    ('2000-01-01T00:00:01', work.arbetsterapeut, geo.mellerud, 1),  # There should be at least one: "id": "23956007"
    ('2020-01-01T00:00:01', group.apotekare, geo.sverige, 1),
    ('2020-02-01T00:00:01', field.militart_arbete, geo.schweiz, 0),
    ('2000-02-01T00:00:01', field.militart_arbete, geo.sverige, 1),
])
def test_filter_with_date_and_work_and_location(session, url, date, work, geo, expected):
    """
    should return results based on date AND occupation type AND location
    """
    _get_stream_check_number_of_results(session, url, expected,
                                        param={'date': date, OCCUPATION_CONCEPT_ID: work, LOCATION_CONCEPT_ID: geo})


@pytest.mark.parametrize('date, work_1, work_2, geo_1, expected', [
    ('2000-01-01T00:00:01', work.arbetsterapeut, work.bussforare_busschauffor, geo.sverige, 9999),
    ('2000-01-01T00:00:01', work.arbetsterapeut, group.apotekare, geo.stockholms_lan, 9999),
    ('2000-01-01T00:00:01', work.arbetsterapeut, field.kropps__och_skonhetsvard, geo.norge, 9999),
    ('2020-01-01T00:00:01', group.apotekare, group.apotekare, geo.hallands_lan, 9999),
    ('2020-01-01T00:00:01', group.apotekare, group.hovmastare_och_servitorer, geo.linkoping, 9999),
    ('2020-01-01T00:00:01', group.apotekare, group.arbetsformedlare, geo.sverige, 9999),
    ('2020-02-01T00:00:01', field.militart_arbete, field.hantverksyrken, geo.stockholm, 9999),
    ('2020-02-01T00:00:01', field.militart_arbete, group.ambulanssjukskoterskor_m_fl_, geo.jonkopings_lan, 9999),
    ('2020-02-01T00:00:01', field.militart_arbete, work.bussforare_busschauffor, geo.norge, 9999),
    ('2020-01-01T00:00:01', group.mjukvaru__och_systemutvecklare_m_fl_, geo.dalarnas_lan, geo.schweiz, 9999),
    ('2020-02-01T00:00:01', work.bussforare_busschauffor, geo.schweiz, geo.norge, 9999)])
def test_filter_with_date_and_two_work_and_locations(session, url, date, work_1, work_2, geo_1, expected):
    """
    should return results based on date AND location AND (work_1 OR work_2)
    """
    _get_stream_check_number_of_results(session, url, expected,
                                        param={'date': date, OCCUPATION_CONCEPT_ID: work_1,
                                               OCCUPATION_CONCEPT_ID: work_2,
                                               LOCATION_CONCEPT_ID: geo_1})


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
    ('2020-01-01T00:00:01', group.mjukvaru__och_systemutvecklare_m_fl_, geo.dalarnas_lan, geo.schweiz, 9999),
    ('2020-02-01T00:00:01', work.bussforare_busschauffor, geo.schweiz, geo.norge, 9999)])
def test_filter_with_date_and_work_and_two_locations(session, url, date, work, geo_1, geo_2, expected):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    _get_stream_check_number_of_results(session, url, expected,
                                        param={'date': date, OCCUPATION_CONCEPT_ID: work, LOCATION_CONCEPT_ID: geo_1,
                                               LOCATION_CONCEPT_ID: geo_2})


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
