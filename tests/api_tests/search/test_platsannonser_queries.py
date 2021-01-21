import os
import pytest
import requests
import json
from dateutil import parser
from sokannonser import settings as search_settings
from sokannonser.repository import taxonomy
from sokannonser.rest.model import fields
from tests.test_resources.settings import NUMBER_OF_ADS, TEST_USE_STATIC_DATA
from tests.test_resources.helper import get_search, get_search_expect_error, compare, _fetch_and_validate_result, \
    check_value_more_than
from tests.test_resources.concept_ids import occupation as work, occupation_field as field, \
    occupation_group as group


@pytest.mark.smoke
@pytest.mark.integration
def test_freetext_query_one_param(session):
    query = 'gymnasielärare'
    json_response = get_search(session, params={'q': query, 'limit': '0'})
    compare(json_response['total']['value'], expected=11)


def test_enrich(session):
    query = 'stresstålig'
    json_response = get_search(session, params={'q': query, 'limit': '0'})
    compare(json_response['total']['value'], expected=46)


# Todo: different queries
@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.integration
@pytest.mark.parametrize("minimum_relevance, expect_to_get_results",
                         [(0, True), (1, True), (2, False), (3, False), (4, False), (5, False), (6, False), (7, False),
                          (8, False), (9, False)])
def test_min_relevance_new(session, minimum_relevance, expect_to_get_results):
    query = 'sjuksköterska grundutbildad'
    params = {'q': query, search_settings.MIN_RELEVANCE: minimum_relevance}
    json_response = get_search(session, params)
    hits_total = json_response['total']['value']
    if expect_to_get_results:
        assert int(hits_total) > 0, f"no hits for query '{query}' with 'relevance-threshold' {minimum_relevance}"
    else:
        assert int(hits_total) == 0, f"Expected no hits for query '{query}' but got {int(hits_total)}"


@pytest.mark.integration
@pytest.mark.parametrize("query, expected", [('python', 23),
                                             ('python php', 24),
                                             ('+python php', 23),
                                             ('+python -php', 22),
                                             ('-python -php', 1471),  # of 1495
                                             ('php', 2),
                                             ('systemutvecklare +python java linux mac', 7),
                                             ('systemutvecklare +python -java linux mac', 4),
                                             ('systemutvecklare python java php', 15),
                                             ('systemutvecklare -python java php', 8),
                                             ('systemutvecklare python java -php', 13),
                                             ('lärarexamen', 4),
                                             ('lärarexamen -lärare', 1),
                                             ('sjuksköterska', 126),
                                             ('sjuksköterska -stockholm', 117),
                                             ('sjuksköterska -malmö', 122),
                                             ('sjuksköterska -stockholm -malmö', 113),
                                             ('sjuksköterska -stockholm -malmö -göteborg -eskilstuna', 109),
                                             ('sjuksköterska Helsingborg -stockholm -malmö -göteborg -eskilstuna', 3)
                                             ])
def test_freetext_plus_minus(session, query, expected):
    """
    Tests query with plus and minus modifiers
    :param query: Which terms to search for, icluding + - modifiers
    :param expected:  How many hits are expected from the test data
    :return: None if expected number of hits are found, AssertionError if not
    """
    json_response = get_search(session, params={'q': query, 'limit': '100'})
    for hit in json_response['hits']:
        print(hit['id'])
    compare(json_response['total']['value'], expected, msg=f'Query: {query}')


@pytest.mark.integration
@pytest.mark.parametrize("typo, expected_number_of_hits", [('sjukssköterska', 126),
                                                           ('javasscript', 20),
                                                           ('montesori', 2)
                                                           ])
def test_freetext_query_misspelled_param(session, typo, expected_number_of_hits):
    json_response = get_search(session, params={'q': typo, 'limit': '0'})
    compare(json_response['total']['value'], expected_number_of_hits, msg=f'Query: {typo}')


