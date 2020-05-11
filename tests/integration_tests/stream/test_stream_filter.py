import pytest
import requests
from sokannonser.settings import OCCUPATION_CONCEPT_ID, LOCATION_CONCEPT_ID, NUMBER_OF_ADS, UPDATED_BEFORE_DATE, \
    DAWN_OF_TIME, current_time_stamp

import tests.integration_tests.test_resources.concept_ids.concept_ids_geo as geo
import tests.integration_tests.test_resources.concept_ids.occupation as work
import tests.integration_tests.test_resources.concept_ids.occupation_group as group
import tests.integration_tests.test_resources.concept_ids.occupation_field as field
from tests.integration_tests.test_resources.helper import get_stream_check_number_of_results, get_stream_expect_error


@pytest.mark.parametrize('date, work, expected_number_of_hits', [
    (DAWN_OF_TIME, group.arbetsformedlare, 5),
    (DAWN_OF_TIME, group.apotekare, 2),
    (DAWN_OF_TIME, group.mjukvaru__och_systemutvecklare_m_fl_, 57),
    (DAWN_OF_TIME, work.mjukvaruutvecklare, 12),
    (DAWN_OF_TIME, work.arbetsterapeut, 5)])
def test_filter_only_on_occupation(session, url, date, work, expected_number_of_hits):
    """
    Returns number of hits in the db. Temporary to verify results in other tests
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('date, geo, expected_number_of_hits', [
    (DAWN_OF_TIME, geo.aland_tillhor_finland, 1),
    (DAWN_OF_TIME, geo.norge, 3),
    (DAWN_OF_TIME, geo.malta, 1),
    (DAWN_OF_TIME, geo.schweiz, 1),
    (DAWN_OF_TIME, geo.kalmar_lan, 17),
    (DAWN_OF_TIME, geo.botkyrka, 5),
    (DAWN_OF_TIME, geo.stockholms_lan, 289),
    (DAWN_OF_TIME, geo.stockholm, 194),
    (DAWN_OF_TIME, geo.sverige, 1066)])
def test_filter_only_on_location(session, url, date, geo, expected_number_of_hits):
    """
    Returns number of hits in the db. Temporary to verify results in other tests
    """
    params = {'date': date, LOCATION_CONCEPT_ID: geo}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('date, work, geo, expected_number_of_hits', [
    (DAWN_OF_TIME, work.arbetsterapeut, geo.mellerud, 1),
    ('2020-04-01T00:00:01', work.arbetsterapeut, geo.mellerud, 0),
    ('2020-02-01T00:00:01', work.barista_kaffebartender, geo.sverige, 1),
    ('2020-02-01T00:00:01', work.bussforare_busschauffor, geo.norge, 1),
    ('2020-03-01T00:00:01', work.larare_i_grundskolan__arskurs_7_9, geo.goteborg, 1),
    (DAWN_OF_TIME, group.apotekare, geo.sverige, 2),
    (DAWN_OF_TIME, group.mjukvaru__och_systemutvecklare_m_fl_, geo.sverige, 56),
    (DAWN_OF_TIME, group.mjukvaru__och_systemutvecklare_m_fl_, geo.schweiz, 1),
    ('2020-01-01T00:00:01', group.mjukvaru__och_systemutvecklare_m_fl_, geo.sverige, 51),
    ('2020-02-01T00:00:01', field.militart_arbete, geo.schweiz, 0),
    (DAWN_OF_TIME, field.militart_arbete, geo.sverige, 1),
    (DAWN_OF_TIME, field.halso__och_sjukvard, geo.sverige, 196),
    (DAWN_OF_TIME, field.halso__och_sjukvard, geo.stockholms_lan, 43),
    ('2020-02-25T00:00:01', field.halso__och_sjukvard, geo.sverige, 160),
    ('2020-02-25T00:00:01', field.halso__och_sjukvard, geo.stockholms_lan, 35),
])
def test_filter_with_date_and_occupation_and_location(session, url, date, work, geo, expected_number_of_hits):
    """
    should return results based on date AND occupation type AND location
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work, LOCATION_CONCEPT_ID: geo}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('date, concept_id, expected_number_of_hits', [
    (DAWN_OF_TIME, work.personlig_assistent, 54),
    (DAWN_OF_TIME, work.personlig_assistent, 54),
    ('2020-02-01T00:00:01', work.personlig_assistent, 51),
    ('2020-03-01T00:00:01', work.personlig_assistent, 46),
    ('2020-03-15T00:00:01', work.personlig_assistent, 33),
    ('2020-04-01T00:00:01', work.personlig_assistent, 0),
    (DAWN_OF_TIME, work.apotekschef, 2),
    ('2020-02-01T00:00:01', work.apotekschef, 2),
    (DAWN_OF_TIME, work.mjukvaruutvecklare, 12),
    ('2020-02-25T07:29:41', work.mjukvaruutvecklare, 10),
    ('2020-03-25T07:29:41', work.mjukvaruutvecklare, 2),
    ('2020-04-25T07:29:41', work.mjukvaruutvecklare, 0),
    (DAWN_OF_TIME, group.arbetsformedlare, 5),
    ('2020-03-25T07:29:41', group.arbetsformedlare, 2),
    (DAWN_OF_TIME, field.militart_arbete, 1),
    (DAWN_OF_TIME, field.socialt_arbete, 95),
    (DAWN_OF_TIME, work.administrativ_chef, 1),
    (DAWN_OF_TIME, work.account_manager, 3),
    (DAWN_OF_TIME, work.cykelbud, 1),
])
def test_filter_with_date_and_one_occupation(session, url, date, concept_id, expected_number_of_hits):
    """
    test of filtering in /stream: should return results based on date AND occupation-related concept_id
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: concept_id}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('date, geo, expected_number_of_hits', [
    (DAWN_OF_TIME, geo.falun, 8),
    (DAWN_OF_TIME, geo.stockholms_lan, 289),
    ('2020-02-01T00:00:01', geo.stockholms_lan, 266),
    ('2020-03-01T00:00:01', geo.stockholms_lan, 217),
    (DAWN_OF_TIME, geo.norge, 3),
    ('2020-01-01T00:00:01', geo.hallands_lan, 29),
    ('2020-01-01T00:00:01', geo.linkoping, 24),
    (DAWN_OF_TIME, geo.sverige, 1066),
    ('2020-01-01T00:00:01', geo.sverige, 1033),
    ('2020-02-15T00:00:01', geo.sverige, 920),
    ('2020-02-01T00:00:01', geo.stockholm, 172),
    ('2020-02-01T00:00:01', geo.schweiz, 1),
    ('2020-02-01T00:00:01', geo.norge, 3),
    ('2020-01-01T00:00:01', geo.dalarnas_lan, 20),
    ('2020-02-01T00:00:01', geo.norge, 3)])
def test_filter_with_date_and_location(session, url, date, geo, expected_number_of_hits):
    """
    should return results based on date AND occupation type AND location_1
    """
    params = {'date': date, LOCATION_CONCEPT_ID: geo}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


#   multiple params of same type

@pytest.mark.parametrize('date, work_1, work_2, expected_number_of_hits', [
    (DAWN_OF_TIME, work.account_manager, work.cykelbud, 4),
    (DAWN_OF_TIME, work.mjukvaruutvecklare, group.arbetsformedlare, 17),
    (DAWN_OF_TIME, work.account_manager, work.cykelbud, 4),
    (DAWN_OF_TIME, work.mjukvaruutvecklare, group.arbetsformedlare, 17),
    ('2020-01-01T00:00:01', work.mjukvaruutvecklare, group.arbetsformedlare, 16),
    (DAWN_OF_TIME, work.administrativ_chef, field.militart_arbete, 2),
    (DAWN_OF_TIME, field.militart_arbete, work.administrativ_chef, 2),
    ('2020-01-01T00:00:01', group.bagare_och_konditorer, group.bartendrar, 5),
    (DAWN_OF_TIME, work.administrativ_chef, field.militart_arbete, 2),
    (DAWN_OF_TIME, field.militart_arbete, work.administrativ_chef, 2),
    (DAWN_OF_TIME, group.bagare_och_konditorer, group.bartendrar, 5),
    ('2020-02-01T00:00:01', group.apotekare, field.data_it, 77),
    ('2020-02-25T07:29:41', group.frisorer, work.akupunktor, 3),
    ('2020-03-25T07:29:41', field.pedagogiskt_arbete, field.halso__och_sjukvard, 97),
    ('2020-02-25T07:29:41', field.hantverksyrken, group.hudterapeuter, 3),
    ('2020-01-25T07:29:41', field.socialt_arbete, work.databasutvecklare, 88)])
def test_filter_with_date_and_two_occupations(session, url, date, work_1, work_2, expected_number_of_hits):
    """
    test of filtering in /stream with date and 2 occupation-related concept_ids
    should return results based on both date AND (work_1 OR work_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2]}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('date, work_1, work_2, work_3, expected_number_of_hits', [
    (DAWN_OF_TIME, work.account_manager, work.cykelbud, work.databasutvecklare, 5),
    ('2020-01-01T00:00:01', work.mjukvaruutvecklare, work.databasutvecklare, group.arbetsformedlare, 17),
    ('2020-02-01T00:00:01', work.administrativ_chef, work.apotekschef, field.militart_arbete, 4),
    ('2020-01-01T00:00:01', group.bagare_och_konditorer, group.bartendrar, group.hovmastare_och_servitorer, 11),
    ('2020-02-01T00:00:01', group.apotekare, group.ambulanssjukskoterskor_m_fl_, field.data_it, 78),
    ('2020-02-25T07:29:41', group.frisorer, group.hudterapeuter, work.akupunktor, 3),
    (DAWN_OF_TIME, field.pedagogiskt_arbete, field.halso__och_sjukvard, field.kropps__och_skonhetsvard, 336),
    ('2020-03-25T07:29:41', field.pedagogiskt_arbete, field.halso__och_sjukvard, field.kropps__och_skonhetsvard, 97),
    (DAWN_OF_TIME, field.hantverksyrken, field.data_it, group.hudterapeuter, 92),
    ('2020-03-25T07:29:41', field.hantverksyrken, field.data_it, group.hudterapeuter, 17),
    (DAWN_OF_TIME, field.socialt_arbete, field.bygg_och_anlaggning, work.databasutvecklare, 136),
    ('2020-02-25T07:29:41', field.socialt_arbete, field.bygg_och_anlaggning, work.databasutvecklare, 112)
])
def test_filter_with_date_and_three_occupations(session, url, date, work_1, work_2, work_3, expected_number_of_hits):
    """
    test of filtering in /stream with date and 2 occupation-related concept_ids
    should return results based on date AND (work_1 OR work_2 OR work 3)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2, work_3]}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params=params)


@pytest.mark.smoke
@pytest.mark.parametrize('date, work_1, work_2, geo_1, expected_number_of_hits', [
    (DAWN_OF_TIME, work.arbetsterapeut, work.bussforare_busschauffor, geo.sverige, 6),
    (DAWN_OF_TIME, work.arbetsterapeut, group.apotekare, geo.stockholms_lan, 1),
    (DAWN_OF_TIME, work.arbetsterapeut, field.kropps__och_skonhetsvard, geo.norge, 0),
    (DAWN_OF_TIME, group.apotekare, group.apotekare, geo.sverige, 2),
    (DAWN_OF_TIME, group.apotekare, group.hovmastare_och_servitorer, geo.stockholms_lan, 3),
    (DAWN_OF_TIME, group.apotekare, group.arbetsformedlare, geo.sverige, 7),
    ('2020-02-01T00:00:01', field.militart_arbete, field.hantverksyrken, geo.stockholm, 1),
    ('2020-02-01T00:00:01', field.militart_arbete, group.ambulanssjukskoterskor_m_fl_, geo.jonkopings_lan, 0),
    ('2020-02-01T00:00:01', field.militart_arbete, work.bussforare_busschauffor, geo.norge, 1),
    (DAWN_OF_TIME, group.mjukvaru__och_systemutvecklare_m_fl_, geo.dalarnas_lan, geo.schweiz, 1),
    ('2020-02-01T00:00:01', work.bussforare_busschauffor, geo.schweiz, geo.norge, 1)])
def test_filter_with_date_and_two_occupations_and_location(session, url, date, work_1, work_2, geo_1,
                                                           expected_number_of_hits):
    """
    should return results based on date AND location AND (work_1 OR work_2)
    results = work_1 + work_2 that matches location
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2], LOCATION_CONCEPT_ID: geo_1}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('date, geo_1, geo_2, expected_number_of_hits', [
    (DAWN_OF_TIME, geo.arboga, geo.falun, 9),
    (DAWN_OF_TIME, geo.arboga, geo.stockholms_lan, 290),
    (DAWN_OF_TIME, geo.arboga, geo.norge, 4),
    ('2020-01-01T00:00:01', geo.dalarnas_lan, geo.hallands_lan, 49),
    ('2020-01-01T00:00:01', geo.dalarnas_lan, geo.linkoping, 44),
    ('2020-01-01T00:00:01', geo.dalarnas_lan, geo.sverige, 1033),
    ('2020-02-01T00:00:01', geo.schweiz, geo.stockholm, 173),
    ('2020-02-01T00:00:01', geo.schweiz, geo.jonkopings_lan, 51),
    ('2020-02-01T00:00:01', geo.schweiz, geo.norge, 4),
    ('2020-01-01T00:00:01', geo.dalarnas_lan, geo.schweiz, 21),
    ('2020-02-01T00:00:01', geo.schweiz, geo.norge, 4)])
