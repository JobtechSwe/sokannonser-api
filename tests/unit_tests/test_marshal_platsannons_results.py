import os
import sys
import time
from operator import itemgetter
import json

import pytest
from sokannonser.rest.endpoint.platsannonser import Search
from sokannonser import settings
from sokannonser.repository.querybuilder import QueryBuilder
from sokannonser.repository.platsannonser import transform_platsannons_query_result
from tests.unit_tests.test_resources import mock_for_querybuilder_tests as mock

currentdir = os.path.dirname(os.path.realpath(__file__)) + '/'


def get_static_ads_from_file():
    with open(currentdir + 'test_resources/platsannons_results_eng.json') as f:
        return json.load(f)


@pytest.mark.unit
def test_properties_and_types_marshal_mocked_elastic_result():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    esresult = get_static_ads_from_file()

    args = {settings.FREETEXT_QUERY: False, settings.STATISTICS: False}

    pbsearch = Search()
    querybuilder = QueryBuilder(mock.MockTextToConcept)

    query_result = transform_platsannons_query_result(args, esresult, querybuilder)
    query_hits = [hit['_source'] for hit in query_result.get('hits', [])]
    sorted_query_hits = sorted(query_hits, key=itemgetter('id'), reverse=False)

    start_time = int(round(time.time() * 1000)) - 1000

    results = pbsearch.marshal_results(query_result, sorted_query_hits, start_time)
    assert_is_type(results, dict)

    assert_has_properties(results,
                          ['hits', 'positions', 'query_time_in_millis',
                           'result_time_in_millis', 'stats', 'total'])

    results_hits = results['hits']
    assert_is_type(results_hits, list)
    assert len(results_hits) > 0

    test_hit = results_hits[0]
    assert test_hit is not None

    assert_is_type(test_hit, dict)
    assert_has_properties(test_hit, ['application_details', 'employment_type',
                                     'number_of_vacancies',
                                     'employer', 'scope_of_work', 'workplace_id',
                                     'workplace_address', 'working_hours_type',
                                     'description',
                                     'access_to_own_car', 'experience_required', 'id',
                                     'source_type', 'keywords',
                                     'driving_license_required', 'must_have',
                                     'salary_type', 'nice_to_have', 'publication_date',
                                     'headline', 'application_deadline',
                                     'access', 'duration',
                                     'occupation_group', 'occupation_field',
                                     'occupation'])

    assert_is_type(test_hit['application_details'], dict)
    assert_has_properties(test_hit['application_details'],
                          ['information', 'reference', 'email', 'via_af', 'url', 'other'])

    assert_is_type(test_hit['employment_type'], dict)
    assert_has_properties(test_hit['employment_type'], ['concept_id', 'label',
                                                        'legacy_ams_taxonomy_id'])

    assert_is_type(test_hit['number_of_vacancies'], int)

    assert_is_type(test_hit['employer'], dict)
    assert_has_properties(test_hit['employer'],
                          ['id', 'phone_number', 'email', 'url', 'organization_number',
                           'name', 'workplace'])

    assert_is_type(test_hit['scope_of_work'], dict)
    assert_has_properties(test_hit['scope_of_work'], ['min', 'max'])


