import sys
import json
import pytest

from tests.test_resources.scraped import get_scraped, get_actual_ad_ids, check_ids


@pytest.mark.parametrize("query, expected_ids", [
    ('obstetrix', ['17701']),
    ('tracheostomi', ['3801']),
    ('yrkesbevis', ['32701', '33501']),
    ('körkort',
     ['5901', '32701', '36101', '8401', '14901', '15801', '1201', '2901', '4701', '18101', '22201', '22301', '23401',
      '4301', '19301', '26401', '1301', '6201', '12801', '13201', '15201', '16201', '16801', '30001', '44401', '4101',
      '4501', '12401', '13901', '36001', '45501', '5201', '7701', '32501', '3201', '13001', '13101', '13801', '19601',
      '23501', '28901', '2701', '3101', '12501', '19201', '21901', '29601', '3301', '4801', '11801', '22401', '30401',
      '5501', '26701', '28201', '44901', '49801', '12701', '29001', '33301', '42401', '33601', '29101', '49701',
      '49901', '14701', '27501', '6001', '26101', '27601', '28701', '25801', '35901']
     ),
    ('livsmedel', ['1301', '1201', '20401', '26701']),
    ('livsmedel distributör', ['1301', '1201']),
    (' distributör', ['1301', '1201', '601']),
    ('konsekvensanalyser', ['1']),
])
def test_enrichment_skill(session_scraped, scraped_url, query, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'q': query, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    print_enrichment(actual_ids)
    print_enrichment(expected_ids)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


@pytest.mark.parametrize("query, expected_ids", [
    ('sköterska', [ '15901',  '16701']),
    ('omsorgspersonal', ['14901']),
    ('undersköterska', ['15401', '49601', '48601', '15501', '14801', '46601', '14901', '15601', '19201', '5201']),
    ('undersköterska omsorgspersonal', ['15401', '49601', '48601', '15501', '14801', '46601', '14901', '15601', '19201', '5201']),
    ('skolfotograf', ['12401']),
    ('brandman', ['2701']),
])
def test_enrichment_occupation(session_scraped, scraped_url, query, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'q': query, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    print_enrichment(actual_ids)
    print_enrichment(expected_ids)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


@pytest.mark.parametrize("query, expected_ids", [
    ('lärarutbildning', ['43201']),
    ('datasystem', ['43201']),
    ('undervisning',
     ['8501', '10501', '6301', '7401', '9401', '42601', '7301', '43501', '43701', '8601', '10301', '43601', '7101',
      '43201', '7701', '9301', '9501', '10601', '6101', '7801', '33701', '10701', '6701', '6901', '6401']
     ),
    ('its', ['42801', '6601', '43001', '43201', '43301', '1601', '25901', '25601']),
    ('handledning', ['3901', '6301', '43501', '43701', '16301', '11401', '6901', '3801', '6401']),

    ('introduktionsprogram', ['6301', '34001']),
    ('försäkring', ['301', '2601', '18601', '28101', '35201']),
    ('specialistutbildning', ['16401', '34001', '16001', '19901', '17801']),

])
def test_enrichment_skills(session_scraped, scraped_url, query, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'q': query, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    print_enrichment(actual_ids)
    print_enrichment(expected_ids)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


def print_enrichment(list_of_ids):
    from tests.api_tests.scraped_ads.test_static_data_file import test_enrichment
    test_enrichment(list_of_ids)
