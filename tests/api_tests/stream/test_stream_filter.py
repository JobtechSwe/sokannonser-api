import pytest

from sokannonser.settings import OCCUPATION_CONCEPT_ID, LOCATION_CONCEPT_ID, UPDATED_BEFORE_DATE
from tests.test_resources.settings import NUMBER_OF_ADS, DAWN_OF_TIME, current_time_stamp

import tests.test_resources.concept_ids.concept_ids_geo as geo
import tests.test_resources.concept_ids.occupation as work
import tests.test_resources.concept_ids.occupation_group as group
import tests.test_resources.concept_ids.occupation_field as field
from tests.test_resources.helper import get_stream_check_number_of_results


@pytest.mark.parametrize('date, work, expected_number_of_hits', [
    (DAWN_OF_TIME, group.arbetsformedlare, 7),
    (DAWN_OF_TIME, group.apotekare, 0),
    (DAWN_OF_TIME, group.mjukvaru__och_systemutvecklare_m_fl_, 88),
    (DAWN_OF_TIME, work.mjukvaruutvecklare, 20),
    (DAWN_OF_TIME, work.arbetsterapeut, 3)])
def test_filter_only_on_occupation(session_stream, date, work, expected_number_of_hits):
    """
    Returns number of hits in the db. Temporary to verify results in other tests
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


@pytest.mark.parametrize('date, geo, expected_number_of_hits', [
    (DAWN_OF_TIME, geo.aland_tillhor_finland, 0),
    (DAWN_OF_TIME, geo.norge, 4),
    (DAWN_OF_TIME, geo.malta, 0),
    (DAWN_OF_TIME, geo.schweiz, 1),
    (DAWN_OF_TIME, geo.kalmar_lan, 38),
    (DAWN_OF_TIME, geo.botkyrka, 6),
    (DAWN_OF_TIME, geo.stockholms_lan, 410),
    (DAWN_OF_TIME, geo.stockholm, 285),
    (DAWN_OF_TIME, geo.sverige, 1485)])
def test_filter_only_on_location(session_stream, date, geo, expected_number_of_hits):
    """
    Returns number of hits in the db. Temporary to verify results in other tests
    """
    params = {'date': date, LOCATION_CONCEPT_ID: geo}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


@pytest.mark.parametrize('date, work, geo, expected_number_of_hits', [
    (DAWN_OF_TIME, work.larare_i_fritidshem_fritidspedagog, geo.vastra_gotalands_lan, 2),
    ('2020-12-15T00:00:01', work.larare_i_fritidshem_fritidspedagog, geo.vastra_gotalands_lan, 1),
    ('2020-12-01T00:00:01', work.servitor_servitris__kafe_och_konditori, geo.sverige, 0),
    ('2020-12-01T00:00:01', work.bussforare_busschauffor, geo.sverige, 2),
    ('2020-12-01T00:00:01', work.larare_i_grundskolan__arskurs_7_9, geo.stockholms_lan, 3),
    (DAWN_OF_TIME, group.grundutbildade_sjukskoterskor, geo.sverige, 104),
    (DAWN_OF_TIME, group.mjukvaru__och_systemutvecklare_m_fl_, geo.sverige, 88),
    (DAWN_OF_TIME, group.mjukvaru__och_systemutvecklare_m_fl_, geo.schweiz, 0),
    ('2020-11-01T00:00:01', group.mjukvaru__och_systemutvecklare_m_fl_, geo.sverige, 81),
    ('2020-12-01T00:00:01', field.militart_arbete, geo.schweiz, 0),
    (DAWN_OF_TIME, field.militart_arbete, geo.sverige, 6),
    (DAWN_OF_TIME, field.halso__och_sjukvard, geo.sverige, 269),
    (DAWN_OF_TIME, field.halso__och_sjukvard, geo.stockholms_lan, 55),
    ('2020-11-25T00:00:01', field.halso__och_sjukvard, geo.sverige, 220),
    ('2020-12-15T00:00:01', field.halso__och_sjukvard, geo.stockholms_lan, 18),
])
def test_filter_with_date_and_occupation_and_location(session_stream, date, work, geo,
                                                      expected_number_of_hits):
    """
    should return results based on date AND occupation type AND location
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work, LOCATION_CONCEPT_ID: geo}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