def test_filter_with_date_and_two_locations(session, url, date, geo_1, geo_2, expected_number_of_hits):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, LOCATION_CONCEPT_ID: [geo_1, geo_2]}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('date, geo_list, expected_number_of_hits', [
    (DAWN_OF_TIME, [geo.stockholms_lan], 289),
    (DAWN_OF_TIME, [geo.stockholms_lan, geo.solna], 289),
    (DAWN_OF_TIME, [geo.stockholms_lan, geo.stockholm, geo.botkyrka], 289),
    (DAWN_OF_TIME, [geo.stockholms_lan, geo.stockholm, geo.botkyrka, geo.solna, geo.nacka], 289)])
def test_filter_with_date_and_multiple_locations_in_same_region(session, url, date, geo_list, expected_number_of_hits):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, LOCATION_CONCEPT_ID: geo_list}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('date, work_list, expected_number_of_hits', [
    (DAWN_OF_TIME, [field.halso__och_sjukvard], 196),
    (DAWN_OF_TIME, [field.halso__och_sjukvard, work.sjukskoterska__grundutbildad], 196),
    (DAWN_OF_TIME, [field.halso__och_sjukvard, group.grundutbildade_sjukskoterskor], 196),
    (DAWN_OF_TIME,
     [field.halso__och_sjukvard, group.grundutbildade_sjukskoterskor, group.ambulanssjukskoterskor_m_fl_,
      work.sjukskoterska__medicin_och_kirurgi], 196)])
