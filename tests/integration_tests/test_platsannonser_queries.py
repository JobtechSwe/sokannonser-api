import sys
import os
import pytest
from pprint import pprint
from sokannonser import app
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


def _fetch_and_validate_result(query, field, expected):
    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers,
                                data=query)
        json_response = result.json
        hits = json_response['hits']
        for hit in hits:
            assert _get_nested_value(field, hit) == expected


@pytest.mark.integration
def test_driving_license_required():
    _fetch_and_validate_result({taxonomy.DRIVING_LICENCE_REQUIRED: 'true'},
                               fields.DRIVING_LICENCE_REQUIRED, True)
    _fetch_and_validate_result({taxonomy.DRIVING_LICENCE_REQUIRED: 'false'},
                               fields.DRIVING_LICENCE_REQUIRED, False)


@pytest.mark.parametrize("field, path, query, expected", [(taxonomy.OCCUPATION,
                                                           fields.OCCUPATION+".concept_id",
                                                           "D7Ns_RG6_hD2",
                                                           "D7Ns_RG6_hD2"),
                                                          (taxonomy.GROUP,
                                                           fields.OCCUPATION_GROUP+".concept_id",
                                                           "DJh5_yyF_hEM",
                                                           "DJh5_yyF_hEM"),
                                                          (taxonomy.FIELD,
                                                           fields.OCCUPATION_FIELD+".concept_id",
                                                           "apaJ_2ja_LuF",
                                                           "apaJ_2ja_LuF"),
                                                          (taxonomy.OCCUPATION,
                                                           fields.OCCUPATION+".legacy_ams_taxonomy_id",
                                                           "D7Ns_RG6_hD2",
                                                           "2419"),
                                                          (taxonomy.GROUP,
                                                           fields.OCCUPATION_GROUP+".concept_id",
                                                           "2512",
                                                           "DJh5_yyF_hEM"),
                                                          (taxonomy.FIELD,
                                                           fields.OCCUPATION_FIELD+".legacy_ams_taxonomy_id",
                                                           "3",
                                                           "3")
                                                          ])
@pytest.mark.integration
def test_occupation_codes(field, path, query, expected):
    _fetch_and_validate_result({field: query}, path, expected)


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