@pytest.mark.unit
def test_values_marshal_mocked_elastic_result():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    esresult = get_static_ads_from_file()

    args = {settings.FREETEXT_QUERY: False, settings.STATISTICS: False}

    pbsearch = Search()
    querybuilder = QueryBuilder(mock.MockTextToConcept)

    query_result = transform_platsannons_query_result(args, esresult, querybuilder)
    query_hits = [hit['_source'] for hit in query_result.get('hits', [])]
    sorted_query_hits = sorted(query_hits, key=itemgetter('id'), reverse=False)

    start_time = int(round(time.time() * 1000)) - 1000
    results = pbsearch.marshal_results(query_result, sorted_query_hits, start_time)

    results_hits = results['hits']
    assert_is_type(results_hits, list)
    assert len(results_hits) > 0

    ad_id = '23174210'

    test_hit = [hit for hit in results_hits if hit['id'] == ad_id][0]
    assert test_hit is not None
    assert sorted_query_hits[0]['id'] == test_hit['id']

    ansokningsdetaljer = test_hit['application_details']
    # 'information', 'reference', 'email', 'via_af', 'url', 'other'
    assert_has_str_value(ansokningsdetaljer['information'])
    assert_has_str_value(ansokningsdetaljer['reference'])
    assert_has_str_value(ansokningsdetaljer['email'])
    assert_has_str_value(ansokningsdetaljer['url'])
    assert_has_bool_value(ansokningsdetaljer['via_af'], False)
    assert_has_str_value(ansokningsdetaljer['other'])

    assert_has_bool_value(test_hit['experience_required'], True)
    assert_has_bool_value(test_hit['access_to_own_car'], False)
    assert_has_bool_value(test_hit['driving_license_required'], True)

    anstallningstyp = test_hit['employment_type']
    assert_has_taxonomy_values(anstallningstyp)

    assert_has_int_value(test_hit['number_of_vacancies'], 1)

    arbetsgivare = test_hit['employer']
    # ['id', 'phone_number', 'email', 'url', 'organization_number', 'name', 'workplace'])
    assert_has_str_value(arbetsgivare['id'])
    assert_has_str_value(arbetsgivare['workplace'])
    assert_has_str_value(arbetsgivare['email'])
    assert_has_str_value(arbetsgivare['name'])
    assert_has_str_value(arbetsgivare['organization_number'])
    assert_has_str_value(arbetsgivare['phone_number'])
    assert_has_str_value(arbetsgivare['url'])

    arbetsomfattning = test_hit['scope_of_work']
    assert_has_int_value(arbetsomfattning['min'], 100)
    assert_has_int_value(arbetsomfattning['max'], 100)

    assert_has_str_value(test_hit['workplace_id'])

    arbetsplatsadress = test_hit['workplace_address']

    assert_has_list_values(arbetsplatsadress['coordinates'])
    assert_has_str_value(arbetsplatsadress['street_address'])
    assert_has_str_value(arbetsplatsadress['municipality'])
    assert_has_str_value(arbetsplatsadress['municipality_code'])
    assert_has_str_value(arbetsplatsadress['region'])
    assert_has_str_value(arbetsplatsadress['region_code'])
    assert_has_str_value(arbetsplatsadress['country'])
    assert_has_str_value(arbetsplatsadress['country_code'])
    assert_has_str_value(arbetsplatsadress['postcode'])
    assert_has_str_value(arbetsplatsadress['city'])

    assert_has_taxonomy_values(test_hit['working_hours_type'])
    assert_has_taxonomy_values(test_hit['employment_type'])
    assert_has_taxonomy_values(test_hit['salary_type'])
    assert_has_taxonomy_values(test_hit['duration'])
    assert_has_taxonomy_values(test_hit['occupation'])
    assert_has_taxonomy_values(test_hit['occupation_group'])
    assert_has_taxonomy_values(test_hit['occupation_field'])

    beskrivning = test_hit['description']
    assert_has_str_value(beskrivning['text'])
    assert_has_str_value(beskrivning['needs'])
    assert_has_str_value(beskrivning['company_information'])
    assert_has_str_value(beskrivning['requirements'])
    assert_has_str_value(beskrivning['conditions'])

    assert_has_int_value(int(test_hit['id']), 23174210)

    assert_has_str_value(test_hit['source_type'])

    keywords = test_hit['keywords']['extracted']
    assert_has_list_values(keywords['location'])
    assert_has_list_values(keywords['occupation'])
    assert_has_list_values(keywords['skill'])

    krav = test_hit['must_have']
    assert_has_taxonomy_list_values(krav['skills'])
    assert_has_taxonomy_list_values(krav['languages'])
    assert_has_taxonomy_list_values(krav['work_experiences'])

    lonetyp = test_hit['salary_type']
    assert_has_taxonomy_values(lonetyp)

    meriterande = test_hit['nice_to_have']
    assert_has_taxonomy_list_values(meriterande['skills'])
    assert_has_taxonomy_list_values(meriterande['languages'])
    assert_has_taxonomy_list_values(meriterande['work_experiences'])
    assert_has_str_value(test_hit['publication_date'])
    assert_has_str_value(test_hit['headline'])
    assert_has_str_value(test_hit['application_deadline'])
    assert_has_bool_value(test_hit['removed'], False)
    assert_has_str_value(test_hit['last_publication_date'])
    assert_has_str_value(test_hit['access'])
    assert_has_int_value(test_hit['timestamp'], 1552410521222)


def assert_has_taxonomy_list_values(listitems):
    assert_is_type(listitems, list)
    assert_has_list_values(listitems)
    for item in listitems:
        assert_has_taxonomy_values(item)


def assert_is_type(value_to_check, wanted_type):
    assert wanted_type == type(value_to_check)


def assert_has_properties(value_to_check, wanted_propertynames):
    for name in wanted_propertynames:
        assert name in value_to_check


def assert_has_str_value(value_to_check):
    assert type(value_to_check) == str
    assert len(value_to_check) > 0


def assert_has_bool_value(value_to_check, wanted_bool):
    assert type(value_to_check) == bool
    assert value_to_check == wanted_bool


def assert_has_int_value(value_to_check, wanted_int):
    assert type(value_to_check) == int
    assert value_to_check == wanted_int


def assert_has_list_values(value_to_check):
    assert type(value_to_check) == list
    assert len(value_to_check) > 0


def assert_has_taxonomy_values(hit_attr):
    assert_has_str_value(hit_attr['concept_id'])
    assert_has_str_value(hit_attr['label'])
    assert_has_str_value(hit_attr['legacy_ams_taxonomy_id'])
