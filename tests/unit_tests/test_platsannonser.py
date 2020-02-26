#  -*- coding: utf-8 -*-
import logging
import pytest
import sys

from dateutil import parser

from sokannonser import settings
from sokannonser.repository.querybuilder import QueryBuilder
from sokannonser.repository import taxonomy

log = logging.getLogger(__name__)


class MockOntology():
    def __init__(self):
        self.extracted_locations = set()


class MockTextToConcept:
    def __init__(self):
        self.ontology = MockOntology()

    def text_to_concepts(self, text):
        skills = {
            "python": {
                "term": "python",
                "uuid": "0b6d3a08-3cc3-546d-b8ed-f2de299bafdb",
                "concept": "Python",
                "type": "KOMPETENS",
                "term_uuid": "f60fa7fd-00f7-5803-acd7-1a3eda170397",
                "term_misspelled": False,
                "plural_occupation": False,
                "definite_occupation": False,
                "version": "SYNONYM-DIC-2.0.1.25",
                "operator": ""
            },
            "java": {
                "term": "java",
                "uuid": "c965e8aa-751a-5923-97bd-b8bd6d5e813a",
                "concept": "Java",
                "type": "KOMPETENS",
                "term_uuid": "e3d2a75a-5717-56d2-ad8a-ee4b5baf8530",
                "term_misspelled": False,
                "plural_occupation": False,
                "definite_occupation": False,
                "version": "SYNONYM-DIC-2.0.1.25",
                "operator": "+"
            },
            "php": {
                "term": "php",
                "uuid": "3e3629d1-95f6-5b0e-8f5c-d6a709fd94e2",
                "concept": "Php",
                "type": "KOMPETENS",
                "term_uuid": "216af07e-d210-572f-8885-b13d79b80acc",
                "term_misspelled": False,
                "plural_occupation": False,
                "definite_occupation": False,
                "version": "SYNONYM-DIC-2.0.1.25",
                "operator": "-"
            }
        }
        occupations = {
            "systemutvecklare": {
                "term": "systemutvecklare",
                "uuid": "df9e7a73-2cc3-5b32-a84e-7e68a527e80e",
                "concept": "Systemutvecklare",
                "type": "YRKE",
                "term_uuid": "7296755c-acf2-5eed-9d4b-e4cd845cd05a",
                "term_misspelled": False,
                "plural_occupation": False,
                "definite_occupation": False,
                "version": "SYNONYM-DIC-2.0.1.25",
                "operator": ""
            }
        }
        response = {
            "skill": [],
            "occupation": [],
            "trait": [],
            "location": [],
            "skill_must": [],
            "occupation_must": [],
            "trait_must": [],
            "location_must": [],
            "skill_must_not": [],
            "occupation_must_not": [],
            "trait_must_not": [],
            "location_must_not": []
        }
        for word in text.split():
            if word.startswith("+"):
                word = word[1:]
                if word in skills:
                    response['skill_must'].append(skills[word])
                if word in occupations:
                    response['occupation_must'].append(occupations[word])
            elif word.startswith("-"):
                word = word[1:]
                if word in skills:
                    response['skill_must_not'].append(skills[word])
                if word in occupations:
                    response['occupation_must_not'].append(occupations[word])
            else:
                if word in skills:
                    response['skill'].append(skills[word])
                if word in occupations:
                    response['occupation'].append(occupations[word])

        return response