@pytest.mark.parametrize('date, concept_id, expected_number_of_hits', [
    (DAWN_OF_TIME, work.personlig_assistent, 48),
    ('2020-11-01T00:00:01', work.personlig_assistent, 42),
    ('2020-12-01T00:00:01', work.personlig_assistent, 30),
    ('2020-12-15T00:00:01', work.personlig_assistent, 9),
    ('2021-01-01T00:00:01', work.personlig_assistent, 0),
    (DAWN_OF_TIME, work.kassapersonal, 3),
    ('2020-12-01T00:00:01', work.kassapersonal, 2),
    (DAWN_OF_TIME, work.mjukvaruutvecklare, 20),
    ('2020-10-25T00:00:00', work.mjukvaruutvecklare, 18),
    ('2020-11-25T00:00:00', work.mjukvaruutvecklare, 14),
    ('2020-12-15T00:00:00', work.mjukvaruutvecklare, 6),
    (DAWN_OF_TIME, group.arbetsformedlare, 7),
    ('2020-03-25T00:00:00', group.arbetsformedlare, 7),
    (DAWN_OF_TIME, field.militart_arbete, 6),
    (DAWN_OF_TIME, field.socialt_arbete, 111),
    (DAWN_OF_TIME, work.administrativ_chef, 4),
    (DAWN_OF_TIME, work.account_manager, 13),
    (DAWN_OF_TIME, work.cykelbud, 1),
])
def test_filter_with_date_and_one_occupation(session_stream, date, concept_id, expected_number_of_hits):
    """
    test of filtering in /stream: should return results based on date AND occupation-related concept_id
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: concept_id}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


@pytest.mark.parametrize('date, geo, expected_number_of_hits', [
    (DAWN_OF_TIME, geo.falun, 9),
    (DAWN_OF_TIME, geo.stockholms_lan, 410),
    ('2020-12-01T00:00:01', geo.stockholms_lan, 297),
    ('2020-12-05T00:00:01', geo.stockholms_lan, 263),
    (DAWN_OF_TIME, geo.norge, 4),
    ('2020-11-01T00:00:01', geo.hallands_lan, 36),
    ('2020-11-01T00:00:01', geo.linkoping, 31),
    (DAWN_OF_TIME, geo.sverige, 1485),
    ('2020-11-01T00:00:01', geo.sverige, 1387),
    ('2020-12-15T00:00:01', geo.sverige, 551),
    ('2020-12-01T00:00:01', geo.stockholm, 202),
    ('2020-12-01T00:00:01', geo.schweiz, 1),
    ('2020-12-01T00:00:01', geo.norge, 4),
    ('2020-11-01T00:00:01', geo.dalarnas_lan, 30),
    ('2020-12-01T00:00:01', geo.dalarnas_lan, 26),
    ('2020-12-15T00:00:01', geo.dalarnas_lan, 12)])
def test_filter_with_date_and_location(session_stream, date, geo, expected_number_of_hits):
    """
    should return results based on date AND occupation type AND location_1
    """
    params = {'date': date, LOCATION_CONCEPT_ID: geo}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


#   multiple params of same type

@pytest.mark.parametrize('date, work_1, work_2, expected_number_of_hits', [
    (DAWN_OF_TIME, work.account_manager, work.cykelbud, 14),
    (DAWN_OF_TIME, work.mjukvaruutvecklare, group.arbetsformedlare, 27),
    (DAWN_OF_TIME, work.cykelbud, work.account_manager, 14),
    ('2020-11-01T00:00:01', work.mjukvaruutvecklare, group.arbetsformedlare, 25),
    ('2020-12-01T00:00:01', work.mjukvaruutvecklare, group.arbetsformedlare, 17),
    (DAWN_OF_TIME, work.administrativ_chef, field.militart_arbete, 10),
    (DAWN_OF_TIME, field.militart_arbete, work.administrativ_chef, 10),
    ('2020-11-01T00:00:01', group.bagare_och_konditorer, group.bartendrar, 2),
    (DAWN_OF_TIME, group.bagare_och_konditorer, group.bartendrar, 3),
    ('2020-11-11T00:00:01', group.apotekare, field.data_it, 129),
    ('2020-12-12T00:00:01', group.apotekare, field.data_it, 66),
    ('2020-11-25T00:00:00', group.frisorer, work.akupunktor, 2),
    ('2020-11-25T00:00:00', field.pedagogiskt_arbete, field.halso__och_sjukvard, 338),
    ('2020-12-15T00:00:00', field.hantverksyrken, group.hudterapeuter, 3),
    ('2020-11-25T00:00:00', field.socialt_arbete, work.databasutvecklare, 92)])
def test_filter_with_date_and_two_occupations(session_stream, date, work_1, work_2,
                                              expected_number_of_hits):
    """
    test of filtering in /stream with date and 2 occupation-related concept_ids
    should return results based on both date AND (work_1 OR work_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2]}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


