import sys
import os
import pytest
from pprint import pprint
from dateutil import parser
from sokannonser import app
from sokannonser import settings as search_settings
from sokannonser.repository import taxonomy
from sokannonser.rest.model import fields

test_api_key = os.getenv('TEST_API_KEY_PLATSANNONSER')


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_one_param():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers, data={'q': 'gymnasielärare',
                                                                  'limit': '1'})
        json_response = result.json
        # pprint(json_response)
        hits_total = json_response['total']['value']
        assert int(hits_total) > 0


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_too_big_offset():
    print('===================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers, data={'offset': '2001',
                                                                  'limit': '10'})
        json_response = result.json
        # pprint(json_response)
        assert 'errors' in json_response


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_total_hits():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers, data={'offset': '0',
                                                                  'limit': '10'})
        json_response = result.json
        # pprint(json_response)
        hits_total = json_response['total']['value']
        assert int(hits_total) > 10000


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_deprecated_ads_should_not_be_in_result():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        for offset in range(0, 2000, 100):
            # print(offs)
            result = testclient.get('/search', headers=headers, data={'offset': offset,
                                                                      'limit': '100'})
            json_response = result.json
            # # pprint(json_response)
            hits = json_response['hits']
            assert len(hits) > 0
            for hit in hits:
                assert hit['removed'] is False


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_job_title_with_hyphen():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers, data={'q': 'HR-specialister',
                                                                  'limit': '1'})
        json_response = result.json
        # pprint(json_response)
        assert json_response['freetext_concepts']
        assert json_response['freetext_concepts']['occupation']
        occupation_val = str(json_response['freetext_concepts']['occupation'][0])
        assert occupation_val == 'hr-specialist'


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_one_param_deleted_enriched():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers, data={'q': 'gymnasielärare',
                                                                  'limit': '10'})
        json_response = result.json
        # pprint(json_response)
        hits_total = json_response['total']['value']
        assert int(hits_total) > 0
        hits = json_response['hits']
        assert len(hits) > 0
        # pprint(hits[0])

        assert 'extracted' in hits[0]['keywords']
        assert 'enriched' not in hits[0]['keywords']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_one_param_found_in_enriched_pos():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers, data={'q': 'diskare',
                                                                  'limit': '100'})
        json_response = result.json
        pprint(json_response)
        # hits_total = json_response['total']
        # assert int(hits_total) > 0
        hits = json_response['hits']
        # assert len(hits) > 0
        pprint(hits[0])
        assert 'found_in_enriched' in hits[0]


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_one_param_found_in_enriched_neg():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers, data={'q': 'ninja',
                                                                  'limit': '100'})
        json_response = result.json
        pprint(json_response)
        # hits_total = json_response['total']
        # assert int(hits_total) > 0
        hits = json_response['hits']
        # assert len(hits) > 0
        # pprint(hits[0])
        for hit in hits:
            assert 'found_in_enriched' in hit
            assert hit['found_in_enriched'] is False


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_two_params():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers,
                                data={'q': 'gymnasielärare lokförare', 'limit': '0'})
        json_response = result.json
        # pprint(json_response)
        hits_total = json_response['total']['value']
        assert int(hits_total) > 0


@pytest.mark.integration
def test_publication_range():
    app.testing = True
    with app.test_client() as testclient:
        date_from = "2019-02-01T00:00:00"
        date_until = "2019-04-20T00:00:00"
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        query = {search_settings.PUBLISHED_AFTER: date_from,
                 search_settings.PUBLISHED_BEFORE: date_until,
                 "limit": 100}
        result = testclient.get('/search', headers=headers, data=query)
        json_response = result.json
        hits = json_response['hits']
        including_max = False
        including_min = False
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
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers,
                                data=query)
        json_response = result.json
        hits = json_response['hits']
        for hit in hits:
            for i in range(len(resultfield)):
                if non_negative:
                    assert _get_nested_value(resultfield[i], hit) == expected[i]
                else:
                    assert not _get_nested_value(resultfield[i], hit) == expected[i]


@pytest.mark.integration
def test_driving_license_required():
    _fetch_and_validate_result({taxonomy.DRIVING_LICENCE_REQUIRED: 'true'},
                               [fields.DRIVING_LICENCE_REQUIRED], [True])
    _fetch_and_validate_result({taxonomy.DRIVING_LICENCE_REQUIRED: 'false'},
                               [fields.DRIVING_LICENCE_REQUIRED], [False])


@pytest.mark.parametrize("query, path, expected, non_negative",
                         [({taxonomy.OCCUPATION: "D7Ns_RG6_hD2"},
                           [fields.OCCUPATION+".concept_id"], ["D7Ns_RG6_hD2"], True),
                          ({taxonomy.GROUP: "DJh5_yyF_hEM"},
                           [fields.OCCUPATION_GROUP+".concept_id"], ["DJh5_yyF_hEM"], True),
                          ({taxonomy.FIELD: "apaJ_2ja_LuF"},
                           [fields.OCCUPATION_FIELD+".concept_id"], ["apaJ_2ja_LuF"], True),
                          ({taxonomy.OCCUPATION: "D7Ns_RG6_hD2"},
                           [fields.OCCUPATION+".legacy_ams_taxonomy_id"], ["2419"], True),
                          ({taxonomy.GROUP: "2512"},
                           [fields.OCCUPATION_GROUP+".concept_id"], ["DJh5_yyF_hEM"], True),
                          ({taxonomy.FIELD: "3"},
                           [fields.OCCUPATION_FIELD+".legacy_ams_taxonomy_id"], ["3"], True),
                          ({taxonomy.FIELD: "-3"},
                           [fields.OCCUPATION_FIELD+".legacy_ams_taxonomy_id"], ["3"], False)
                          ])
