import sys
import os
import pytest
import requests
import json
from dateutil import parser
from sokannonser import settings as search_settings
from sokannonser.repository import taxonomy
from sokannonser.rest.model import fields
from tests.test_resources.settings import NUMBER_OF_ADS, TEST_USE_STATIC_DATA
from tests.test_resources.helper import get_search, compare, _fetch_and_validate_result, check_value_more_than
from tests.test_resources.concept_ids import occupation as work, occupation_field as field, \
    occupation_group as group


@pytest.mark.smoke
@pytest.mark.integration
def test_freetext_query_one_param(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    query = 'gymnasielärare'
    json_response = get_search(session, search_url, params={'q': query, 'limit': '0'})
    compare(json_response['total']['value'], expected=18)


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.parametrize("query, expected_number_of_hits, identifier", [
    ('"gymnasielärare"', 5, 'a'),
    ("'gymnasielärare'", 4, 'b'),
    ("\"gymnasielärare\"", 5, 'c'),
    ("\'gymnasielärare\'", 4, 'd'),
    ("""gymnasielärare""", 18, 'e'),
    ('''gymnasielärare''', 18, 'f'),
    ('gymnasielärare', 18, 'g'),
    ("gymnasielärare""", 18, 'h'),
])
def test_query_with_different_quotes(session, search_url, query, expected_number_of_hits, identifier):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': query, 'limit': '0'})
    compare(json_response['total']['value'], expected_number_of_hits, msg=f'Query: {query}')


# Todo: different queries
@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.integration
@pytest.mark.parametrize("minimum_relevance, expect_to_get_results",
                         [(0, True), (1, True), (2, False), (3, False), (4, False), (5, False), (6, False), (7, False),
                          (8, False), (9, False)])
def test_min_relevance_new(session, search_url, minimum_relevance, expect_to_get_results):
    query = 'sjuksköterska grundutbildad'
    params = {'q': query, search_settings.MIN_RELEVANCE: minimum_relevance}
    json_response = get_search(session, search_url, params)
    hits_total = json_response['total']['value']
    if expect_to_get_results:
        assert int(hits_total) > 0, f"no hits for query '{query}' with 'relevance-threshold' {minimum_relevance}"
    else:
        assert int(hits_total) == 0, f"Expected no hits for query '{query}' but got {int(hits_total)}"


@pytest.mark.integration
@pytest.mark.parametrize("query, expected", [('python', 8),
                                             ('python php', 7),
                                             ('+python php', 7),
                                             ('+python -php', 7),
                                             ('-python -php', 1065),  # of 1072
                                             ('php', 0),  # ?
                                             ('systemutvecklare +python java linux mac', 2),
                                             ('systemutvecklare +python -java linux mac', 0),
                                             ('systemutvecklare python java php', 12),
                                             ('systemutvecklare -python java php', 10),
                                             ('systemutvecklare python java -php', 12),
                                             ('lärarexamen', 6),
                                             ('lärarexamen -lärare', 1),
                                             ('sjuksköterska', 85),
                                             ('sjuksköterska -stockholm', 77),
                                             ('sjuksköterska -malmö', 82),
                                             ('sjuksköterska -stockholm -malmö', 74),
                                             ('sjuksköterska -stockholm -malmö -göteborg -eskilstuna', 67),
                                             ('sjuksköterska Helsingborg -stockholm -malmö -göteborg -eskilstuna', 1)
                                             # 3 ads with work_place.municipality Helsingborg
                                             ])
def test_freetext_plus_minus(session, search_url, query, expected):
    """
    Tests query with plus and minus modifiers
    :param query: Which terms to search for, icluding + - modifiers
    :param expected:  How many hits are expected from the test data
    :return: None if expected number of hits are found, AssertionError if not
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': query, 'limit': '0'})
    compare(json_response['total']['value'], expected, msg=f'Query: {query}')


@pytest.mark.integration
@pytest.mark.parametrize("typo, expected_number_of_hits", [('sjukssköterska', 85),
                                                           ('javasscript', 10)
                                                           # 'montesori' # todo: no match for 'montesori'
                                                           ])
def test_freetext_query_misspelled_param(session, search_url, typo, expected_number_of_hits):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': typo, 'limit': '0'})
    compare(json_response['total']['value'], expected_number_of_hits, msg=f'Query: {typo}')


@pytest.mark.integration
@pytest.mark.parametrize("special, expected_number_of_hits", [('c++', 7), ('c#', 15)])
def test_freetext_query_with_special_characters(session, search_url, special, expected_number_of_hits):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': special, 'limit': '0'})
    compare(json_response['total']['value'], expected_number_of_hits, msg=f'Query: {special}')


@pytest.mark.integration
@pytest.mark.parametrize("geo, expected_number_of_hits", [
    ('kista', 6),
    ('gärdet', 1),
    ('stockholm', 205),
    ('skåne', 130),
    ('värmland', 18),
    ('örebro', 23),
    ('örebro län', 28),
    ('rissne', 1)
])
def test_freetext_query_geo_param(session, search_url, geo, expected_number_of_hits):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    # todo check this test and remove the comment below
    # kista: 119 (46)
    # gärdet: 62 (8)
    # råsunda: 8 (8)
    # stockholm: 5826 (1196)
    # skåne: 2718 (260)
    # värmland: 103 (47)
    # örebro: 351 (178)
    # örebros län: 66 (66)

    json_response = get_search(session, search_url, params={'q': geo, 'limit': '0'})

    compare(json_response['total']['value'], expected_number_of_hits, geo)


@pytest.mark.integration
def test_bugfix_reset_query_rewrite_location(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': 'rissne', 'limit': '0'})
    check_value_more_than(json_response['total']['value'], 0)


@pytest.mark.integration
@pytest.mark.parametrize("query_location, expected", [
    ('kista kallhäll', 7),
    ('vara', 1),
    ('kallhäll', 1),
    ('kallhäll introduktion', 0),  # Todo: what is expected here?
    ('kallhäll ystad', 5),
    ('stockholm malmö', 240)
])
def test_freetext_query_location_extracted_or_enriched_or_freetext(session, search_url, query_location, expected):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': query_location, 'limit': '0'})
    compare(json_response['total']['value'], expected, f"Query: {query_location} ")


@pytest.mark.integration
def test_too_big_offset(session, search_url):
    print('===================', sys._getframe().f_code.co_name, '================== ')
    response = session.get(f"{search_url}/search", params={'offset': '2001', 'limit': '0'})
    assert response.status_code == requests.codes.bad_request
    response_json = json.loads(response.content.decode('utf8'))
    assert response_json['errors']['offset'] == "Invalid argument: 2001. argument must be within the range 0 - 2000"
    assert 'Input payload validation failed' in str(response.text)


@pytest.mark.integration
def test_total_hits(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'offset': '0', 'limit': '0'})
    hits_total = json_response['total']['value']
    compare(hits_total, NUMBER_OF_ADS)


@pytest.mark.integration
def test_find_all_ads_check_removed_is_false(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    limit = 100
    for offset in range(0, NUMBER_OF_ADS, limit):
        json_response = get_search(session, search_url, params={'offset': offset, 'limit': limit})
        hits = json_response['hits']
        for hit in hits:
            assert hit['removed'] is False
        if NUMBER_OF_ADS - offset > limit:
            expected = limit
        else:
            expected = NUMBER_OF_ADS % limit
        compare(len(hits), expected)


@pytest.mark.integration
def test_freetext_query_job_title_with_hyphen(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': 'HR-specialister', 'limit': '1'})
    assert json_response['freetext_concepts']
    assert json_response['freetext_concepts']['occupation']
    occupation_val = json_response['freetext_concepts']['occupation'][0]
    assert occupation_val == 'hr-specialist'


@pytest.mark.integration
def test_freetext_query_two_params(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': 'gymnasielärare lokförare', 'limit': '0'})
    compare(json_response['total']['value'], expected=18)


@pytest.mark.integration
def test_publication_range(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    date_from = "2019-02-01T00:00:00"
    date_until = "2020-04-20T00:00:00"
    params = {search_settings.PUBLISHED_AFTER: date_from, search_settings.PUBLISHED_BEFORE: date_until, "limit": 100}
    json_response = get_search(session, search_url, params)
    hits = json_response['hits']
    assert len(hits) > 0
    for hit in hits:
        assert parser.parse(hit[fields.PUBLICATION_DATE]) >= parser.parse(date_from)
        assert parser.parse(hit[fields.PUBLICATION_DATE]) <= parser.parse(date_until)


@pytest.mark.integration
def test_driving_license_required(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result(session, search_url, {taxonomy.DRIVING_LICENCE_REQUIRED: 'true'},
                               [fields.DRIVING_LICENCE_REQUIRED], [True])
    _fetch_and_validate_result(session, search_url, {taxonomy.DRIVING_LICENCE_REQUIRED: 'false'},
                               [fields.DRIVING_LICENCE_REQUIRED], [False])


@pytest.mark.parametrize("query, path, expected, non_negative",
                         [({taxonomy.OCCUPATION: work.systemutvecklare_programmerare},
                           [fields.OCCUPATION + ".concept_id"], [work.systemutvecklare_programmerare], True),
                          ({taxonomy.OCCUPATION: f"-{work.systemutvecklare_programmerare}"},
                           [fields.OCCUPATION + ".concept_id"], [work.systemutvecklare_programmerare], False),
                          ({taxonomy.GROUP: group.mjukvaru__och_systemutvecklare_m_fl_},
                           [fields.OCCUPATION_GROUP + ".concept_id"],
                           [group.mjukvaru__och_systemutvecklare_m_fl_], True),
                          ({taxonomy.FIELD: field.data_it}, [fields.OCCUPATION_FIELD + ".concept_id"], [field.data_it],
                           True),
                          ({taxonomy.FIELD: f"-{field.data_it}"}, [fields.OCCUPATION_FIELD + ".concept_id"],
                           [field.data_it], False),
                          ({taxonomy.GROUP: "2512"}, [fields.OCCUPATION_GROUP + ".legacy_ams_taxonomy_id"], ["2512"],
                           True),
                          ({taxonomy.FIELD: "3"}, [fields.OCCUPATION_FIELD + ".legacy_ams_taxonomy_id"], ["3"], True),
                          ({taxonomy.FIELD: "-3"}, [fields.OCCUPATION_FIELD + ".legacy_ams_taxonomy_id"], ["3"], False),

                          # 0 results
                          # TODO check this
                          # ({taxonomy.OCCUPATION: "D7Ns_RG6_hD2"}, [fields.OCCUPATION + ".legacy_ams_taxonomy_id"],
                          # ["2419"], True)
                          ])
@pytest.mark.integration
def test_occupation_codes(session, search_url, query, path, expected, non_negative):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result(session, search_url, query, path, expected, non_negative)


@pytest.mark.integration
def test_skill(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    params = {taxonomy.SKILL: 'DHhX_uVf_y6X', "limit": 100}
    json_response = get_search(session, search_url, params)
    for hit in json_response['hits']:
        must = "DHhX_uVf_y6X" in [skill['concept_id']
                                  for skill in hit["must_have"]["skills"]]
        should = "DHhX_uVf_y6X" in [skill['concept_id']
                                    for skill in hit["nice_to_have"]["skills"]]
        assert must or should


@pytest.mark.integration
def test_negative_skill(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    params = {taxonomy.SKILL: '-DHhX_uVf_y6X', "limit": 100}
    json_response = get_search(session, search_url, params)
    for hit in json_response['hits']:
        assert "DHhX_uVf_y6X" not in [skill['concept_id']
                                      for skill in hit["must_have"]["skills"]]
        assert "DHhX_uVf_y6X" not in [skill['concept_id']
                                      for skill in hit["nice_to_have"]["skills"]]


@pytest.mark.integration
def test_worktime_extent(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result(session, search_url, {taxonomy.WORKTIME_EXTENT: '947z_JGS_Uk2'},
                               [fields.WORKING_HOURS_TYPE + ".concept_id"],
                               ['947z_JGS_Uk2'])


@pytest.mark.integration
def test_scope_of_work(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    params = {search_settings.PARTTIME_MIN: 50, search_settings.PARTTIME_MAX: 80, "limit": 100}
    json_response = get_search(session, search_url, params)
    including_max = False
    including_min = False
    for hit in json_response['hits']:
        assert hit['scope_of_work']['min'] >= 50
        assert hit['scope_of_work']['max'] <= 80
        if hit['scope_of_work']['min'] == 50:
            including_min = True
        if hit['scope_of_work']['max'] == 80:
            including_max = True

    assert including_min
    assert including_max


@pytest.mark.integration
def test_driving_licence(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    params = {taxonomy.DRIVING_LICENCE: ['VTK8_WRx_GcM'], "limit": 100}
    json_response = get_search(session, search_url, params)
    for hit in json_response['hits']:
        concept_ids = [item['concept_id'] for item in hit[fields.DRIVING_LICENCE]]
        assert 'VTK8_WRx_GcM' in concept_ids


@pytest.mark.integration
def test_employment_type(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result(session, search_url, {taxonomy.EMPLOYMENT_TYPE: 'PFZr_Syz_cUq'},
                               [fields.EMPLOYMENT_TYPE + ".concept_id"], ['PFZr_Syz_cUq'])


@pytest.mark.integration
def test_experience(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result(session, search_url, {search_settings.EXPERIENCE_REQUIRED: 'true'},
                               [fields.EXPERIENCE_REQUIRED], [True])
    _fetch_and_validate_result(session, search_url, {search_settings.EXPERIENCE_REQUIRED: 'false'},
                               [fields.EXPERIENCE_REQUIRED], [False])


@pytest.mark.integration
def test_region(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    _fetch_and_validate_result(session, search_url, {taxonomy.REGION: '01'},
                               [fields.WORKPLACE_ADDRESS_REGION_CODE], ['01'])
    _fetch_and_validate_result(session, search_url, {taxonomy.REGION: '-01'},
                               [fields.WORKPLACE_ADDRESS_REGION_CODE], ['01'], False)
    # TODO: this test does not work with parametrize


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
