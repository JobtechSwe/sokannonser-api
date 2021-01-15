import sys
import json
import pytest

from tests.test_resources.concept_ids import concept_ids_geo as geo
from tests.test_resources.helper import get_search, get_search_check_number_of_results, check_freetext_concepts
from tests.test_resources.settings import TEST_USE_STATIC_DATA


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.integration
@pytest.mark.parametrize("query, municipality, code, municipality_concept_id, expected_number_of_hits", [
    ('bagare stockholm', 'Stockholm', '0180', geo.stockholm, 0),
    ('lärare stockholm', 'Stockholm', '0180', geo.stockholm, 11),
    ('lärare göteborg', 'Göteborg', '1480', geo.goteborg, 6),
])
def test_freetext_work_and_location_details(session, query, municipality, code, municipality_concept_id,
                                            expected_number_of_hits):
    params = {'q': query, 'limit': '100'}
    response = get_search_check_number_of_results(session, expected_number_of_hits, params)
    response_json = json.loads(response.content.decode('utf8'))

    for ad in response_json['hits']:
        print(ad['id'])
        assert ad['workplace_address']['municipality'] == municipality
        assert ad['workplace_address']['municipality_code'] == code
        assert ad['workplace_address']['municipality_concept_id'] == municipality_concept_id


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.parametrize("query, expected_ids_and_relevance", [
    ('sjuksköterska läkare Stockholm Göteborg', [
        ('24429701', 1.0),
        ('24402238', 1.0),
        ('24398617', 0.8741737070842681),
        ('24312980', 0.8741737070842681),
        ('24418102', 0.7045549889157827),
        ('24416155', 0.7045549889157827),
        ('24425309', 0.5787286960000507),
        ('24420444', 0.5787286960000507),
        ('24403543', 0.5787286960000507),
        ('24403071', 0.5787286960000507),
        ('24395432', 0.5787286960000507),
        ('24369160', 0.5787286960000507),
        ('24225167', 0.5787286960000507),
        ('24202976', 0.5787286960000507),
        ('24420717', 0.428879288175419),
        ('24408926', 0.25384773681085276)
    ])])
def test_freetext_two_work_and_two_locations_check_order(session, query, expected_ids_and_relevance):
    """
    Tests that the sorting order of hits is as expected and that relevance value has not changed
    This documents current behavior
    """

    params = {'q': query, 'limit': '100'}
    response_json = get_search(session, params)

    old_relevance = 1
    for index, hit in enumerate(response_json['hits']):
        relevance = hit['relevance']
        assert old_relevance >= relevance  # check that results are presented in ascending relevance order
        assert hit['id'] == expected_ids_and_relevance[index][0]
        assert hit['relevance'] == expected_ids_and_relevance[index][1], hit['id']
        old_relevance = relevance


@pytest.mark.parametrize("query, top_id, expected_number_of_hits", [
    ('bagare kock Stockholm Göteborg', '24274093', 1),
    ('kock bagare Stockholm Göteborg', '24274093', 1),
    ('kallskänka kock Stockholm Göteborg', '24274093', 1),
    ('lärare lågstadielärare Malmö Göteborg', '24439613', 9),
])
def test_freetext_two_work_and_two_locations(session, query, top_id, expected_number_of_hits):
    """
    Test that the top hit for a search has not changed and that the number of hits for query has not changed
    This documents current behavior
    """

    params = {'q': query, 'limit': '100'}
    response = get_search_check_number_of_results(session, expected_number_of_hits, params)
    response_json = json.loads(response.content.decode('utf8'))
    if TEST_USE_STATIC_DATA:
        assert response_json['hits'][0]['id'] == top_id


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.integration
@pytest.mark.parametrize("query, expected_number, top_id", [
    ('Bauhaus Kundtjänst', 38, '24419003'),
    ('Sirius crew', 2, '24416669'),
    ('super', 6, '24361060'),
    ('Säsong', 2, '24404500'),
])
def test_freetext_search(session, query, expected_number, top_id):
    """
    Tests from examples
    Test that specific queries should return only one hit (identified by id)
    and that freetext concepts are not included in search result
    """

    params = {'q': query, 'limit': '40'}
    response = get_search_check_number_of_results(session, expected_number=expected_number, params=params)
    response_json = json.loads(response.content.decode('utf8'))
    # freetext concepts should be empty
    check_freetext_concepts(response_json['freetext_concepts'], [[], [], [], [], [], [], [], [], []])
    if TEST_USE_STATIC_DATA:
        assert response_json['hits'][0]['id'] == top_id


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
def test_search_rules(session):
    params = {'q': "systemutvecklare python java stockholm sopra", 'limit': '1'}
    response_json = get_search(session, params=params)
    hit = response_json['hits'][0]
    check_freetext_concepts(response_json['freetext_concepts'],
                            [['python', 'java'], ['systemutvecklare'], ['stockholm'], [], [], [], [], [], []])
    assert 'sopra' in hit['employer']['name'].lower()
    assert 'sopra' in hit['employer']['workplace'].lower()
    assert 'systemutvecklare' in hit['occupation']['label'].lower()
    assert hit['workplace_address']['municipality'] == 'Stockholm'
