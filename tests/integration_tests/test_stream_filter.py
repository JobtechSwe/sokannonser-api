import json
import pytest
import requests

from tests.integration_tests.test_resources.settings import headers
from sokannonser.settings import OCCUPATION_CONCEPT_ID, LOCATION_CONCEPT_ID

import tests.integration_tests.test_resources.concept_ids.concept_ids_geo as geo
import tests.integration_tests.test_resources.concept_ids.occupation as work
import tests.integration_tests.test_resources.concept_ids.occupation_group as group
import tests.integration_tests.test_resources.concept_ids.occupation_field as field


@pytest.mark.parametrize('date, work, expected', [
    ('2000-01-25T07:29:41', group.arbetsformedlare, 5),
    ('2000-01-25T07:29:41', group.apotekare, 2),
    ('2000-01-25T07:29:41', group.mjukvaru__och_systemutvecklare_m_fl_, 57),
    ('2000-01-25T07:29:41', work.mjukvaruutvecklare, 12),
    ('2000-01-01T00:00:01', work.arbetsterapeut, 5)])
def test_check_number_of_ads(session, url, date, work, expected):
    """
    Returns number of hits in the db. Looks a bit low for 'mjukvarutvecklare', but let's accept it for now
    """
    _get_stream_check_number_of_results(session, url, expected, param={'date': date, OCCUPATION_CONCEPT_ID: work})


@pytest.mark.parametrize('date, work, geo, expected', [
    ('2020-01-01T00:00:01', work.arbetsterapeut, geo.mellerud, 1),
    ('2020-04-01T00:00:01', work.arbetsterapeut, geo.mellerud, 0),
    ('2020-02-01T00:00:01', work.barista_kaffebartender, geo.sverige, 1),
    ('2020-02-01T00:00:01', work.bussforare_busschauffor, geo.norge, 1),
    ('2020-03-01T00:00:01', work.larare_i_grundskolan__arskurs_7_9, geo.goteborg, 1),
    ('2020-01-01T00:00:01', group.apotekare, geo.sverige, 2),
    ('1999-01-01T00:00:01', group.mjukvaru__och_systemutvecklare_m_fl_, geo.sverige, 56),
    ('1999-01-01T00:00:01', group.mjukvaru__och_systemutvecklare_m_fl_, geo.schweiz, 1),
    ('2020-01-01T00:00:01', group.mjukvaru__och_systemutvecklare_m_fl_, geo.sverige, 51),
    ('2020-02-01T00:00:01', field.militart_arbete, geo.schweiz, 0),
    ('2000-02-01T00:00:01', field.militart_arbete, geo.sverige, 1),
    ('2000-01-01T00:00:01', field.halso__och_sjukvard, geo.sverige, 194),
    ('2000-01-01T00:00:01', field.halso__och_sjukvard, geo.stockholms_lan, 43),
    ('2020-02-25T00:00:01', field.halso__och_sjukvard, geo.sverige, 158),
    ('2020-02-25T00:00:01', field.halso__och_sjukvard, geo.stockholms_lan, 35),
])
def test_filter_with_date_and_work_and_location(session, url, date, work, geo, expected):
    """
    should return results based on date AND occupation type AND location
    """
    _get_stream_check_number_of_results(session, url, expected,
                                        param={'date': date, OCCUPATION_CONCEPT_ID: work, LOCATION_CONCEPT_ID: geo})


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
    ('2000-01-25T07:29:41', group.arbetsformedlare, 5),
    ('2000-01-25T07:29:41', field.militart_arbete, 1),
    ('2000-01-25T07:29:41', field.socialt_arbete, 95),
    ('2000-01-25T07:29:41', work.administrativ_chef, 1),
    ('2000-01-25T07:29:41', work.account_manager, 3),
    ('2000-01-25T07:29:41', work.cykelbud, 1),
])
def test_filter_concept_id_for_one_occupation(session, url, date, concept_id, expected):
    """
    test of filtering in /stream: should return results based on date AND occupation-related concept_id
    """
    _get_stream_check_number_of_results(session, url, expected, param={'date': date, OCCUPATION_CONCEPT_ID: concept_id})


@pytest.mark.parametrize('date, geo, expected', [
    ('2000-01-01T00:00:01', geo.falun, 8),
    ('2000-01-01T00:00:01', geo.stockholms_lan, 289),
    ('2000-01-01T00:00:01', geo.norge, 3),
    ('2020-01-01T00:00:01', geo.hallands_lan, 29),
    ('2020-01-01T00:00:01', geo.linkoping, 23),
    ('1999-01-01T00:00:01', geo.sverige, 1059),
    ('2020-01-01T00:00:01', geo.sverige, 1026),
    ('2020-02-01T00:00:01', geo.stockholm, 172),
    ('2020-02-01T00:00:01', geo.schweiz, 1),
    ('2020-02-01T00:00:01', geo.norge, 3),
    ('2020-01-01T00:00:01', geo.dalarnas_lan, 20),
    ('2020-02-01T00:00:01', geo.norge, 3)])