@pytest.mark.integration
def test_occupation_codes(query, path, expected, non_negative):
    _fetch_and_validate_result(query, path, expected, non_negative)


@pytest.mark.parametrize("query, path, expected",
                         [({taxonomy.OCCUPATION: "D7Ns_RG6_hD2",
                            taxonomy.MUNICIPALITY: "0180", "limit": 100},
                           [fields.OCCUPATION+".concept_id",
                            fields.WORKPLACE_ADDRESS_MUNICIPALITY],
                           ["D7Ns_RG6_hD2", "0180"]),
                          ])
@pytest.mark.integration
def test_occupation_location_combo(query, path, expected):
    _fetch_and_validate_result(query, path, expected)


@pytest.mark.integration
def test_skill():
    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        query = {taxonomy.SKILL: 'DHhX_uVf_y6X', "limit": 100}
        result = testclient.get('/search', headers=headers, data=query)
        json_response = result.json
        hits = json_response['hits']
        for hit in hits:
            must = "DHhX_uVf_y6X" in [skill['concept_id']
                                      for skill in hit["must_have"]["skills"]]
            should = "DHhX_uVf_y6X" in [skill['concept_id']
                                        for skill in hit["nice_to_have"]["skills"]]
            assert must or should


@pytest.mark.integration
def test_negative_skill():
    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        query = {taxonomy.SKILL: '-DHhX_uVf_y6X', "limit": 100}
        result = testclient.get('/search', headers=headers, data=query)
        json_response = result.json
        hits = json_response['hits']
        for hit in hits:
            assert "DHhX_uVf_y6X" not in [skill['concept_id']
                                            for skill in hit["must_have"]["skills"]]
            assert "DHhX_uVf_y6X" not in [skill['concept_id']
                                            for skill in hit["nice_to_have"]["skills"]]


@pytest.mark.integration
def test_worktime_extent():
    _fetch_and_validate_result({taxonomy.WORKTIME_EXTENT: '947z_JGS_Uk2'},
                               [fields.WORKING_HOURS_TYPE+".concept_id"], ['947z_JGS_Uk2'])


@pytest.mark.integration
def test_scope_of_work():
    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        query = {search_settings.PARTTIME_MIN: 20, search_settings.PARTTIME_MAX: 80,
                 "limit": 100}
        result = testclient.get('/search', headers=headers, data=query)
        json_response = result.json
        hits = json_response['hits']
        including_max = False
        including_min = False
        for hit in hits:
            assert hit['scope_of_work']['min'] >= 20
            assert hit['scope_of_work']['max'] <= 80
            if hit['scope_of_work']['max'] == 80:
                including_max = True
            if hit['scope_of_work']['min'] == 20:
                including_min = True

        assert including_min
        assert including_max


@pytest.mark.integration
def test_driving_license():
    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        query = {taxonomy.DRIVING_LICENCE: 'VTK8_WRx_GcM', "limit": 100}
        result = testclient.get('/search', headers=headers, data=query)
        json_response = result.json
        hits = json_response['hits']
        including_max = False
        including_min = False
        for hit in hits:
            concept_ids = [item['concept_id'] for item in hit[fields.DRIVING_LICENCE]]
            assert 'VTK8_WRx_GcM' in concept_ids


@pytest.mark.integration
def test_employment_type():
    _fetch_and_validate_result({taxonomy.EMPLOYMENT_TYPE: 'PFZr_Syz_cUq'},
                               [fields.EMPLOYMENT_TYPE+".concept_id"], ['PFZr_Syz_cUq'])


@pytest.mark.integration
def test_experience():
    _fetch_and_validate_result({search_settings.EXPERIENCE_REQUIRED: 'true'},
                               [fields.EXPERIENCE_REQUIRED], [True])
    _fetch_and_validate_result({search_settings.EXPERIENCE_REQUIRED: 'false'},
                               [fields.EXPERIENCE_REQUIRED], [False])

@pytest.mark.integration
def test_region():
    _fetch_and_validate_result({taxonomy.REGION: '01'},
                               [fields.WORKPLACE_ADDRESS_REGION_CODE], ['01'])
    _fetch_and_validate_result({taxonomy.REGION: '-01'},
                               [fields.WORKPLACE_ADDRESS_REGION_CODE], ['01'], False)


@pytest.mark.integration
def test_country():
    _fetch_and_validate_result({taxonomy.REGION: '199'},
                               [fields.WORKPLACE_ADDRESS_REGION_CODE], ['199'])
    _fetch_and_validate_result({taxonomy.REGION: '-199'},
                               [fields.WORKPLACE_ADDRESS_REGION_CODE], ['199'], False)

if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
