#  -*- coding: utf-8 -*-
import logging
import pytest
import sys

from dateutil import parser

from sokannonser import settings
from sokannonser.repository.querybuilder import QueryBuilder
from sokannonser.repository import taxonomy

log = logging.getLogger(__name__)
pbquery = QueryBuilder()


@pytest.mark.parametrize("from_datetime", ["2018-09-28T00:00:00",
                                           '2018-09-28', '', None, []])
@pytest.mark.parametrize("to_datetime", ["2018-09-28T00:01",
                                         '2018-09-27', '', None, []])
def test_filter_timeframe(from_datetime, to_datetime):
    if not from_datetime and not to_datetime:  # from and to date are empty
        assert pbquery._filter_timeframe(from_datetime, to_datetime) is None
        return
    if from_datetime and to_datetime:
        d = pbquery._filter_timeframe(from_datetime,
                                      parser.parse(to_datetime))
        assert d['range']['publication_date']['gte'] == \
               parser.parse(from_datetime).isoformat()
        assert d['range']['publication_date']['lte'] == \
               parser.parse(to_datetime).isoformat()
        return
    if from_datetime:
        d = pbquery._filter_timeframe(from_datetime, to_datetime)
        assert d['range']['publication_date']['gte'] == \
               parser.parse(from_datetime).isoformat()
        return
    if to_datetime:
        d = pbquery._filter_timeframe(from_datetime, parser.parse(to_datetime))
        assert d['range']['publication_date']['lte'] == \
               parser.parse(to_datetime).isoformat()


@pytest.mark.unit
@pytest.mark.parametrize("args, exist, expected",
                         [({settings.APIKEY: "",
                            settings.POSITION: ["66.6, 77.7"],
                            settings.POSITION_RADIUS: [5]},
                           True,
                           {"bool": {
                               "should":
                                   [{"geo_distance": {
                                       "distance": "5km",
                                       "workplace_address.coordinates":
                                           [77.7, 66.6]}}]}}),
                          ({settings.APIKEY: "",
                            settings.POSITION: ["66.6, 180.1"],
                            settings.POSITION_RADIUS: [5]},
                           False,
                           {"bool": {
                               "should":
                                   [{"geo_distance": {
                                       "distance": "5km",
                                       "workplace_address.coordinates":
                                           [180.1, 66.6]}}]}}),
                          ({settings.APIKEY: "",
                            settings.POSITION: ["66.6, 77.7"],
                            settings.POSITION_RADIUS: [-5]},
                           False,
                           {"bool": {
                               "should":
                                   [{"geo_distance": {
                                       "distance": "-5km",
                                       "workplace_address.coordinates": [
                                           77.7, 66.6
                                       ]}}]}}),
                          ({settings.APIKEY: "",
                            settings.POSITION: ["66.6, 77.7", "59.1, 18.1"],
                            settings.POSITION_RADIUS: [5, 10]},
                           True,
                           {"bool": {
                               "should":
                                   [{"geo_distance": {
                                       "distance": "5km",
                                       "workplace_address.coordinates": [
                                           77.7, 66.6
                                       ]}},
                                       {"geo_distance": {
                                           "distance": "10km",
                                           "workplace_address.coordinates": [
                                               18.1, 59.1
                                           ]
                                       }}]
                           }}),
                          ({settings.APIKEY: "",
                            settings.POSITION: ["66.6, 77.7", "59.1, 18.1"],
                            settings.POSITION_RADIUS: [5, 10, 15]},
                           True,
                           {"bool": {
                               "should":
                                   [{"geo_distance": {
                                       "distance": "5km",
                                       "workplace_address.coordinates": [
                                           77.7, 66.6
                                       ]}},
                                       {"geo_distance": {
                                           "distance": "10km",
                                           "workplace_address.coordinates": [
                                               18.1, 59.1
                                           ]
                                       }}]
                           }}),
                          ({settings.APIKEY: "",
                            settings.POSITION: ["66.6, 77.7", "59.1, 18.1"],
                            settings.POSITION_RADIUS: [10]},
                           True,
                           {"bool": {
                               "should":
                                   [{"geo_distance": {
                                       "distance": "10km",
                                       "workplace_address.coordinates": [
                                           77.7, 66.6
                                       ]}},
                                       {"geo_distance": {
                                           "distance": "5km",
                                           "workplace_address.coordinates": [
                                               18.1, 59.1
                                           ]
                                       }}]
                           }}),
                          ({settings.APIKEY: "",
                            settings.POSITION: ["66.6, 77.7", "59.1, 18.1"]},
                           True,
                           {"bool": {
                               "should":
                                   [{"geo_distance": {
                                       "distance": "5km",
                                       "workplace_address.coordinates": [
                                           77.7, 66.6
                                       ]}},
                                       {"geo_distance": {
                                           "distance": "5km",
                                           "workplace_address.coordinates": [
                                               18.1, 59.1
                                           ]
                                       }}]
                           }})])