def test_filter_with_date_and_location(session, url, date, geo, expected):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    param = {'date': date, LOCATION_CONCEPT_ID: geo}
    _get_stream_check_number_of_results(session, url, expected, param)


#   multiple params of same type


@pytest.mark.parametrize('date, work_1, work_2, expected', [
    ('2000-01-25T07:29:41', work.mjukvaruutvecklare, group.arbetsformedlare, 17),
    ('2000-01-25T07:29:41', group.arbetsformedlare, work.mjukvaruutvecklare, 17)])
def test_compare_order_of_occupation_params(session, url, date, work_1, work_2, expected):
    """
    Expected behaviour:
    - date AND (work_1 OR work_2).
    - same result from both queries
    - result is sum of both occupations
    Actual behaviour:
    - looks like only last param is used
    """
    _get_stream_check_number_of_results(session, url, expected,
                                        param={'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2]})


@pytest.mark.parametrize('date, work_1, work_2, expected', [
    ('2000-01-01T00:00:01', work.account_manager, work.cykelbud, 4),
    ('1458-01-01T00:00:01', work.mjukvaruutvecklare, group.arbetsformedlare, 17),
    ('2020-01-01T00:00:01', work.mjukvaruutvecklare, group.arbetsformedlare, 16),
    ('1920-02-01T00:00:01', work.administrativ_chef, field.militart_arbete, 2),
    ('1920-02-01T00:00:01', field.militart_arbete, work.administrativ_chef, 2),
    ('2020-01-01T00:00:01', group.bagare_och_konditorer, group.bartendrar, 5),
    ('2020-02-01T00:00:01', group.apotekare, field.data_it, 77),
    ('2020-02-25T07:29:41', group.frisorer, work.akupunktor, 3),
    ('2020-03-25T07:29:41', field.pedagogiskt_arbete, field.halso__och_sjukvard, 95),
    ('2020-02-25T07:29:41', field.hantverksyrken, group.hudterapeuter, 3),
    ('2020-01-25T07:29:41', field.socialt_arbete, work.databasutvecklare, 88)])
def test_filter_with_date_and_two_occupations(session, url, date, work_1, work_2, expected):
    """
    test of filtering in /stream with date and 2 occupation-related concept_ids
    should return results based on both date AND (work_1 OR work_2)
    """
    param = {'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2]}
    _get_stream_check_number_of_results(session, url, expected, param)


@pytest.mark.parametrize('date, work_1, work_2, work_3, expected', [
    ('2000-01-01T00:00:01', work.account_manager, work.cykelbud, work.databasutvecklare, 5),
    ('2020-01-01T00:00:01', work.mjukvaruutvecklare, work.databasutvecklare, group.arbetsformedlare, 17),
    ('2020-02-01T00:00:01', work.administrativ_chef, work.apotekschef, field.militart_arbete, 4),
    ('2020-01-01T00:00:01', group.bagare_och_konditorer, group.bartendrar, group.hovmastare_och_servitorer, 11),
    ('2020-02-01T00:00:01', group.apotekare, group.ambulanssjukskoterskor_m_fl_, field.data_it, 78),
    ('2020-02-25T07:29:41', group.frisorer, group.hudterapeuter, work.akupunktor, 3),
    ('1980-03-25T07:29:41', field.pedagogiskt_arbete, field.halso__och_sjukvard, field.kropps__och_skonhetsvard, 334),
    ('2020-03-25T07:29:41', field.pedagogiskt_arbete, field.halso__och_sjukvard, field.kropps__och_skonhetsvard, 95),
    ('2000-04-25T07:29:41', field.hantverksyrken, field.data_it, group.hudterapeuter, 92),
    ('2020-03-25T07:29:41', field.hantverksyrken, field.data_it, group.hudterapeuter, 17),
    ('1920-04-25T07:29:41', field.socialt_arbete, field.bygg_och_anlaggning, work.databasutvecklare, 136),
    ('2020-02-25T07:29:41', field.socialt_arbete, field.bygg_och_anlaggning, work.databasutvecklare, 112)
])
def test_filter_with_date_and_three_occupations(session, url, date, work_1, work_2, work_3, expected):
    """
    test of filtering in /stream with date and 2 occupation-related concept_ids
    should return results based on date AND (work_1 OR work_2 OR work 3)
    """
    _get_stream_check_number_of_results(session, url, expected,
                                        param={'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2, work_3]})


@pytest.mark.parametrize('date, work_1, work_2, geo_1, expected', [
    ('2000-01-01T00:00:01', work.arbetsterapeut, work.bussforare_busschauffor, geo.sverige, 6),
    ('2000-01-01T00:00:01', work.arbetsterapeut, group.apotekare, geo.stockholms_lan, 1),
    ('2000-01-01T00:00:01', work.arbetsterapeut, field.kropps__och_skonhetsvard, geo.norge, 0),
    ('2020-01-01T00:00:01', group.apotekare, group.apotekare, geo.sverige, 2),
    ('2020-01-01T00:00:01', group.apotekare, group.hovmastare_och_servitorer, geo.stockholms_lan, 3),
    ('2020-01-01T00:00:01', group.apotekare, group.arbetsformedlare, geo.sverige, 7),
    ('2020-02-01T00:00:01', field.militart_arbete, field.hantverksyrken, geo.stockholm, 1),
    ('2020-02-01T00:00:01', field.militart_arbete, group.ambulanssjukskoterskor_m_fl_, geo.jonkopings_lan, 0),
    ('2020-02-01T00:00:01', field.militart_arbete, work.bussforare_busschauffor, geo.norge, 1),
    ('2020-01-01T00:00:01', group.mjukvaru__och_systemutvecklare_m_fl_, geo.dalarnas_lan, geo.schweiz, 1),
    ('2020-02-01T00:00:01', work.bussforare_busschauffor, geo.schweiz, geo.norge, 1)])
def test_filter_with_date_and_two_work_and_locations(session, url, date, work_1, work_2, geo_1, expected):
    """
    should return results based on date AND location AND (work_1 OR work_2)
    results = work_1 + work_2 that matches location
    """
    _get_stream_check_number_of_results(session, url, expected,
                                        param={'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2],
                                               LOCATION_CONCEPT_ID: geo_1})


@pytest.mark.parametrize('date, geo_1, geo_2, expected', [
    ('2000-01-01T00:00:01', geo.arboga, geo.falun, 9),
    ('2000-01-01T00:00:01', geo.arboga, geo.stockholms_lan, 290),
    ('2000-01-01T00:00:01', geo.arboga, geo.norge, 4),
    ('2020-01-01T00:00:01', geo.dalarnas_lan, geo.hallands_lan, 49),
    ('2020-01-01T00:00:01', geo.dalarnas_lan, geo.linkoping, 43),
    ('2020-01-01T00:00:01', geo.dalarnas_lan, geo.sverige, 1026),
    ('2020-02-01T00:00:01', geo.schweiz, geo.stockholm, 173),
    ('2020-02-01T00:00:01', geo.schweiz, geo.jonkopings_lan, 51),
    ('2020-02-01T00:00:01', geo.schweiz, geo.norge, 4),
    ('2020-01-01T00:00:01', geo.dalarnas_lan, geo.schweiz, 21),
    ('2020-02-01T00:00:01', geo.schweiz, geo.norge, 4)])
def test_filter_with_date_and_two_locations(session, url, date, geo_1, geo_2, expected):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    param = {'date': date, LOCATION_CONCEPT_ID: [geo_1, geo_2]}
    _get_stream_check_number_of_results(session, url, expected, param)


@pytest.mark.parametrize('date, work, geo_1, geo_2, expected', [
    ('2000-01-01T00:00:01', work.arbetsterapeut, geo.arboga, geo.falun, 0),
    ('2000-01-01T00:00:01', work.arbetsterapeut, geo.arboga, geo.stockholms_lan, 1),
    ('2020-01-01T00:00:01', group.apotekare, geo.dalarnas_lan, geo.hallands_lan, 0),
    ('2020-01-01T00:00:01', group.apotekare, geo.dalarnas_lan, geo.linkoping, 0),
    ('2020-01-01T00:00:01', group.apotekare, geo.malta, geo.sverige, 2),
    ('2020-02-01T00:00:01', field.kultur__media__design, geo.schweiz, geo.stockholm, 1),
    ('2020-02-01T00:00:01', field.naturvetenskapligt_arbete, geo.schweiz, geo.stockholms_lan, 1),
    ('2020-02-01T00:00:01', field.bygg_och_anlaggning, geo.schweiz, geo.norge, 0),
    ('2020-01-01T00:00:01', group.mjukvaru__och_systemutvecklare_m_fl_, geo.dalarnas_lan, geo.schweiz, 1),
    ('2020-02-01T00:00:01', work.bussforare_busschauffor, geo.schweiz, geo.norge, 1)])
def test_filter_with_date_and_work_and_two_locations(session, url, date, work, geo_1, geo_2, expected):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    param = {'date': date, OCCUPATION_CONCEPT_ID: work, LOCATION_CONCEPT_ID: [geo_1, geo_2]}
    _get_stream_check_number_of_results(session, url, expected, param)


@pytest.mark.parametrize('work, expected', [
    (group.mjukvaru__och_systemutvecklare_m_fl_, 57),
    (group.mjukvaru__och_systemutvecklare_m_fl_.lower(), 0)])
def test_filter_with_lowercase_concept_id(session, url, work, expected):
    """
    compare correct concept_id with a lower case version
    """
    param = {'date': '2000-01-01T00:00:01', OCCUPATION_CONCEPT_ID: work}
    _get_stream_check_number_of_results(session, url, expected, param)


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
