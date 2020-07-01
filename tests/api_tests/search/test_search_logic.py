import sys
import json
import pytest

from tests.test_resources.concept_ids import concept_ids_geo as geo
from tests.test_resources.helper import get_search_check_number_of_results, check_freetext_concepts
from tests.test_resources.settings import TEST_USE_STATIC_DATA


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.integration
@pytest.mark.parametrize("query, municipality, code, municipality_concept_id, expected_number_of_hits", [
    ('bagare stockholm', 'Stockholm', '0180', geo.stockholm, 3),
    ('lärare stockholm', 'Stockholm', '0180', geo.stockholm, 4),
    ('lärare göteborg', 'Göteborg', '1480', geo.goteborg, 4),
])
def test_freetext_work_and_location_details(session, search_url, query, municipality, code, municipality_concept_id,
                                            expected_number_of_hits):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    params = {'q': query, 'limit': '100'}
    response = get_search_check_number_of_results(session, search_url, expected_number_of_hits, params)
    response_json = json.loads(response.content.decode('utf8'))

    for ad in response_json['hits']:
        print(ad)
        assert ad['workplace_address']['municipality'] == municipality
        assert ad['workplace_address']['municipality_code'] == code
        assert ad['workplace_address']['municipality_concept_id'] == municipality_concept_id


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.parametrize("query, expected_ids_and_relevance", [
    ('bagare kock Stockholm Göteborg', [
        ('23780773', 1.0),
        ('23578307', 1.0),
        ('23762170', 1.0),
        ('23934411', 0.8918585379117067),  # 0.8918585379117067
        ('23918920', 0.8918585379117067),  # Old: 0.8918781594454271
        ('23978318', 0.7669555993474402),
        ('23826966', 0.7669555993474402),
        ('23566906', 0.7669555993474402),
        ('23552714', 0.7669555993474402),
        ('23502782', 0.7669555993474402),
        ('23451218', 0.7669555993474402),
        ('23981076', 0.45275073813570443),
        ('23978439', 0.45275073813570443),
        ('23550781', 0.45275073813570443)
    ])])
def test_freetext_two_work_and_two_locations_check_order(session, search_url, query, expected_ids_and_relevance):
    """
    Tests that the sorting order of hits is as expected and that relevance value has not changed
    This documents current behavior
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')

    params = {'q': query, 'limit': '100'}
    response = get_search_check_number_of_results(session, search_url, len(expected_ids_and_relevance), params)
    response_json = json.loads(response.content.decode('utf8'))
    old_relevance = 1
    for index, hit in enumerate(response_json['hits']):
        relevance = hit['relevance']
        assert old_relevance >= relevance  # check that results are presented in ascending relevance order
        assert hit['id'] == expected_ids_and_relevance[index][0]
        assert hit['relevance'] == expected_ids_and_relevance[index][1], hit['id']
        old_relevance = relevance


@pytest.mark.parametrize("query, top_id, expected_number_of_hits", [
    ('bagare kock Stockholm Göteborg', '23780773', 14),
    ('kock bagare Stockholm Göteborg', '23780773', 14),
    ('kallskänka kock Stockholm Göteborg', '23552714', 12),
    ('lärare lågstadielärare Malmö Göteborg', '23981080', 5),
])
def test_freetext_two_work_and_two_locations(session, search_url, query, top_id, expected_number_of_hits):
    """
    Test that the top hit for a search has not changed and that the number of hits for query has not changed
    This documents current behavior
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')

    params = {'q': query, 'limit': '100'}
    response = get_search_check_number_of_results(session, search_url, expected_number_of_hits, params)
    response_json = json.loads(response.content.decode('utf8'))
    if TEST_USE_STATIC_DATA:
        assert response_json['hits'][0]['id'] == top_id


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.integration
@pytest.mark.parametrize("query, expected_id", [
    ('Bauhaus Kundtjänst', '23783146'),
    ('Sirius crew', '10537882'),
    ('super', '23801747'),
    ('Säsongande', '23437355'),
    ('Diskretessen', '23396767'),
])
def test_freetext_search(session, search_url, query, expected_id):
    """
    Tests from examples
    Test that specific queries should return only one hit (identified by id)
    and that freetext concepts are not included in search result
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')
    params = {'q': query, 'limit': '100'}
    response = get_search_check_number_of_results(session, search_url, expected_number=1, params=params)
    response_json = json.loads(response.content.decode('utf8'))
    # freetext concepts should be empty
    check_freetext_concepts(response_json['freetext_concepts'], [[], [], [], [], [], [], [], [], []])
    if TEST_USE_STATIC_DATA:
        assert response_json['hits'][0]['id'] == expected_id


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
def test_search_rules(session, search_url):
    params = {'q': "systemutvecklare python java stockholm blocket", 'limit': '100'}
    response = get_search_check_number_of_results(session, search_url, expected_number=1, params=params)
    response_json = json.loads(response.content.decode('utf8'))
    hit = response_json['hits'][0]
    check_freetext_concepts(response_json['freetext_concepts'], [
        ['python', 'java'], ['systemutvecklare'], ['stockholm'], [], [], [], [], [], []
    ])
    assert 'blocket' in hit['headline'].lower()
    assert 'blocket' in hit['employer']['name'].lower()
    assert 'blocket' in hit['employer']['workplace'].lower()
    assert 'systemutvecklare' in hit['occupation']['label'].lower()
    assert 'stockholm' in hit['description']['text'].lower()
    assert 'stockholm' in hit['workplace_address']['municipality'].lower()