@pytest.mark.integration
@pytest.mark.parametrize("special, expected_number_of_hits", [
    ('c++', 16),
    ('c#', 16)])
def test_freetext_query_with_special_characters(session, special, expected_number_of_hits):
    json_response = get_search(session, params={'q': special, 'limit': '0'})
    compare(json_response['total']['value'], expected_number_of_hits, msg=f'Query: {special}')


@pytest.mark.integration
@pytest.mark.parametrize("geo, expected_number_of_hits", [
    ('kista', 5),
    ('gärdet', 3),
    ('stockholm', 299),
    ('skåne', 197),
    ('värmland', 30),
    ('örebro', 28),
    ('örebro län', 37),
    ('rissne', 1)
])
def test_freetext_query_geo_param(session, geo, expected_number_of_hits):
    json_response = get_search(session, params={'q': geo, 'limit': '0'})
    compare(json_response['total']['value'], expected_number_of_hits, geo)


@pytest.mark.integration
def test_bugfix_reset_query_rewrite_location(session):
    json_response = get_search(session, params={'q': 'rissne', 'limit': '0'})
    check_value_more_than(json_response['total']['value'], 0)


@pytest.mark.integration
@pytest.mark.parametrize("query_location, expected", [
    ('kista kallhäll', 5),
    ('vara', 918),
    ('kallhäll', 0),
    ('kallhäll introduktion', 0),  # Todo: what is expected here?
    ('kallhäll ystad', 5),
    ('stockholm malmö', 378)
])
def test_freetext_query_location_extracted_or_enriched_or_freetext(session, query_location, expected):
    json_response = get_search(session, params={'q': query_location, 'limit': '0'})
    compare(json_response['total']['value'], expected, f"Query: {query_location} ")


@pytest.mark.integration
def test_too_big_offset(session):
    response = get_search_expect_error(session, params={'offset': '2001', 'limit': '0'},
                                       expected_http_code=requests.codes.bad_request)
    response_json = json.loads(response.content.decode('utf8'))
    assert response_json['errors']['offset'] == "Invalid argument: 2001. argument must be within the range 0 - 2000"
    assert 'Input payload validation failed' in str(response.text)


@pytest.mark.integration
def test_total_hits(session):
    json_response = get_search(session, params={'offset': '0', 'limit': '0'})
    hits_total = json_response['total']['value']
    compare(hits_total, NUMBER_OF_ADS)


@pytest.mark.integration
def test_find_all_ads_check_removed_is_false(session):
    limit = 100
    for offset in range(0, NUMBER_OF_ADS, limit):
        json_response = get_search(session, params={'offset': offset, 'limit': limit})
        hits = json_response['hits']
        print()
        print("all_ads = [ ")
        for hit in hits:
            assert hit['removed'] is False
            print(f"{hit}, ")
        if NUMBER_OF_ADS - offset > limit:
            expected = limit
        else:
            expected = NUMBER_OF_ADS % limit
        compare(len(hits), expected)
        print("]")
        print()


@pytest.mark.integration
def test_freetext_query_job_title_with_hyphen(session):
    json_response = get_search(session, params={'q': 'HR-specialister', 'limit': '1'})
    assert json_response['freetext_concepts']
    assert json_response['freetext_concepts']['occupation']
    occupation_val = json_response['freetext_concepts']['occupation'][0]
    assert occupation_val == 'hr-specialist'


@pytest.mark.integration
def test_freetext_query_two_params(session):
    json_response = get_search(session, params={'q': 'gymnasielärare lokförare', 'limit': '0'})
    compare(json_response['total']['value'], expected=11)


@pytest.mark.integration
def test_publication_range(session):
    date_from = "2020-12-01T00:00:00"
    date_until = "2020-12-20T00:00:00"
    params = {search_settings.PUBLISHED_AFTER: date_from, search_settings.PUBLISHED_BEFORE: date_until, "limit": 100}
    json_response = get_search(session, params)
    hits = json_response['hits']
    assert len(hits) == 100
    for hit in hits:
        assert parser.parse(hit[fields.PUBLICATION_DATE]) >= parser.parse(date_from)
        assert parser.parse(hit[fields.PUBLICATION_DATE]) <= parser.parse(date_until)