@pytest.mark.parametrize('date, work_1, work_2, work_3, expected_number_of_hits', [
    (DAWN_OF_TIME, work.account_manager, work.cykelbud, work.databasutvecklare, 15),
    ('2020-11-01T00:00:01', work.mjukvaruutvecklare, work.databasutvecklare, group.arbetsformedlare, 26),
    ('2020-12-01T00:00:01', work.administrativ_chef, work.apotekschef, field.militart_arbete, 10),
    ('2020-11-01T00:00:01', group.bagare_och_konditorer, group.bartendrar, group.hovmastare_och_servitorer, 4),
    ('2020-12-01T00:00:01', group.apotekare, group.ambulanssjukskoterskor_m_fl_, field.data_it, 108),
    ('2020-11-25T00:00:00', group.frisorer, group.hudterapeuter, work.akupunktor, 2),
    (DAWN_OF_TIME, field.pedagogiskt_arbete, field.halso__och_sjukvard, field.kropps__och_skonhetsvard, 416),
    ('2020-11-25T00:00:00', field.pedagogiskt_arbete, field.halso__och_sjukvard, field.kropps__och_skonhetsvard, 342),
    (DAWN_OF_TIME, field.hantverksyrken, field.data_it, group.hudterapeuter, 162),
    ('2020-11-25T00:00:00', field.hantverksyrken, field.data_it, group.hudterapeuter, 122),
    (DAWN_OF_TIME, field.socialt_arbete, field.bygg_och_anlaggning, work.databasutvecklare, 184),
    ('2020-11-25T00:00:00', field.socialt_arbete, field.bygg_och_anlaggning, work.databasutvecklare, 153)
])
def test_filter_with_date_and_three_occupations(session_stream, date, work_1, work_2, work_3,
                                                expected_number_of_hits):
    """
    test of filtering in /stream with date and 2 occupation-related concept_ids
    should return results based on date AND (work_1 OR work_2 OR work 3)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2, work_3]}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params=params)


@pytest.mark.smoke
@pytest.mark.parametrize('date, work_1, work_2, geo_1, expected_number_of_hits', [
    (DAWN_OF_TIME, work.arbetsterapeut, work.bussforare_busschauffor, geo.sverige, 5),
    (DAWN_OF_TIME, work.arbetsterapeut, group.apotekare, geo.vastra_gotalands_lan, 0),
    (DAWN_OF_TIME, work.arbetsterapeut, field.kropps__och_skonhetsvard, geo.norge, 0),
    (DAWN_OF_TIME, work.arbetsterapeut, field.kropps__och_skonhetsvard, geo.sverige, 11),
    (DAWN_OF_TIME, group.grundutbildade_sjukskoterskor, group.grundutbildade_sjukskoterskor, geo.sverige, 104),
    (DAWN_OF_TIME, group.apotekare, group.hovmastare_och_servitorer, geo.stockholms_lan, 1),
    (DAWN_OF_TIME, group.apotekare, group.arbetsformedlare, geo.sverige, 7),
    ('2020-12-01T00:00:01', field.militart_arbete, field.hantverksyrken, geo.stockholm, 2),
    ('2020-12-01T00:00:01', field.militart_arbete, group.ambulanssjukskoterskor_m_fl_, geo.sverige, 8),
    ('2020-12-01T00:00:01', field.militart_arbete, work.bussforare_busschauffor, geo.norge, 0)])
def test_filter_with_date_and_two_occupations_and_location(session_stream, date, work_1, work_2, geo_1,
                                                           expected_number_of_hits):
    """
    should return results based on date AND location AND (work_1 OR work_2)
    results = work_1 + work_2 that matches location
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2], LOCATION_CONCEPT_ID: geo_1}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


