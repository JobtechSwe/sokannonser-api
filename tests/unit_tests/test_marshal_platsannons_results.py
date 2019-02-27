import os
import sys
import time
from operator import itemgetter
# from pprint import pprint
import json

import pytest
from sokannonser.rest.endpoint.platsannonser import PBSearch
from sokannonser import settings
from sokannonser.repository.querybuilder import QueryBuilder
from sokannonser.repository.platsannonser import transform_platsannons_query_result

currentdir = os.path.dirname(os.path.realpath(__file__)) + '/'


def get_static_ads_from_file():
    with open(currentdir + 'test_resources/platsannons_results.json') as f:
        result = json.load(f)
        # pprint(result)

        return result


@pytest.mark.unit
def test_properties_and_types_marshal_mocked_elastic_result():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    esresult = get_static_ads_from_file()
    # pprint(esresult)

    args = {settings.FREETEXT_QUERY: False, settings.STATISTICS: False}

    pbsearch = PBSearch()
    querybuilder = QueryBuilder()

    query_result = transform_platsannons_query_result(args, esresult, querybuilder)
    query_hits = [hit['_source'] for hit in query_result.get('hits', [])]
    sorted_query_hits = sorted(query_hits, key=itemgetter('id'), reverse=False)

    start_time = int(round(time.time() * 1000)) - 1000

    results = pbsearch.marshal_results(query_result, sorted_query_hits, start_time)
    assert_is_type(results, dict)
    # pprint(results)

    assert_has_properties(results,
                          ['hits', 'positions', 'query_time_in_millis', 'result_time_in_millis', 'stats', 'total'])

    results_hits = results['hits']
    assert_is_type(results_hits, list)
    assert len(results_hits) > 0

    # test_hit = None
    # for hit in results_hits:
    #     # print(hit['id'])
    #     if hit['id'] == 8127938:
    #         test_hit = hit
    test_hit = results_hits[0]

    # pprint(test_hit)

    assert test_hit is not None

    assert_is_type(test_hit, dict)
    assert_has_properties(test_hit, ['ansokningsdetaljer', 'anstallningstyp', 'antal_platser',
                                     'arbetsgivare', 'arbetsomfattning', 'arbetsplats_id',
                                     'arbetsplatsadress', 'arbetstidstyp', 'beskrivning',
                                     'egen_bil', 'erfarenhet_kravs', 'id',
                                     'kalla', 'keywords', 'keywords_enriched_binary',
                                     'korkort_kravs', 'krav',
                                     'lonetyp', 'meriterande', 'publiceringsdatum',
                                     'publiceringskanaler', 'rubrik', 'sista_ansokningsdatum',
                                     'status', 'tilltrade', 'varaktighet',
                                     'yrkesgrupp', 'yrkesomrade', 'yrkesroll'])

    assert_is_type(test_hit['ansokningsdetaljer'], dict)
    assert_has_properties(test_hit['ansokningsdetaljer'],
                          ['annat', 'epost', 'information', 'referens', 'via_af', 'webbadress'])

    assert_is_type(test_hit['anstallningstyp'], dict)
    assert_has_properties(test_hit['anstallningstyp'], ['kod', 'taxonomi-kod', 'term'])

    assert_is_type(test_hit['antal_platser'], int)

    assert_is_type(test_hit['arbetsgivare'], dict)
    assert_has_properties(test_hit['arbetsgivare'],
                          ['arbetsplats', 'epost', 'id', 'namn', 'organisationsnummer', 'telefonnummer', 'webbadress'])

    assert_is_type(test_hit['arbetsomfattning'], dict)
    assert_has_properties(test_hit['arbetsomfattning'], ['min', 'max'])


