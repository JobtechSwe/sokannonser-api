import pytest
import requests
from sokannonser.settings import OCCUPATION_CONCEPT_ID, LOCATION_CONCEPT_ID

import tests.integration_tests.test_resources.concept_ids.concept_ids_geo as geo
import tests.integration_tests.test_resources.concept_ids.occupation as work
import tests.integration_tests.test_resources.concept_ids.occupation_group as group
import tests.integration_tests.test_resources.concept_ids.occupation_field as field
from tests.integration_tests.test_resources.stream import get_stream_check_number_of_results


@pytest.mark.skip("test for checking unexpected behaviour, remove when fixed")
@pytest.mark.parametrize('date, geo, expected', [('2000-01-25T07:29:41', geo.sverige, 1050), ])
def test_too_many_hits_for_location(session, url, date, geo, expected):
    """
    Returns number of hits in the db.
    Expected: 1050 hits (1056 hits - ads with location in other countries than 'sverige')
        can an ad have multiple countries?

    Actual result: 1059.  more than the actual number of ads in the test data

    add 'sverige' and the correct number of expected hits to 'test_only_location' when fixed
    """
    params = {'date': date, LOCATION_CONCEPT_ID: geo}
    get_stream_check_number_of_results(session, url, expected, params)


@pytest.mark.parametrize('date, work, expected', [
    ('2000-01-25T07:29:41', group.arbetsformedlare, 5),
    ('2000-01-25T07:29:41', group.apotekare, 2),
    ('2000-01-25T07:29:41', group.mjukvaru__och_systemutvecklare_m_fl_, 57),
    ('2000-01-25T07:29:41', work.mjukvaruutvecklare, 12),
    ('2000-01-01T00:00:01', work.arbetsterapeut, 5)])
def test_filter_only_on_occupation(session, url, date, work, expected):
    """
    Returns number of hits in the db. Temporary to verify results in other tests
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work}
    get_stream_check_number_of_results(session, url, expected, params)


@pytest.mark.parametrize('date, geo, expected', [
    ('2000-01-25T07:29:41', geo.aland_tillhor_finland, 1),
    ('2000-01-25T07:29:41', geo.norge, 3),
    ('2000-01-25T07:29:41', geo.malta, 1),
    ('2000-01-25T07:29:41', geo.schweiz, 1),
    ('2000-01-25T07:29:41', geo.kalmar_lan, 17),
    ('2000-01-25T07:29:41', geo.botkyrka, 5),
    ('2000-01-25T07:29:41', geo.stockholms_lan, 289),
    ('2000-01-01T00:00:01', geo.stockholm, 194)])
def test_filter_only_on_location(session, url, date, geo, expected):
    """
    Returns number of hits in the db. Temporary to verify results in other tests
    """
    params = {'date': date, LOCATION_CONCEPT_ID: geo}
    get_stream_check_number_of_results(session, url, expected, params)


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
def test_filter_with_date_and_occupation_and_location(session, url, date, work, geo, expected):
    """
    should return results based on date AND occupation type AND location
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work, LOCATION_CONCEPT_ID: geo}
    get_stream_check_number_of_results(session, url, expected, params)


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
def test_filter_with_date_and_one_occupation(session, url, date, concept_id, expected):
    """
    test of filtering in /stream: should return results based on date AND occupation-related concept_id
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: concept_id}
    get_stream_check_number_of_results(session, url, expected, params)


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
    should return results based on date AND occupation type AND location_1
    """
    params = {'date': date, LOCATION_CONCEPT_ID: geo}
    get_stream_check_number_of_results(session, url, expected, params)