def test_geo_distance_filter(args, exist, expected):
    query_dsl = pbquery.parse_args(args)
    assert (expected in query_dsl["query"]["bool"]["filter"]) == exist


@pytest.mark.unit
@pytest.mark.parametrize("args, expected_pos, expected_neg",
                         [({settings.APIKEY: "",
                            taxonomy.REGION: ["01", "02"]},
                           [
                               {"term": {"workplace_address.region_code":
                                             {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.region_code":
                                             {"value": "02", "boost": 1.0}}},
                               {"term": {"workplace_address.region_concept_id":
                                             {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.region_concept_id":
                                             {"value": "02", "boost": 1.0}}}
                           ],
                           []),
                          ({settings.APIKEY: "",
                            taxonomy.MUNICIPALITY: ["0111"]},
                           [
                               {"term": {"workplace_address.municipality_code":
                                             {"value": "0111", "boost": 2.0}}},
                               {"term": {
                                   "workplace_address.municipality_concept_id":
                                       {"value": "0111", "boost": 2.0}}}
                           ],
                           []),
                          ({settings.APIKEY: "",
                            taxonomy.REGION: ["01", "02"],
                            taxonomy.MUNICIPALITY: ["1111", "2222"]},
                           [
                               {"term": {"workplace_address.region_code":
                                             {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.region_code":
                                             {"value": "02", "boost": 1.0}}},
                               {"term": {"workplace_address.region_concept_id":
                                             {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.region_concept_id":
                                             {"value": "02", "boost": 1.0}}},
                               {"term": {"workplace_address.municipality_code":
                                             {"value": "1111", "boost": 2.0}}},
                               {"term": {"workplace_address.municipality_code":
                                             {"value": "2222", "boost": 2.0}}},
                               {"term": {
                                   "workplace_address.municipality_concept_id":
                                       {"value": "1111", "boost": 2.0}}},
                               {"term": {
                                   "workplace_address.municipality_concept_id":
                                       {"value": "2222", "boost": 2.0}}}
                           ],
                           []),
                          ({settings.APIKEY: "",
                            taxonomy.REGION: ["01", "-02"],
                            taxonomy.MUNICIPALITY: ["1111", "-2222"]},
                           [
                               {"term": {"workplace_address.region_code":
                                             {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.municipality_code":
                                             {"value": "1111", "boost": 2.0}}},
                               {"term": {"workplace_address.region_code":
                                             {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.municipality_code":
                                             {"value": "1111", "boost": 2.0}}}
                           ],
                           [
                               {"term": {"workplace_address.region_code":
                                             {"value": "02"}}},
                               {"term": {"workplace_address.municipality_code":
                                             {"value": "2222"}}},
                               {"term": {"workplace_address.region_concept_id":
                                             {"value": "02"}}},
                               {"term": {
                                   "workplace_address.municipality_concept_id":
                                       {"value": "2222"}}}
                           ]),
                          ({settings.APIKEY: "",
                            taxonomy.REGION: ["01", "-02"],
                            taxonomy.MUNICIPALITY: ["1111"]},
                           [
                               {"term": {"workplace_address.region_code":
                                             {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.municipality_code":
                                             {"value": "1111", "boost": 2.0}}},
                               {"term": {"workplace_address.region_concept_id":
                                             {"value": "01", "boost": 1.0}}},
                               {"term": {
                                   "workplace_address.municipality_concept_id":
                                       {"value": "1111", "boost": 2.0}}},
                           ],
                           [
                               {"term": {"workplace_address.region_code":
                                             {"value": "02"}}},
                               {"term": {"workplace_address.region_concept_id":
                                             {"value": "02"}}}
                           ]),
                          ({settings.APIKEY: "",
                            taxonomy.REGION: ["01"],
                            taxonomy.MUNICIPALITY: ["1111", "-2222"]},
                           [
                               {"term": {"workplace_address.region_code":
                                             {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.municipality_code":
                                             {"value": "1111", "boost": 2.0}}},
                               {"term": {"workplace_address.region_concept_id":
                                             {"value": "01", "boost": 1.0}}},
                               {"term": {
                                   "workplace_address.municipality_concept_id":
                                       {"value": "1111", "boost": 2.0}}},
                           ],
                           [
                               {"term": {"workplace_address.municipality_code":
                                             {"value": "2222"}}},
                               {"term": {
                                   "workplace_address.municipality_concept_id":
                                       {"value": "2222"}}}
                           ])])
def test_region_municipality_query(args, expected_pos, expected_neg):
    query_dsl = pbquery.parse_args(args)
    if expected_pos:
        pos_query = query_dsl["query"]["bool"]["must"][0]["bool"]["should"]
        assert (len(pos_query) == len(expected_pos))
        for e in expected_pos:
            assert (e in pos_query)
    if expected_neg:
        neg_query = query_dsl["query"]["bool"]['must'][0]["bool"]["must_not"]
        assert (len(neg_query) == len(expected_neg))
        for e in expected_neg:
            assert (e in neg_query)
    print('====================', sys._getframe().f_code.co_name,
          '==================== ')


# Querybuilder tests
@pytest.mark.unit
def test_rewrite_word_for_regex():
    assert pbquery._rewrite_word_for_regex("[python3]") == "\\[python3\\]"
    assert pbquery._rewrite_word_for_regex("python3") == "python3"
    assert pbquery._rewrite_word_for_regex("asp.net") == "asp\\.net"
    assert pbquery._rewrite_word_for_regex("c++") == "c\\+\\+"


@pytest.mark.unit
def test_rewrite_querystring():
    # concepts blob should be handled differently
    concepts = {'skill': [
        {'term': 'c++', 'uuid': '1eb1dbeb-e22a-53cb-bb28-c9fbca5ad307',
         'concept': 'C++', 'type': 'KOMPETENS',
         'term_uuid': '9734cba6-eff8-5cdc-9881-392a4345e57e',
         'term_misspelled': False,
         'version': 'NARVALONTOLOGI-2.0.0.33', 'operator': ''},
        {'term': 'c#', 'uuid': 'af98ee4d-49e7-5274-bc76-a9f119c1514c',
         'concept': 'C-sharp', 'type': 'KOMPETENS',
         'term_uuid': '37da571a-a958-5b3d-a857-0a0a6bbc88cf',
         'term_misspelled': False,
         'version': 'NARVALONTOLOGI-2.0.0.33', 'operator': ''},
        {'term': 'asp.net', 'uuid': '18d88a83-55d5-527b-a800-3695ed035a0c',
         'concept': 'Asp.net', 'type': 'KOMPETENS',
         'term_uuid': '280d3fa7-becd-510d-94ac-c67edb0ef4e0',
         'term_misspelled': False,
         'version': 'NARVALONTOLOGI-2.0.0.33', 'operator': ''},
        {'term': 'c++', 'uuid': '1eb1dbeb-e22a-53cb-bb28-c9fbca5ad307',
         'concept': 'C++', 'type': 'KOMPETENS',
         'term_uuid': '9734cba6-eff8-5cdc-9881-392a4345e57e',
         'term_misspelled': False,
         'version': 'NARVALONTOLOGI-2.0.0.33', 'operator': ''}], 'occupation': [
        {'term': 'specialpedagog',
         'uuid': '4872acf8-ea61-50fe-8a7e-7af82b37ce9e',
         'concept': 'Specialpedagog',
         'type': 'YRKE', 'term_uuid': 'c6db8f6e-69f7-5aae-af18-2a1eae084eba',
         'term_misspelled': False,
         'version': 'NARVALONTOLOGI-2.0.0.33', 'operator': ''},
        {'term': 'lärare', 'uuid': 'eadc9f5f-35c0-5324-b215-ea388ca054ff',
         'concept': 'Lärare', 'type': 'YRKE',
         'term_uuid': '300844f7-77b6-539e-a8d7-1955ce18a00c',
         'term_misspelled': False,
         'version': 'NARVALONTOLOGI-2.0.0.33', 'operator': ''},
        {'term': 'speciallärare',
         'uuid': '2708c006-d8d0-5920-b434-a5968aa088e3',
         'concept': 'Speciallärare',
         'type': 'YRKE', 'term_uuid': 'cd50806f-3c52-5e73-a06e-c7a65f7410a4',
         'term_misspelled': False,
         'version': 'NARVALONTOLOGI-2.0.0.33', 'operator': ''}], 'trait': [],
        'location': [], 'skill_must': [],
        'occupation_must': [], 'trait_must': [], 'location_must': [],
        'skill_must_not': [],
        'occupation_must_not': [], 'trait_must_not': [],
        'location_must_not': []}
    assert pbquery._rewrite_querystring("specialpedagog lärare speciallärare",
                                        concepts) == ""
    assert pbquery._rewrite_querystring("specialpedagog speciallärare lärare",
                                        concepts) == ""
    assert pbquery._rewrite_querystring("lärare speciallärare flärgare",
                                        concepts) == "flärgare"
    assert pbquery._rewrite_querystring(
        "korvprånglare c++ asp.net [python3] flärgare",
        concepts) == "korvprånglare [python3] flärgare"