@pytest.mark.unit
def test_values_marshal_mocked_elastic_result():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    esresult = get_static_ads_from_file()
    # pprint(esresult)

    args = {settings.FREETEXT_QUERY: False, settings.STATISTICS: False}

    pbsearch = PBSearch()
    querybuilder = QueryBuilder()

    query_result = transform_platsannons_query_result(args, esresult, querybuilder)
    query_hits = [hit['_source'] for hit in query_result.get('hits', [])]
    sorted_query_hits = sorted(query_hits, key=itemgetter('id'), reverse=False)
    # pprint(sorted_query_hits)
    # print('sorted_query_hits[0][id]:', sorted_query_hits[0]['id'])

    start_time = int(round(time.time() * 1000)) - 1000

    results = pbsearch.marshal_results(query_result, sorted_query_hits, start_time)
    # pprint(results)

    results_hits = results['hits']
    assert_is_type(results_hits, list)
    assert len(results_hits) > 0

    test_hit = results_hits[0]
    # pprint(test_hit)

    assert test_hit is not None
    # print('test_hit[id]', test_hit['id'])
    assert sorted_query_hits[0]['id'] == test_hit['id']

    ansokningsdetaljer = test_hit['ansokningsdetaljer']
    assert_has_str_value(ansokningsdetaljer['annat'])
    assert_has_str_value(ansokningsdetaljer['epost'])
    assert_has_str_value(ansokningsdetaljer['information'])
    assert_has_str_value(ansokningsdetaljer['referens'])
    assert_has_bool_value(ansokningsdetaljer['via_af'], False)
    assert_has_str_value(ansokningsdetaljer['webbadress'])

    anstallningstyp = test_hit['anstallningstyp']
    assert_has_taxonomy_values(anstallningstyp)

    assert_has_int_value(test_hit['antal_platser'], 1)

    arbetsgivare = test_hit['arbetsgivare']
    assert_has_str_value(arbetsgivare['arbetsplats'])
    assert_has_str_value(arbetsgivare['epost'])
    assert_has_str_value(arbetsgivare['id'])
    assert_has_str_value(arbetsgivare['namn'])
    assert_has_str_value(arbetsgivare['organisationsnummer'])
    assert_has_str_value(arbetsgivare['telefonnummer'])
    assert_has_str_value(arbetsgivare['webbadress'])

    arbetsomfattning = test_hit['arbetsomfattning']
    assert_has_int_value(arbetsomfattning['min'], 100)
    assert_has_int_value(arbetsomfattning['max'], 100)

    assert_has_str_value(test_hit['arbetsplats_id'])

    arbetsplatsadress = test_hit['arbetsplatsadress']

    assert_has_list_values(arbetsplatsadress['coordinates'])
    assert_has_str_value(arbetsplatsadress['gatuadress'])
    assert_has_str_value(arbetsplatsadress['kommun'])
    assert_has_str_value(arbetsplatsadress['kommunkod'])
    assert_has_str_value(arbetsplatsadress['lan'])
    assert_has_str_value(arbetsplatsadress['land'])
    assert_has_str_value(arbetsplatsadress['landskod'])
    assert_has_str_value(arbetsplatsadress['postnummer'])
    assert_has_str_value(arbetsplatsadress['postort'])

    arbetstidstyp = test_hit['arbetstidstyp']
    assert_has_taxonomy_values(arbetstidstyp)

    beskrivning = test_hit['beskrivning']
    assert_has_str_value(beskrivning['annonstext'])
    assert_has_str_value(beskrivning['behov'])
    assert_has_str_value(beskrivning['information'])
    assert_has_str_value(beskrivning['krav'])
    assert_has_str_value(beskrivning['villkor'])

    assert_has_bool_value(test_hit['egen_bil'], True)
    assert_has_bool_value(test_hit['erfarenhet_kravs'], True)

    assert_has_int_value(test_hit['id'], 8052385)

    assert_has_str_value(test_hit['kalla'])

    keywords = test_hit['keywords']
    assert_has_list_values(keywords['location'])
    assert_has_list_values(keywords['occupation'])
    assert_has_list_values(keywords['skill'])

    keywords_enriched_binary = test_hit['keywords_enriched_binary']
    assert_has_list_values(keywords_enriched_binary['occupation'])
    assert_has_list_values(keywords_enriched_binary['skill'])
    assert_has_list_values(keywords_enriched_binary['trait'])

    assert_has_bool_value(test_hit['korkort_kravs'], True)

    krav = test_hit['krav']
    assert_has_taxonomy_list_values(krav['kompetenser'])
    assert_has_taxonomy_list_values(krav['sprak'])
    assert_has_taxonomy_list_values(krav['utbildningsinriktning'])
    assert_has_taxonomy_list_values(krav['utbildningsniva'])
    assert_has_taxonomy_list_values(krav['yrkeserfarenheter'])

    lonetyp = test_hit['lonetyp']
    assert_has_taxonomy_values(lonetyp)

    meriterande = test_hit['meriterande']
    assert_has_taxonomy_list_values(meriterande['kompetenser'])
    assert_has_taxonomy_list_values(meriterande['sprak'])
    assert_has_taxonomy_list_values(meriterande['utbildningsinriktning'])
    assert_has_taxonomy_list_values(meriterande['utbildningsniva'])
    assert_has_taxonomy_list_values(meriterande['yrkeserfarenheter'])

    assert_has_str_value(test_hit['publiceringsdatum'])

    publiceringskanaler = test_hit['publiceringskanaler']

    assert_has_bool_value(publiceringskanaler['ais'], True)
    assert_has_bool_value(publiceringskanaler['platsbanken'], True)
    assert_has_bool_value(publiceringskanaler['platsjournalen'], True)

    assert_has_str_value(test_hit['rubrik'])

    assert_has_str_value(test_hit['sista_ansokningsdatum'])

    status = test_hit['status']

    assert_has_str_value(status['anvandarId'])
    assert_has_bool_value(status['publicerad'], False)
    assert_has_str_value(status['sista_publiceringsdatum'])
    assert_has_str_value(status['skapad'])
    assert_has_str_value(status['skapad_av'])
    assert_has_str_value(status['uppdaterad'])
    assert_has_str_value(status['uppdaterad_av'])

    assert_has_str_value(test_hit['tilltrade'])

    assert_has_int_value(test_hit['timestamp'], 1550579758889)

    assert_has_taxonomy_values(test_hit['varaktighet'])
    assert_has_taxonomy_values(test_hit['yrkesgrupp'])
    assert_has_taxonomy_values(test_hit['yrkesomrade'])
    assert_has_taxonomy_values(test_hit['yrkesroll'])


def assert_has_taxonomy_list_values(listitems):
    assert_is_type(listitems, list)
    assert_has_list_values(listitems)
    for item in listitems:
        assert_has_taxonomy_values(item)


def assert_is_type(value_to_check, wanted_type):
    # print('value: %s, type: %s, wanted_type: %s' % (value_to_check, type(value_to_check), wanted_type))
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
    assert_has_str_value(hit_attr['kod'])
    assert_has_str_value(hit_attr['taxonomi-kod'])
    assert_has_str_value(hit_attr['term'])