@pytest.mark.parametrize('date, geo_1, geo_2, expected_number_of_hits', [
    (DAWN_OF_TIME, geo.arboga, geo.falun, 11),
    (DAWN_OF_TIME, geo.arboga, geo.stockholms_lan, 412),
    (DAWN_OF_TIME, geo.arboga, geo.norge, 6),
    ('2020-11-01T00:00:01', geo.dalarnas_lan, geo.hallands_lan, 66),
    ('2020-11-01T00:00:01', geo.dalarnas_lan, geo.linkoping, 61),
    ('2020-11-01T00:00:01', geo.dalarnas_lan, geo.sverige, 1387),
    ('2020-12-01T00:00:01', geo.schweiz, geo.stockholm, 203),
    ('2020-12-01T00:00:01', geo.schweiz, geo.jonkopings_lan, 39),
    ('2020-12-01T00:00:01', geo.schweiz, geo.norge, 5),
    ('2020-11-01T00:00:01', geo.dalarnas_lan, geo.schweiz, 31),
    ('2020-12-01T00:00:01', geo.schweiz, geo.norge, 5)])
def test_filter_with_date_and_two_locations(session_stream, date, geo_1, geo_2, expected_number_of_hits):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, LOCATION_CONCEPT_ID: [geo_1, geo_2]}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


@pytest.mark.parametrize('date, geo_list, expected_number_of_hits', [
    (DAWN_OF_TIME, [geo.stockholms_lan], 410),
    (DAWN_OF_TIME, [geo.stockholms_lan, geo.solna], 410),
    (DAWN_OF_TIME, [geo.stockholms_lan, geo.stockholm, geo.botkyrka], 410),
    (DAWN_OF_TIME, [geo.stockholms_lan, geo.stockholm, geo.botkyrka, geo.solna, geo.nacka], 410)])
def test_filter_with_date_and_multiple_locations_in_same_region(session_stream, date, geo_list,
                                                                expected_number_of_hits):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, LOCATION_CONCEPT_ID: geo_list}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


@pytest.mark.parametrize('date, work_list, expected_number_of_hits', [
    (DAWN_OF_TIME, [field.halso__och_sjukvard], 270),
    (DAWN_OF_TIME, [field.halso__och_sjukvard, work.sjukskoterska__grundutbildad], 270),
    (DAWN_OF_TIME, [field.halso__och_sjukvard, group.grundutbildade_sjukskoterskor], 270),
    (DAWN_OF_TIME,
     [field.halso__och_sjukvard, group.grundutbildade_sjukskoterskor, group.ambulanssjukskoterskor_m_fl_,
      work.sjukskoterska__medicin_och_kirurgi], 270)])
def test_filter_with_date_and_multiple_occupations_within_same_field(session_stream, date, work_list,
                                                                     expected_number_of_hits):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work_list}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


@pytest.mark.parametrize('date, work_list, expected_number_of_hits', [
    (DAWN_OF_TIME, [field.halso__och_sjukvard], 270),
    (DAWN_OF_TIME, [group.grundutbildade_sjukskoterskor], 105),
    (DAWN_OF_TIME, [work.sjukskoterska__grundutbildad], 103)
])
def test_filter_narrowing_down_occupations_within_same_field(session_stream, date, work_list,
                                                             expected_number_of_hits):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work_list}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


