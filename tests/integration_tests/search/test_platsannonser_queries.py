import sys
import os
import pytest
import requests
import json
from dateutil import parser
from sokannonser import app
from sokannonser import settings as search_settings
from sokannonser.repository import taxonomy
from sokannonser.rest.model import fields
from tests.integration_tests.test_resources.check_response import check_response_return_json
from sokannonser.settings import NUMBER_OF_ADS, headers
from tests.integration_tests.test_resources.helper import get_search


@pytest.mark.skip(
    reason="Temporarily disabled. Needs fix according to Trello Card #137, Multipla ord i ett yrke")  # Missing test data?
@pytest.mark.integration
def test_freetext_query_ssk():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        query = 'stockholm grundutbildad sjuksköterska'
        result = testclient.get('/search', headers=headers, data={'q': query, 'limit': '0'})
        json_response = check_response_return_json(result)
        hits_total = json_response['total']['value']
        assert int(hits_total) > 0, f"no hits for query '{query}'"


@pytest.mark.smoke
@pytest.mark.integration
def test_freetext_query_one_param():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    app.testing = True
    with app.test_client() as testclient:
        query = 'gymnasielärare'
        result = testclient.get('/search', headers=headers, data={'q': query, 'limit': '0'})
        json_response = check_response_return_json(result)
        hits_total = json_response['total']['value']
        assert int(hits_total) > 0, f"no hits for query '{query}'"


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
    assert int(json_response['total']['value']) == expected_number_of_hits, f"wrong number of hits for query '{query}'"


# Todo: different queries
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
    hits_total = json_response['total']['value']
    assert int(hits_total) == expected, f"expected {expected} hits but got {hits_total} for query '{query}'"


@pytest.mark.integration
@pytest.mark.parametrize("typo, expected_number_of_hits", [('sjukssköterska', 85),
                                                           ('javasscript', 10)
                                                           # 'montesori' # todo: no match for 'montesori'
                                                           ])
def test_freetext_query_misspelled_param(session, search_url, typo, expected_number_of_hits):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': typo, 'limit': '0'})
    hits_total = json_response['total']['value']
    assert int(
        hits_total) == expected_number_of_hits, f"expected {expected_number_of_hits} hits but got {hits_total} for query '{typo}'"


@pytest.mark.integration
@pytest.mark.parametrize("special, expected_number_of_hits", [('c++', 7), ('c#', 15)])
def test_freetext_query_with_special_characters(session, search_url, special, expected_number_of_hits):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': special, 'limit': '0'})
    hits_total = json_response['total']['value']
    assert int(
        hits_total) == expected_number_of_hits, f"expected {expected_number_of_hits} hits but got {hits_total} for query '{typo}'"


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
    hits_total = json_response['total']['value']
    assert int(
        hits_total) == expected_number_of_hits, f"expected {expected_number_of_hits} hits but got {hits_total} for query '{typo}'"