def test_filter_with_date_and_multiple_occupations_within_same_field(session, url, date, work_list,
                                                                     expected_number_of_hits):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work_list}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('date, work_list, expected_number_of_hits', [
    (DAWN_OF_TIME, [field.halso__och_sjukvard], 196),
    (DAWN_OF_TIME, [group.grundutbildade_sjukskoterskor], 70),
    (DAWN_OF_TIME, [work.sjukskoterska__grundutbildad], 68)
])
def test_filter_narrowing_down_occupations_within_same_field(session, url, date, work_list, expected_number_of_hits):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work_list}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('date, work, geo_1, geo_2, expected_number_of_hits', [
    (DAWN_OF_TIME, work.arbetsterapeut, geo.arboga, geo.falun, 0),
    (DAWN_OF_TIME, work.arbetsterapeut, geo.arboga, geo.stockholms_lan, 1),
    (DAWN_OF_TIME, group.apotekare, geo.dalarnas_lan, geo.hallands_lan, 0),
    (DAWN_OF_TIME, group.apotekare, geo.dalarnas_lan, geo.linkoping, 0),
    (DAWN_OF_TIME, group.apotekare, geo.malta, geo.sverige, 2),
    ('2020-02-01T00:00:01', field.kultur__media__design, geo.schweiz, geo.stockholm, 1),
    ('2020-02-01T00:00:01', field.naturvetenskapligt_arbete, geo.schweiz, geo.stockholms_lan, 1),
    ('2020-02-01T00:00:01', field.bygg_och_anlaggning, geo.schweiz, geo.norge, 0),
    (DAWN_OF_TIME, group.mjukvaru__och_systemutvecklare_m_fl_, geo.dalarnas_lan, geo.schweiz, 1),
    ('2020-02-01T00:00:01', work.bussforare_busschauffor, geo.schweiz, geo.norge, 1)])