@pytest.mark.integration
def test_driving_license_required(session):
    _fetch_and_validate_result(session, {taxonomy.DRIVING_LICENCE_REQUIRED: 'true'}, [fields.DRIVING_LICENCE_REQUIRED],
                               [True])
    _fetch_and_validate_result(session, {taxonomy.DRIVING_LICENCE_REQUIRED: 'false'}, [fields.DRIVING_LICENCE_REQUIRED],
                               [False])


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
def test_occupation_codes(session, query, path, expected, non_negative):
    _fetch_and_validate_result(session, query, path, expected, non_negative)


@pytest.mark.integration
def test_skill(session):
    params = {taxonomy.SKILL: 'DHhX_uVf_y6X', "limit": 100}
    json_response = get_search(session, params)
    for hit in json_response['hits']:
        must = "DHhX_uVf_y6X" in [skill['concept_id']
                                  for skill in hit["must_have"]["skills"]]
        should = "DHhX_uVf_y6X" in [skill['concept_id']
                                    for skill in hit["nice_to_have"]["skills"]]
        assert must or should


@pytest.mark.integration
def test_negative_skill(session):
    params = {taxonomy.SKILL: '-DHhX_uVf_y6X', "limit": 100}
    json_response = get_search(session, params)
    for hit in json_response['hits']:
        assert "DHhX_uVf_y6X" not in [skill['concept_id']
                                      for skill in hit["must_have"]["skills"]]
        assert "DHhX_uVf_y6X" not in [skill['concept_id']
                                      for skill in hit["nice_to_have"]["skills"]]

# 0 hits
@pytest.mark.integration
def test_worktime_extent(session):

    _fetch_and_validate_result(session, query={taxonomy.WORKTIME_EXTENT: '6YE1_gAC_R2G'},
                               resultfield=[fields.WORKING_HOURS_TYPE + ".concept_id"],
                               expected=['6YE1_gAC_R2G'])


@pytest.mark.integration
def test_scope_of_work(session):
    params = {search_settings.PARTTIME_MIN: 50, search_settings.PARTTIME_MAX: 80, "limit": 100}
    json_response = get_search(session, params)
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
def test_driving_licence(session):
    params = {taxonomy.DRIVING_LICENCE: ['VTK8_WRx_GcM'], "limit": 100}
    json_response = get_search(session, params)
    for hit in json_response['hits']:
        concept_ids = [item['concept_id'] for item in hit[fields.DRIVING_LICENCE]]
        assert 'VTK8_WRx_GcM' in concept_ids

# 0 hits
@pytest.mark.integration
def test_employment_type(session):
    _fetch_and_validate_result(session, {taxonomy.EMPLOYMENT_TYPE: 'PFZr_Syz_cUq'},
                               [fields.EMPLOYMENT_TYPE + ".concept_id"], ['PFZr_Syz_cUq'])


@pytest.mark.integration
def test_experience(session):
    _fetch_and_validate_result(session, {search_settings.EXPERIENCE_REQUIRED: 'true'}, [fields.EXPERIENCE_REQUIRED],
                               [True])
    _fetch_and_validate_result(session, {search_settings.EXPERIENCE_REQUIRED: 'false'}, [fields.EXPERIENCE_REQUIRED],
                               [False])


@pytest.mark.integration
def test_region(session):
    _fetch_and_validate_result(session, {taxonomy.REGION: '01'}, [fields.WORKPLACE_ADDRESS_REGION_CODE], ['01'])
    _fetch_and_validate_result(session, {taxonomy.REGION: '-01'}, [fields.WORKPLACE_ADDRESS_REGION_CODE], ['01'], False)
    # TODO: this test does not work with parametrize


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
