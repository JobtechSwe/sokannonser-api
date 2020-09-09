import sys
import pytest
from tests.test_resources.scraped import get_scraped, check_required_ad_fields_not_none, check_ids, get_actual_ad_ids


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.parametrize("query, expected_ids", [
    ('barnmorska', [19769, 43643, 19764, 43645, 19765, 43655]),
    ('tandsköterska', [14662, 14171, 45671, 49580]),
    ('Sjuksköterskor',
     [17507, 43518, 17901, 43507, 18944, 43636, 16674, 43619, 18921, 43281, 18924, 43280, 18922, 43278, 17136, 43605,
      17181]),
    ('Sjuksköterska',
     [18924, 43280, 18922, 43278, 43619, 18921, 43281, 17136, 43605, 17181, 17507, 43518, 17901, 43507, 43636, 18944,
      16674, 16393, 43621]),

])
def test_freetext_query(session_scraped, scraped_url, query, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'q': query, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


@pytest.mark.smoke
@pytest.mark.integration
def test_freetext_query_check_fields(session_scraped, scraped_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_scraped(session_scraped, scraped_url, params={'limit': '100'})
    expected_number = 100
    assert json_response['total']['value'] == expected_number
    assert len(json_response['hits']) == expected_number

    for hit in json_response['hits']:
        check_required_ad_fields_not_none(hit)
        print(hit['headline'])



@pytest.mark.parametrize("query, expected_ids", [
    ('barnmorska tandsköterska', [45671, 14662, 19769, 43643, 19764, 43645, 19765, 43655, 14171, 49580]),  # 49580 missing
    ('tandsköterska barnmorska', [45671, 14662, 19769, 43643, 19764, 43645, 19765, 43655, 14171, 49580]),  # 49580 missing
    ('barnmorska', [19769, 43643, 19764, 43645, 19765, 43655]),
    ('tandsköterska', [14662, 14171, 45671, 49580]),
    ('lärare', [10709, 10710, 46507, 46503, 47157, 47325, 46807]),
    ('kock', [20208, 20352]),
    ('lärare kock', [20208, 20352, 10709, 10710, 46507, 46503, 47157, 47325, 46807]),
    ('engineer', [24209, 24067, 24968, 24234, 49736]),
    ('developer', [24773, 25031, 25088, 49954]),
    ('developer engineer', [24773, 25031, 25088, 49954,24209, 24067, 24968, 24234, 49736]),
    ('engineer developer', [24773, 25031, 25088, 49954,24209, 24067, 24968, 24234, 49736]),
    ('engineer developer kock', [24773, 25031, 25088, 49954,24209, 24067, 24968, 24234, 49736, 20208, 20352]),  # zero hits
    ('Umeå', [2261, 46272, 45671, 22148]),
    ('Harstena', [20352, 19927]),
    ('Harstena Umeå', [20352, 19927, 2261, 46272, 45671, 22148]), # zero hits
    ('Harstena sjuksköterska', [20352, 19927, 18924, 43280, 18922, 43278, 43619, 18921, 43281, 17136, 43605, 17181, 17507, 43518, 17901, 43507, 43636, 18944,
      16674, 16393, 43621]), # zero hits
    ('sjuksköterskor', [17507, 43518, 17901, 43507, 18944, 43636, 16674, 43619, 18921, 43281, 18924, 43280, 18922, 43278, 17136, 43605, 17181]),
    ('Uppsala', [19433, 43653, 17507, 43518, 19765, 43655, 17901, 43507]),
    ('sjuksköterskor Uppsala', [19433, 43653, 17507, 43518, 19765, 43655, 17901, 43507, 17507, 43518, 17901, 43507, 18944, 43636, 16674, 43619, 18921, 43281, 18924, 43280, 18922, 43278, 17136, 43605, 17181]),

])
def test_freetext_query_multiple_search_terms(session_scraped, scraped_url, query, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_scraped(session_scraped, scraped_url, params={'q': query, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    print(actual_ids)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


"""
   49580 is included in a search for 'tandsköterska' but not in a search for 'barnmorska tandsköterska'
   {'id': 49580, 'external_id': '8b75fd20-2429-4d84-a85d-6bc102a2549c',
                                  'webpage_url': 'https://www.offentligajobb.se/jobad/tandsk%c3%b6terska-till-specialisttandv%c3%a5rden-%c3%b6stersund-avd-f%c3%b6r-ortodonti_%c3%b6stersund-j%c3%a4mtlands-l%c3%a4n-sverige_8b75fd20-2429-4d84-a85d-6bc102a2549c',
                                  'headline': 'Tandsköterska till Specialisttandvården Östersund, Avd. för ortodonti',
                                  'workplace_address': {'municipality_concept_id': 'Vt7P_856_WZS',
                                                        'municipality': 'Östersund',
                                                        'region_concept_id': '65Ms_7r1_RTG', 'region': 'Jämtlands län',
                                                        'country_concept_id': 'i46j_HmG_v64', 'country': 'Sverige'},
                                  'occupation': {'label': None, 'concept_id': None},
                                  'occupation_group': {'label': None, 'concept_id': None},
                                  'occupation_field': {'label': None, 'concept_id': None}, 'sameAs': '',
                                  'hashsum': 'A1RGeQAS8gQwHifChy4=CMOBVMOkAMOkwoxWAcODEMKkBDzCksOfCcKewrTDsA+6d71c31c6b1af361e90beb534666a0a6'}
"""