@pytest.mark.integration
def test_bugfix_reset_query_rewrite_location(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_search(session, search_url, params={'q': 'rissne', 'limit': '0'})
    assert int(json_response['total']['value']) > 0, f"no hits for query 'rissne'"


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
    hits_total = json_response['total']['value']
    assert int(
        hits_total) == expected, f"Expected {expected} hits for query '{query_location}' but got {hits_total}"


@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_geo_param2():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    # kista: 119 (46)
    # gärdet: 62 (8)
    # råsunda: 8 (8)
    # stockholm: 5826 (1196)
    # skåne: 2718 (260)
    # värmland: 103 (47)
    # örebro: 351 (178)
    # örebros län: 66 (66)

    app.testing = True
    with app.test_client() as testclient:
        # result = testclient.get('/search', headers=headers, data={'q': 'sjukssköterska noggran javasscript',
        #                                                           'limit': '1'})
        result_freetext = testclient.get('/search', headers=headers, data={'q': 'restaurangbiträde stockholm',
                                                                           'limit': '100'})
        json_response = result_freetext.json
        # pprint(json_response)

        hits_total = json_response['total']['value']
        # print(hits_total)

        ids_freetext = [hit['id'] for hit in json_response['hits']]
        result_freetext2 = testclient.get('/search', headers=headers, data={'q': 'restaurangbiträde stockholm',
                                                                            'limit': '100', 'offset': 80})
        json_response2 = result_freetext2.json
        ids_freetext.extend([hit['id'] for hit in json_response2['hits']])

        # pprint(sorted(ids_freetext))

        result_taxonomy = testclient.get('/search', headers=headers, data={'occupation-name': '5555', 'q': 'stockholm',
                                                                           'limit': '100'})
        json_response_tax = result_taxonomy.json
        # pprint(json_response)

        hits_total_tax = json_response_tax['total']['value']
        # print(hits_total_tax)

        ids_tax = [hit['id'] for hit in json_response_tax['hits']]

        result_taxonomy2 = testclient.get('/search', headers=headers, data={'occupation-name': '5555', 'q': 'stockholm',
                                                                            'limit': '100', 'offset': 80})
        json_response_tax2 = result_taxonomy2.json
        ids_tax.extend([hit['id'] for hit in json_response_tax2['hits']])

        # pprint(sorted(ids_tax))

        result_ids_tax_minus_freetext = sorted(list(set(ids_tax) - set(ids_freetext)))
        # print('tax - free', result_ids_tax_minus_freetext)
        # All hits in structured search should be covered when doing an equivalent freetext search.
        assert len(result_ids_tax_minus_freetext) == 0
        # print('free - tax', sorted(list(set(ids_freetext) - set(ids_tax))))


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
    assert int(hits_total) == NUMBER_OF_ADS, f"too few hits, actual number: {hits_total} "


@pytest.mark.integration
def test_removed_ads_should_not_be_in_result():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        for offset in range(0, 1100, 100):
            result = testclient.get('/search', headers=headers, data={'offset': offset, 'limit': '100'})
            json_response = check_response_return_json(result)
            hits = json_response['hits']
            # todo check this
            # removed the code below since there are not enough ads in the test data
            # the point of the test is to check all ads and see that 'removed' is False
            # new test created that will verify that all ads can be collected 100 at the time
            # assert len(hits) == 100, f"wrong number of hits, actual number: {len(hits)} "
            for hit in hits:
                assert hit['removed'] is False


@pytest.mark.integration
def test_find_all_ads(session, search_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    limit = 100
    for offset in range(0, NUMBER_OF_ADS, limit):
        json_response = get_search(session, search_url, params={'offset': offset, 'limit': limit})
        hits = json_response['hits']
        if NUMBER_OF_ADS - offset > limit:
            expected = limit
        else:
            expected = NUMBER_OF_ADS % limit
        assert len(hits) == expected, f"wrong number of hits, actual number: {len(hits)} "

    app.testing = True
    with app.test_client() as testclient:
        limit = 100
        for offset in range(0, NUMBER_OF_ADS, limit):
            result = testclient.get('/search', headers=headers, data={'offset': offset, 'limit': limit})
            json_response = check_response_return_json(result)
            hits = json_response['hits']
            if NUMBER_OF_ADS - offset > limit:
                expected = limit
            else:
                expected = NUMBER_OF_ADS % limit
            assert len(hits) == expected, f"wrong number of hits, actual number: {len(hits)} "


@pytest.mark.integration
def test_freetext_query_job_title_with_hyphen():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        result = testclient.get('/search', headers=headers, data={'q': 'HR-specialister', 'limit': '1'})
        json_response = check_response_return_json(result)
        assert json_response['freetext_concepts']
        assert json_response['freetext_concepts']['occupation']
        occupation_val = str(json_response['freetext_concepts']['occupation'][0])
        assert occupation_val == 'hr-specialist'


@pytest.mark.integration
def test_freetext_query_two_params():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        query = 'gymnasielärare lokförare'  # todo: is this an OR search? In that case it makes sens
        result = testclient.get('/search', headers=headers, data={'q': query, 'limit': '0'})
        json_response = check_response_return_json(result)
        hits_total = json_response['total']['value']
        assert int(hits_total) == 18, f"Expected 18 hits for query '{query}' but got {hits_total}"


@pytest.mark.integration
def test_publication_range():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    app.testing = True
    with app.test_client() as testclient:
        date_from = "2019-02-01T00:00:00"
        date_until = "2019-04-20T00:00:00"
        query = {search_settings.PUBLISHED_AFTER: date_from,
                 search_settings.PUBLISHED_BEFORE: date_until,
                 "limit": 100}
        result = testclient.get('/search', headers=headers, data=query)
        json_response = check_response_return_json(result)
        hits = json_response['hits']
        for hit in hits:
            assert parser.parse(hit[fields.PUBLICATION_DATE]) >= parser.parse(date_from)
            assert parser.parse(hit[fields.PUBLICATION_DATE]) <= parser.parse(date_until)


def _get_nested_value(path, dictionary):
    keypath = path.split('.')
    value = None
    for i in range(len(keypath)):
        element = dictionary.get(keypath[i])
        if isinstance(element, dict):
            dictionary = element
        else:
            value = element
            break
    return value


def _fetch_and_validate_result(query, resultfield, expected, non_negative=True):
    app.testing = True
    with app.test_client() as testclient:
        result = testclient.get('/search', headers=headers, data=query)
        json_response = check_response_return_json(result)
        hits = json_response['hits']
        for hit in hits:
            for i in range(len(resultfield)):
                if non_negative:
                    assert _get_nested_value(resultfield[i], hit) == expected[i]
                else:
                    assert not _get_nested_value(resultfield[i], hit) == expected[i]


@pytest.mark.integration
def test_driving_license_required():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result({taxonomy.DRIVING_LICENCE_REQUIRED: 'true'},
                               [fields.DRIVING_LICENCE_REQUIRED], [True])
    _fetch_and_validate_result({taxonomy.DRIVING_LICENCE_REQUIRED: 'false'},
                               [fields.DRIVING_LICENCE_REQUIRED], [False])


@pytest.mark.parametrize("query, path, expected, non_negative",
                         [({taxonomy.OCCUPATION: "fg7B_yov_smw"},
                           [fields.OCCUPATION + ".concept_id"], ["fg7B_yov_smw"], True),
                          ({taxonomy.OCCUPATION: "-fg7B_yov_smw"},
                           [fields.OCCUPATION + ".concept_id"], ["fg7B_yov_smw"], False),
                          ({taxonomy.GROUP: "DJh5_yyF_hEM"},
                           [fields.OCCUPATION_GROUP + ".concept_id"],
                           ["DJh5_yyF_hEM"], True),
                          ({taxonomy.FIELD: "apaJ_2ja_LuF"},
                           [fields.OCCUPATION_FIELD + ".concept_id"],
                           ["apaJ_2ja_LuF"], True),
                          ({taxonomy.FIELD: "-apaJ_2ja_LuF"},
                           [fields.OCCUPATION_FIELD + ".concept_id"],
                           ["apaJ_2ja_LuF"], False),
                          ({taxonomy.OCCUPATION: "D7Ns_RG6_hD2"},
                           [fields.OCCUPATION + ".legacy_ams_taxonomy_id"], ["2419"], True),
                          ({taxonomy.GROUP: "2512"},
                           [fields.OCCUPATION_GROUP + ".legacy_ams_taxonomy_id"],
                           ["2512"], True),
                          ({taxonomy.FIELD: "3"},
                           [fields.OCCUPATION_FIELD + ".legacy_ams_taxonomy_id"],
                           ["3"], True),
                          ({taxonomy.FIELD: "-3"},
                           [fields.OCCUPATION_FIELD + ".legacy_ams_taxonomy_id"],
                           ["3"], False)
                          ])
@pytest.mark.integration
def test_occupation_codes(query, path, expected, non_negative):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result(query, path, expected, non_negative)


@pytest.mark.parametrize("query, path, expected",
                         [({taxonomy.OCCUPATION: "D7Ns_RG6_hD2",
                            taxonomy.MUNICIPALITY: "0180", "limit": 100},
                           [fields.OCCUPATION + ".concept_id",
                            fields.WORKPLACE_ADDRESS_MUNICIPALITY],
                           ["D7Ns_RG6_hD2", "0180"]),
                          ])
@pytest.mark.integration
def test_occupation_location_combo(query, path, expected):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result(query, path, expected)


@pytest.mark.integration
def test_skill():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    app.testing = True
    with app.test_client() as testclient:
        query = {taxonomy.SKILL: 'DHhX_uVf_y6X', "limit": 100}
        result = testclient.get('/search', headers=headers, data=query)
        json_response = check_response_return_json(result)
        hits = json_response['hits']
        for hit in hits:
            must = "DHhX_uVf_y6X" in [skill['concept_id']
                                      for skill in hit["must_have"]["skills"]]
            should = "DHhX_uVf_y6X" in [skill['concept_id']
                                        for skill in hit["nice_to_have"]["skills"]]
            assert must or should


@pytest.mark.integration
def test_negative_skill():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    app.testing = True
    with app.test_client() as testclient:
        query = {taxonomy.SKILL: '-DHhX_uVf_y6X', "limit": 100}
        result = testclient.get('/search', headers=headers, data=query)
        json_response = check_response_return_json(result)
        hits = json_response['hits']
        for hit in hits:
            assert "DHhX_uVf_y6X" not in [skill['concept_id']
                                          for skill in hit["must_have"]["skills"]]
            assert "DHhX_uVf_y6X" not in [skill['concept_id']
                                          for skill in hit["nice_to_have"]["skills"]]


@pytest.mark.integration
def test_worktime_extent():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result({taxonomy.WORKTIME_EXTENT: '947z_JGS_Uk2'},
                               [fields.WORKING_HOURS_TYPE + ".concept_id"],
                               ['947z_JGS_Uk2'])


@pytest.mark.integration
def test_scope_of_work():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    app.testing = True
    with app.test_client() as testclient:
        query = {search_settings.PARTTIME_MIN: 50, search_settings.PARTTIME_MAX: 80, "limit": 100}
        result = testclient.get('/search', headers=headers, data=query)
        json_response = check_response_return_json(result)
        hits = json_response['hits']
        including_max = False
        including_min = False
        for hit in hits:
            assert hit['scope_of_work']['min'] >= 50
            assert hit['scope_of_work']['max'] <= 80
            if hit['scope_of_work']['min'] == 50:
                including_min = True
            if hit['scope_of_work']['max'] == 80:
                including_max = True

        assert including_min
        assert including_max


@pytest.mark.integration
def test_driving_licence():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    app.testing = True
    with app.test_client() as testclient:
        query = {taxonomy.DRIVING_LICENCE: ['VTK8_WRx_GcM'], "limit": 100}
        result = testclient.get('/search', headers=headers, data=query)
        json_response = check_response_return_json(result)
        hits = json_response['hits']
        for hit in hits:
            concept_ids = [item['concept_id'] for item in hit[fields.DRIVING_LICENCE]]
            assert 'VTK8_WRx_GcM' in concept_ids


@pytest.mark.integration
def test_employment_type():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result({taxonomy.EMPLOYMENT_TYPE: 'PFZr_Syz_cUq'},
                               [fields.EMPLOYMENT_TYPE + ".concept_id"], ['PFZr_Syz_cUq'])


@pytest.mark.integration
def test_experience():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result({search_settings.EXPERIENCE_REQUIRED: 'true'},
                               [fields.EXPERIENCE_REQUIRED], [True])
    _fetch_and_validate_result({search_settings.EXPERIENCE_REQUIRED: 'false'},
                               [fields.EXPERIENCE_REQUIRED], [False])


@pytest.mark.integration
def test_region():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result({taxonomy.REGION: '01'},
                               [fields.WORKPLACE_ADDRESS_REGION_CODE], ['01'])
    _fetch_and_validate_result({taxonomy.REGION: '-01'},
                               [fields.WORKPLACE_ADDRESS_REGION_CODE], ['01'], False)


@pytest.mark.integration
def test_country():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    _fetch_and_validate_result({taxonomy.REGION: '199'},
                               [fields.WORKPLACE_ADDRESS_REGION_CODE], ['199'])
    _fetch_and_validate_result({taxonomy.REGION: '-199'},
                               [fields.WORKPLACE_ADDRESS_REGION_CODE], ['199'], False)


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