pbquery = QueryBuilder(MockTextToConcept())


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
         'version': 'NARVALONTOLOGI-2.0.0.33', 'operator': ''},
        {'term': 'tcp/ip', 'uuid': '09df5ef2-357f-5cfc-9333-dec2e220638a',
         'concept': 'Tcp/ip', 'type': 'KOMPETENS',
         'term_uuid': 'a18b2945-779f-5032-bbaa-c7945a63055f',
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
    assert pbquery._rewrite_querystring("tcp/ip", concepts) == ""


@pytest.mark.unit
@pytest.mark.parametrize("querystring, expected", [
    ("python \"grym kodare\"", ({"phrases": ["grym kodare"], "phrases_must": [], "phrases_must_not": []}, "python")),
    ("java \"malmö stad\"", ({"phrases": ["malmö stad"], "phrases_must": [], "phrases_must_not": []}, "java")),
    ("python -\"grym kodare\" +\"i am lazy\"", ({"phrases": [], "phrases_must": ["i am lazy"], "phrases_must_not": ["grym kodare"]}, "python")),
    ("\"python på riktigt\" -\"grym kodare\" +\"i am lazy\"", ({"phrases": ["python på riktigt"], "phrases_must": ["i am lazy"], "phrases_must_not": ["grym kodare"]}, "")),
])
def test_extract_querystring_phrases(querystring, expected):
    assert expected == pbquery.extract_quoted_phrases(querystring)


@pytest.mark.unit
@pytest.mark.parametrize("querystring, expected", [
    ("\"i am lazy", ({"phrases": ["i am lazy"], "phrases_must": [], "phrases_must_not": []}, "")),
    ("python \"grym kodare\" \"i am lazy java", ({"phrases": ["grym kodare", "i am lazy java"], "phrases_must": [], "phrases_must_not": []}, "python")),
    ("python \"grym kodare\" +\"i am lazy", ({"phrases": ["grym kodare"], "phrases_must": ["i am lazy"], "phrases_must_not": []}, "python")),
    ("python \"grym kodare\" -\"i am lazy", ({"phrases": ["grym kodare"], "phrases_must": [], "phrases_must_not": ["i am lazy"]}, "python")),
])
def test_extract_querystring_phrases_with_unbalanced_quotes(querystring, expected):
    assert expected == pbquery.extract_quoted_phrases(querystring)


@pytest.mark.unit
@pytest.mark.parametrize("querystring, expected", [
    ("-php", {"bool": {"must_not": {"term": {"keywords.enriched.skill.raw": {"value": "php"}}}}}),
    ("+java", {"bool": {"must": {"term": {"keywords.enriched.skill.raw": {"value": "java"}}}}}),
    ("python", {"bool": {"must": {"bool": {"should": {"term": {"keywords.enriched.skill.raw": {"value": "python"}}}}}}}),
    ("systemutvecklare python +java", {"bool": {"must": {"bool": {"should": {"term": {"keywords.enriched.skill.raw": {"value": "python"}}}}}}}),
    ("systemutvecklare python +java", {"bool": {"must": {"term": {"keywords.enriched.skill.raw": {"value": "java"}}}}}),
    ("systemutvecklare python +java", {"bool": {"must": {"bool": {"should": {"term": {"keywords.enriched.occupation.raw": {"value": "systemutvecklare"}}}}}}}),
    ("systemutvecklare python +java", {"bool": {"must": {"bool": {"should": {"term": {"keywords.extracted.occupation.raw": {"value": "systemutvecklare"}}}}}}}),
    ("systemutvecklare python +java -php", {"bool": {"must": {"bool": {"should": {"term": {"keywords.enriched.skill.raw": {"value": "python"}}}}}}}),
    ("systemutvecklare python +java -php", {"bool": {"must": {"term": {"keywords.enriched.skill.raw": {"value": "java"}}}}}),
    ("systemutvecklare python +java -php", {"bool": {"must": {"bool": {"should": {"term": {"keywords.enriched.occupation.raw": {"value": "systemutvecklare"}}}}}}}),
    ("systemutvecklare python +java -php", {"bool": {"must_not": {"term": {"keywords.enriched.skill.raw": {"value": "php"}}}}}),
])
def test_freetext_bool_structure(querystring, expected):
    result = pbquery._build_freetext_query(querystring, None, "and", False)
    assert _assert_json_structure(result, expected)


def _assert_json_structure(result, expected):
    return _walk_dictionary(result, expected)


def _walk_dictionary(result, expected):
    if isinstance(result, str) and isinstance(expected, str):
        return result == expected
    else:
        for item in expected:
            if item in result:
                if isinstance(result[item], list):
                    for listitem in result[item]:
                        if _walk_dictionary(listitem, expected[item]):
                            return True
                else:
                    return _walk_dictionary(result[item], expected[item])

        return False