@pytest.mark.parametrize('date, work, geo_1, geo_2, expected_number_of_hits', [
    (DAWN_OF_TIME, work.arbetsterapeut, geo.arboga, geo.falun, 0),
    (DAWN_OF_TIME, work.arbetsterapeut, geo.vastra_gotalands_lan, geo.ostergotlands_lan, 0),
    (DAWN_OF_TIME, group.civilingenjorsyrken_inom_bygg_och_anlaggning, geo.dalarnas_lan, geo.hallands_lan, 0),
    (DAWN_OF_TIME, group.civilingenjorsyrken_inom_bygg_och_anlaggning, geo.dalarnas_lan, geo.linkoping, 0),
    (DAWN_OF_TIME, group.civilingenjorsyrken_inom_bygg_och_anlaggning, geo.malta, geo.sverige, 12),
    ('2020-12-01T00:00:01', field.kultur__media__design, geo.schweiz, geo.stockholm, 5),
    ('2020-12-01T00:00:01', field.naturvetenskapligt_arbete, geo.schweiz, geo.stockholms_lan, 4),
    ('2020-12-01T00:00:01', field.bygg_och_anlaggning, geo.schweiz, geo.norge, 1),
    (DAWN_OF_TIME, group.mjukvaru__och_systemutvecklare_m_fl_, geo.vastra_gotalands_lan, geo.schweiz, 16),
    ('2020-02-01T00:00:01', work.bussforare_busschauffor, geo.schweiz, geo.norge,0)])
