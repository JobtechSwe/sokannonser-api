import sys
import json
import pytest

from tests.integration_tests.test_resources.concept_ids import concept_ids_geo as geo
from tests.integration_tests.test_resources.helper import get_search_check_number_of_results


@pytest.mark.integration
@pytest.mark.parametrize("query, municipality, code, municipality_concept_id, expected_number_of_hits", [
    ('bagare stockholm', 'Stockholm', '0180', geo.stockholm, 3),
    ('lärare stockholm', 'Stockholm', '0180', geo.stockholm, 4),
    ('lärare göteborg', 'Göteborg', '1480', geo.goteborg, 4),
])
def test_freetext_work_and_location_details(session, url, query, municipality, code, municipality_concept_id,
                                            expected_number_of_hits):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    params = {'q': query, 'limit': '100'}
    response = get_search_check_number_of_results(session, url, expected_number_of_hits, params)
    response_json = json.loads(response.content.decode('utf8'))

    for ad in response_json['hits']:
        assert ad['workplace_address']['municipality'] == municipality
        assert ad['workplace_address']['municipality_code'] == code
        assert ad['workplace_address']['municipality_concept_id'] == municipality_concept_id


@pytest.mark.parametrize("query, expected_ids_and_relevance", [
    ('bagare kock Stockholm Göteborg',
     [('23780773', 1.0), ('23578307', 1.0), ('23762170', 1.0), ('23934411', 0.897897309155177),
      ('23918920', 0.897897309155177), ('23783846', 0.8949498104298874), ('23978318', 0.7716591497509147),
      ('23826966', 0.7716591497509147), ('23566906', 0.7716591497509147), ('23552714', 0.7716591497509147),
      ('23502782', 0.7716591497509147), ('23451218', 0.7716591497509147), ('23981076', 0.45415871049258943),
      ('23978439', 0.45415871049258943), ('23550781', 0.45415871049258943),
      ])])
def test_freetext_two_work_and_two_locations_check_order(session, url, query, expected_ids_and_relevance):
    """
    Tests that the sorting order of hits is as expected and that relevance value has not changed
    This documents current behavior
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')

    params = {'q': query, 'limit': '100'}
    response = get_search_check_number_of_results(session, url, len(expected_ids_and_relevance), params)
    response_json = json.loads(response.content.decode('utf8'))
    old_relevance = 1
    for index, hit in enumerate(response_json['hits']):
        relevance = hit['relevance']
        assert old_relevance >= relevance
        assert hit['id'] == expected_ids_and_relevance[index][0]
        assert hit['relevance'] == expected_ids_and_relevance[index][1]
        old_relevance = relevance


@pytest.mark.parametrize("query, top_id, expected_number_of_hits", [
    ('bagare kock Stockholm Göteborg', '23780773', 15),
    ('kock bagare Stockholm Göteborg', '23780773', 15),
    ('kallskänka kock Stockholm Göteborg', '23552714', 13),
    ('lärare lågstadielärare Malmö Göteborg', '23981080', 5),
])
def test_freetext_two_work_and_two_locations(session, url, query, top_id, expected_number_of_hits):
    """
    Test that the top hit for a search has not changed and that the number of hits for query has not changed
    This documents current behavior
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')

    params = {'q': query, 'limit': '100'}
    response = get_search_check_number_of_results(session, url, expected_number_of_hits, params)
    response_json = json.loads(response.content.decode('utf8'))

    assert response_json['hits'][0]['id'] == top_id


@pytest.mark.integration
@pytest.mark.parametrize("query, expected_id", [
    ('Bauhaus Kundtjänst', '23783146'),
    ('Sirius crew', '10537882'),
    ('super', '23801747'),
    ('Säsongande', '23437355'),
    ('Diskretessen', '23396767'),
])
def test_freetext_search(session, url, query, expected_id):
    """
    Tests from examples
    Test that specific queries should return only one hit (identified by id)
    and that freetext concepts are not included in search result
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')
    params = {'q': query, 'limit': '100'}
    response = get_search_check_number_of_results(session, url, 1, params)
    response_json = json.loads(response.content.decode('utf8'))

    assert response_json['hits'][0]['id'] == expected_id

    # freetext concepts should be empty
    free_text_concepts = response_json['freetext_concepts']
    assert free_text_concepts['skill'] == []
    assert free_text_concepts['occupation'] == []
    assert free_text_concepts['location'] == []
    assert free_text_concepts['skill_must'] == []
    assert free_text_concepts['occupation_must'] == []
    assert free_text_concepts['location_must'] == []
    assert free_text_concepts['skill_must_not'] == []
    assert free_text_concepts['occupation_must_not'] == []
    assert free_text_concepts['location_must_not'] == []