#   multiple params of same type


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
    params = {'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2]}
    get_stream_check_number_of_results(session, url, expected, params)


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
    params = {'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2, work_3]}
    get_stream_check_number_of_results(session, url, expected, params=params)


@pytest.mark.smoke
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
def test_filter_with_date_and_two_occupations_and_location(session, url, date, work_1, work_2, geo_1, expected):
    """
    should return results based on date AND location AND (work_1 OR work_2)
    results = work_1 + work_2 that matches location
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2], LOCATION_CONCEPT_ID: geo_1}
    get_stream_check_number_of_results(session, url, expected, params)


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
    params = {'date': date, LOCATION_CONCEPT_ID: [geo_1, geo_2]}
    get_stream_check_number_of_results(session, url, expected, params)


@pytest.mark.parametrize('date, geo_list, expected', [
    ('2000-01-01T00:00:01', [geo.stockholms_lan], 289),
    ('2000-01-01T00:00:01', [geo.stockholms_lan, geo.solna], 289),
    ('2000-01-01T00:00:01', [geo.stockholms_lan, geo.stockholm, geo.botkyrka], 289),
    ('2000-01-01T00:00:01', [geo.stockholms_lan, geo.stockholm, geo.botkyrka, geo.solna, geo.nacka], 289)])
def test_filter_with_date_and_multiple_locations_in_same_region(session, url, date, geo_list, expected):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, LOCATION_CONCEPT_ID: geo_list}
    get_stream_check_number_of_results(session, url, expected, params)


@pytest.mark.parametrize('date, work_list, expected', [
    ('2000-01-01T00:00:01', [field.halso__och_sjukvard], 194),
    ('2000-01-01T00:00:01', [field.halso__och_sjukvard, work.sjukskoterska__grundutbildad], 194),
    ('2000-01-01T00:00:01', [field.halso__och_sjukvard, group.grundutbildade_sjukskoterskor], 194),
    ('2000-01-01T00:00:01',
     [field.halso__och_sjukvard, group.grundutbildade_sjukskoterskor, group.ambulanssjukskoterskor_m_fl_,
      work.sjukskoterska__medicin_och_kirurgi], 194)])
def test_filter_with_date_and_multiple_occupations_within_same_field(session, url, date, work_list, expected):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work_list}
    get_stream_check_number_of_results(session, url, expected, params)


@pytest.mark.parametrize('date, work_list, expected', [
    ('2000-01-01T00:00:01', [field.halso__och_sjukvard], 194),
    ('2000-01-01T00:00:01', [group.grundutbildade_sjukskoterskor], 68),
    ('2000-01-01T00:00:01', [work.sjukskoterska__grundutbildad], 66)
])
def test_filter_narrowing_down_occupations_within_same_field(session, url, date, work_list, expected):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work_list}
    get_stream_check_number_of_results(session, url, expected, params)


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
def test_filter_with_date_and_occupation_and_two_locations(session, url, date, work, geo_1, geo_2, expected):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work, LOCATION_CONCEPT_ID: [geo_1, geo_2]}
    get_stream_check_number_of_results(session, url, expected, params)


@pytest.mark.parametrize('work, expected', [
    (group.mjukvaru__och_systemutvecklare_m_fl_, 57),
    (group.mjukvaru__och_systemutvecklare_m_fl_.lower(), 0)])
def test_filter_with_lowercase_concept_id(session, url, work, expected):
    """
    compare correct concept_id with a lower case version
    """
    params = {'date': '2000-01-01T00:00:01', OCCUPATION_CONCEPT_ID: work}
    get_stream_check_number_of_results(session, url, expected, params)


@pytest.mark.parametrize('type, value', [
    (OCCUPATION_CONCEPT_ID, work.bartender),
    (LOCATION_CONCEPT_ID, geo.stockholm)])
def test_filter_without_date(session, url, type, value):
    """
    test that a 'bad request' (http 400 ) is returned when doing a request without date parameter
    """
    r = session.get(f"{url}/stream", params={type: value})
    assert r.status_code == requests.codes.bad_request


# test below for comparison of number of hits for different dates
@pytest.mark.parametrize('date, expected_number', [
    ('2000-01-01T00:00:01', 1065),
    ('2020-01-01T00:00:01', 1032),
    ('2020-02-01T00:00:01', 971),
    ('2020-02-25T07:29:41', 872),
    ('2020-03-14T07:29:41', 556),
    ('2020-03-25T07:29:41', 273),
    ('2020-03-27T07:29:41', 186),
    ('2020-03-31T07:29:41', 74),
    ('2020-04-25T07:29:41', 0)])
def test_filter_only_on_date(session, url, date, expected_number):
    """
    Test basic stream with filtering on date
    """
    get_stream_check_number_of_results(session, url, expected_number, params={'date': date})