def test_filter_with_date_and_occupation_and_two_locations(session_stream, date, work, geo_1, geo_2,
                                                           expected_number_of_hits):
    """
    should return results based on date AND occupation type AND (location_1 OR location_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: work, LOCATION_CONCEPT_ID: [geo_1, geo_2]}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


@pytest.mark.parametrize('date, work_1, work_2, geo_1, geo_2, expected_number_of_hits', [
    (DAWN_OF_TIME, work.databasutvecklare, work.arbetsterapeut, geo.goteborg, geo.falun, 0),
    (DAWN_OF_TIME, work.databasutvecklare, work.sjukskoterska__grundutbildad, geo.arboga, geo.falun, 4),
    (DAWN_OF_TIME, group.mjukvaru__och_systemutvecklare_m_fl_, work.arbetsterapeut, geo.arboga, geo.stockholms_lan, 37),
    (DAWN_OF_TIME, work.farmaceut_apotekare, group.kassapersonal_m_fl_, geo.dalarnas_lan, geo.hallands_lan, 0),
    (DAWN_OF_TIME, work.sjukskoterska__grundutbildad, group.apotekare, geo.dalarnas_lan, geo.linkoping,6),
    (DAWN_OF_TIME, work.barnsjukskoterska, group.apotekare, geo.malta, geo.sverige, 1),
    ('2020-12-01T00:00:01', work.eltekniker, field.kultur__media__design, geo.schweiz, geo.stockholm, 5),
    ('2020-12-01T00:00:01', work.butikssaljare__fackhandel, field.naturvetenskapligt_arbete, geo.schweiz,
     geo.stockholms_lan, 8),
    ('2020-12-01T00:00:01', group.gymnasielarare, field.bygg_och_anlaggning, geo.schweiz, geo.norge, 1),
    ('2020-12-01T00:00:01', group.grundutbildade_sjukskoterskor, field.bygg_och_anlaggning, geo.schweiz, geo.norge, 2),
    ('2020-12-01T00:00:01', group.grundutbildade_sjukskoterskor, field.halso__och_sjukvard, geo.schweiz, geo.norge, 1),
    (DAWN_OF_TIME, work.bygg__och_anlaggningsforare, group.mjukvaru__och_systemutvecklare_m_fl_, geo.dalarnas_lan,
     geo.schweiz, 0),
    ('2020-12-01T00:00:01', field.halso__och_sjukvard, work.bussforare_busschauffor, geo.schweiz, geo.norge, 1)])
def test_filter_with_date_and_two_occupations_and_two_locations(session_stream, date, work_1, work_2, geo_1,
                                                                geo_2,
                                                                expected_number_of_hits):
    """
    should return results based on date AND (occupation 1 OR occupation 2) AND (location_1 OR location_2)
    """
    params = {'date': date, OCCUPATION_CONCEPT_ID: [work_1, work_2], LOCATION_CONCEPT_ID: [geo_1, geo_2]}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)


# test below for comparison of number of hits for different dates
@pytest.mark.parametrize('date, expected_number_of_hits', [
    (DAWN_OF_TIME, NUMBER_OF_ADS),
    ('2020-10-01T00:00:01', 1439),
    ('2020-11-01T00:00:01', 1397),
    ('2020-11-25T00:00:00', 1249),
    ('2020-12-01T00:00:00', 1146),
    ('2020-12-05T00:00:00', 985),
    ('2020-12-10T00:00:00', 778),
    ('2020-12-15T00:00:00', 554),
    ('2020-12-20T00:00:00', 168),
    ('2020-12-21T00:00:00', 161),
    ('2020-12-22T00:00:00', 28),
    ('2020-12-22T12:00:00', 6),
    ('2020-12-22T12:30:40', 1),
    ('2020-12-23T00:00:00', 0),
])
def test_filter_only_on_date(session_stream, date, expected_number_of_hits):
    """
    Test basic stream with filtering on date (update after this date)
    """
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params={'date': date})


@pytest.mark.parametrize('from_date, to_date, expected_number_of_hits', [
    # 1 verify that results are the same as when only using a single date
    (DAWN_OF_TIME, current_time_stamp, NUMBER_OF_ADS),
    ('2020-10-01T00:00:01', '2021-04-30T00:00:00', 1439),
    ('2020-11-01T00:00:01', '2021-04-30T00:00:00', 1397),
    ('2020-11-15T00:00:00', '2021-04-30T00:00:00', 1339),
    ('2020-11-20T00:00:00', '2021-04-30T00:00:00', 1301),
    ('2020-11-30T00:00:00', '2021-04-30T00:00:00', 1171),
    ('2020-12-05T00:00:00', '2021-04-30T00:00:00', 985),
    ('2020-12-10T00:00:00', '2021-04-30T00:00:00', 778),
    ('2020-12-15T00:00:00', '2021-04-30T00:00:00', 554),
    ('2020-12-20T00:00:00', '2021-04-30T00:00:00', 168),
    ('2020-12-30T08:29:41', '2021-04-30T00:00:00', 0),
    ('2020-11-25T00:00:00', '2021-11-25T00:00:00', 1249),
    ('2020-12-14T00:00:00', '2021-03-30T00:00:00', 649),
    ('2020-12-14T00:00:00', '2020-12-16T00:00:00', 176),
    ('2020-11-14T00:00:00', '2020-11-20T00:00:00',39),
    ('2020-11-25T00:00:00', '2020-11-30T00:00:00', 78),
    ('2020-11-26T00:00:00', '2020-11-30T00:00:00', 52),
    ('2020-12-10T00:00:00', '2020-12-15T00:00:00', 224),
    ('2020-12-12T00:00:00', '2020-12-15T00:00:00', 103),
    ('2020-12-15T00:00:00', '2020-12-16T00:00:00', 81),
    ('2020-12-16T00:00:00', '2020-12-17T10:00:00', 101),
    ('2020-12-22T00:00:00', '2020-12-23T10:00:00', 28),
    (DAWN_OF_TIME, '2021-04-30T10:00:00', NUMBER_OF_ADS),
    (DAWN_OF_TIME, current_time_stamp, NUMBER_OF_ADS),
    # reverse order should return 0 results without errors
    (current_time_stamp, DAWN_OF_TIME, 0)
])
def test_filter_on_date_interval(session_stream, from_date, to_date, expected_number_of_hits):
    """
    Test stream with filtering on date interval. 
    """
    params = {'date': from_date, UPDATED_BEFORE_DATE: to_date}
    get_stream_check_number_of_results(session_stream, expected_number_of_hits, params)