def test_filter_with_date_and_occupation_and_two_locations(session, url, date, work, geo_1, geo_2,
                                                           expected_number_of_hits):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work, LOCATION_CONCEPT_ID: [geo_1, geo_2]}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('date, work_1, work_2, geo_1, geo_2, expected_number_of_hits', [
    (DAWN_OF_TIME, work.databasutvecklare, work.arbetsterapeut, geo.arboga, geo.falun, 0),
    (DAWN_OF_TIME, work.databasutvecklare, work.sjukskoterska__grundutbildad, geo.arboga, geo.falun, 2),
    (DAWN_OF_TIME, group.mjukvaru__och_systemutvecklare_m_fl_, work.arbetsterapeut, geo.arboga, geo.stockholms_lan, 24),
    (DAWN_OF_TIME, work.farmaceut_apotekare, group.apotekare, geo.dalarnas_lan, geo.hallands_lan, 0),
    (DAWN_OF_TIME, work.sjukskoterska__grundutbildad, group.apotekare, geo.dalarnas_lan, geo.linkoping, 4),
    (DAWN_OF_TIME, work.barnsjukskoterska, group.apotekare, geo.malta, geo.sverige, 5),
    ('2020-02-01T00:00:01', work.eltekniker, field.kultur__media__design, geo.schweiz, geo.stockholm, 2),
    ('2020-02-01T00:00:01', work.butikssaljare__fackhandel, field.naturvetenskapligt_arbete, geo.schweiz,
     geo.stockholms_lan, 4),
    ('2020-02-01T00:00:01', group.gymnasielarare, field.bygg_och_anlaggning, geo.schweiz, geo.norge, 0),
    ('2020-02-01T00:00:01', group.grundutbildade_sjukskoterskor, field.bygg_och_anlaggning, geo.schweiz, geo.norge, 0),
    ('2020-02-01T00:00:01', group.grundutbildade_sjukskoterskor, field.halso__och_sjukvard, geo.schweiz, geo.norge, 0),
    (DAWN_OF_TIME, work.bygg__och_anlaggningsforare, group.mjukvaru__och_systemutvecklare_m_fl_, geo.dalarnas_lan,
     geo.schweiz, 1),
    ('2020-02-01T00:00:01', field.halso__och_sjukvard, work.bussforare_busschauffor, geo.schweiz, geo.norge, 1)])
def test_filter_with_date_and_two_occupations_and_two_locations(session, url, date, work_1, work_2, geo_1, geo_2,
                                                                expected_number_of_hits):
    """
    should return results based on date AND (occupation 1 OR occupation 2) AND (location_1 OR location_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2], LOCATION_CONCEPT_ID: [geo_1, geo_2]}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('work, expected_number_of_hits', [
    (group.mjukvaru__och_systemutvecklare_m_fl_, 57),
    (group.mjukvaru__och_systemutvecklare_m_fl_.lower(), 0)])
def test_filter_with_lowercase_concept_id(session, url, work, expected_number_of_hits):
    """
    compare correct concept_id with a lower case version
    """
    params = {'date': DAWN_OF_TIME, OCCUPATION_CONCEPT_ID: work}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)


@pytest.mark.parametrize('type, value', [
    (OCCUPATION_CONCEPT_ID, work.bartender),
    (LOCATION_CONCEPT_ID, geo.stockholm)])
def test_filter_without_date_expect_bad_request_response(session, url, type, value):
    """
    test that a 'bad request' response (http 400) is returned when doing a request without date parameter
    """
    get_stream_expect_error(session, url, path='/stream', params={type: value},
                            expected_http_code=requests.codes.bad_request)


@pytest.mark.parametrize('path', ['/stream', '/snapshot'])
def test_filter_wrong_api_key_expect_unauthorized_response(session, url, path):
    """
    test that a 'unauthorized' response (http 401) is returned when doing a request with an incorrect api key
    """
    session.headers.update({'api-key': 'wrong key'})
    params = {LOCATION_CONCEPT_ID: geo.stockholm}
    expected_http_code = requests.codes.unauthorized
    get_stream_expect_error(session, url, path, params, expected_http_code)


# test below for comparison of number of hits for different dates
@pytest.mark.parametrize('date, expected_number_of_hits', [
    (DAWN_OF_TIME, NUMBER_OF_ADS),
    ('2020-01-01T00:00:01', 1039),
    ('2020-02-01T00:00:01', 978),
    ('2020-02-25T07:29:41', 879),
    ('2020-03-14T07:29:41', 563),
    ('2020-03-25T07:29:41', 280),
    ('2020-03-27T07:29:41', 193),
    ('2020-03-31T07:29:41', 81),
    ('2020-04-25T07:29:41', 2),
    ('2020-04-27T08:29:41', 0),
])
def test_filter_only_on_date(session, url, date, expected_number_of_hits):
    """
    Test basic stream with filtering on date (update after this date)
    """
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params={'date': date})


@pytest.mark.parametrize('from_date, to_date, expected_number_of_hits', [
    # 1 verify that results are the same as when only using a single date
    (DAWN_OF_TIME, '2020-04-30T00:00:00', NUMBER_OF_ADS),
    ('2020-01-01T00:00:01', '2020-04-30T00:00:00', 1039),
    ('2020-02-01T00:00:01', '2020-04-30T00:00:00', 978),
    ('2020-02-25T07:29:41', '2020-04-30T00:00:00', 879),
    ('2020-03-14T07:29:41', '2020-04-30T00:00:00', 563),
    ('2020-03-25T07:29:41', '2020-04-30T00:00:00', 280),
    ('2020-03-27T07:29:41', '2020-04-30T00:00:00', 193),
    ('2020-03-31T07:29:41', '2020-04-30T00:00:00', 81),
    ('2020-04-25T07:29:41', '2020-04-30T00:00:00', 2),
    ('2020-04-27T07:29:41', '2020-04-30T00:00:00', 1),
    ('2020-04-27T08:29:41', '2020-04-30T00:00:00', 0),
    ('2020-02-25T07:29:41', '2020-03-25T00:00:00', 598),
    ('2020-03-14T07:29:41', '2020-03-30T00:00:00', 426),
    ('2020-03-14T07:29:41', '2020-03-16T00:00:00', 4),
    ('2020-03-14T07:29:41', '2020-03-20T00:00:00', 143),
    ('2020-03-25T07:29:41', '2020-03-30T00:00:00', 143),
    ('2020-03-26T07:29:41', '2020-03-30T00:00:00', 100),
    ('2020-03-27T07:29:41', '2020-03-30T00:00:00', 56),
    ('2020-03-31T07:29:41', '2020-04-02T00:00:00', 74),
    ('2020-04-25T07:29:41', '2020-04-30T00:00:00', 2),
    ('2020-04-25T07:29:41', '2020-04-25T10:00:00', 0),
    (DAWN_OF_TIME, '2020-04-30T10:00:00', NUMBER_OF_ADS),
    (DAWN_OF_TIME, current_time_stamp, NUMBER_OF_ADS),
    # reverse order should return 0 results without errors
    (current_time_stamp, DAWN_OF_TIME, 0)
])
def test_filter_on_date_interval(session, url, from_date, to_date, expected_number_of_hits):
    """
    Test stream with filtering on date interval. 
    """
    params = {'date': from_date, UPDATED_BEFORE_DATE: to_date}
    get_stream_check_number_of_results(session, url, expected_number_of_hits, params)
