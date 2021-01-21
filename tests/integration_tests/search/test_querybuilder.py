import sys
import datetime
import pytz
import pytest
from dateutil import parser
from sokannonser import settings
from sokannonser.repository import taxonomy
from sokannonser.repository.querybuilder import QueryBuilder
from tests.integration_tests.test_resources import mock_for_querybuilder_tests as mock


@pytest.mark.parametrize("collection_id, expected", [(["UdVa_jRr_9DE"],
                                                      {'bool': {'should': {'terms': {
                                                          'occupation.concept_id.keyword': ['fFkk_8X8_pym',
                                                                                            '4zLr_jP5_peZ',
                                                                                            '5NxT_WeC_C31']}}}}),
                                                     (["-UdVa_jRr_9DE"],
                                                      {'bool': {'must_not': {'terms': {
                                                          'occupation.concept_id.keyword': ['fFkk_8X8_pym',
                                                                                            '4zLr_jP5_peZ',
                                                                                            '5NxT_WeC_C31']}}}}),
                                                     ([None], None), ([[]], None),
                                                     (["None_existing_concept_id"], None)])
def test_build_occupation_collection_query(collection_id, expected):
    querybuilder = QueryBuilder(mock.MockTextToConcept)
    querybuilder.occupation_collections = {
        "UdVa_jRr_9DE": [
            "fFkk_8X8_pym",
            "4zLr_jP5_peZ",
            "5NxT_WeC_C31"]
    }
    query_result = querybuilder.build_yrkessamlingar_query(collection_id)
    assert query_result == expected


@pytest.mark.parametrize("querystring, expected", [('xx,', 'xx '),  # trailing space
                                                   ('xx.', 'xx'),
                                                   ('xx!', 'xx'),
                                                   ('xx?', 'xx'),
                                                   ('xx:', 'xx'),
                                                   ('xx;', 'xx'),
                                                   ('.xx', 'xx'),
                                                   (',xx', ' xx'),  # leading space
                                                   ('!xx', 'xx'),
                                                   ('?xx', 'xx'),
                                                   (':xx', 'xx'),
                                                   (';xx', 'xx'),
                                                   (';xx', 'xx'),
                                                   (' xx', ' xx'),
                                                   ('x x', 'x x'),
                                                   ('x,x ', 'x x '),  # trailing space
                                                   ('x.x ', 'x.x '),
                                                   ('x!x ', 'x!x '),
                                                   ('x?x ', 'x?x '),
                                                   ('x:x ', 'x:x '),
                                                   ('x;x ', 'x;x '),
                                                   ('xx ', 'xx '),
                                                   ('x/y', 'x/y'),
                                                   ('.x/y', 'x/y'),
                                                   ('x/y.', 'x/y'),
                                                   ('x / y.', 'x / y'),
                                                   ('y,.!?:; x', 'y  x'),
                                                   ('x,y.z!1?2:3;4 x', 'x y.z!1?2:3;4 x'),
                                                   ('12345x', '12345x'),
                                                   ('.12345', '12345'),
                                                   ('.12345.', '12345'),
                                                   ('.12345.', '12345'),
                                                   (',12345', ' 12345'),
                                                   (',12345,', ' 12345 '),
                                                   ('\\x', '\\x'),
                                                   ('\\x,', '\\x '),
                                                   ('\\x.', '\\x'),
                                                   ('\\.x.', '\\.x'),
                                                   ('.\\.x.', '\\.x'),
                                                   (',\\.x.', ' \\.x'),
                                                   ])
def test_querystring_char_removal(querystring, expected):
    querybuilder = QueryBuilder(mock.MockTextToConcept())
    formatted = querybuilder._remove_unwanted_chars_from_querystring(querystring)
    assert formatted == expected


def test_parse_args_query_with_slash():
    args = {'x-feature-freetext-bool-method': 'and', 'x-feature-disable-smart-freetext': None,
            'x-feature-enable-false-negative': None, 'published-before': None, 'published-after': None,
            'occupation-name': None, 'occupation-group': None, 'occupation-field': None, 'occupation-collection': None,
            'skill': None, 'language': None, 'worktime-extent': None, 'parttime.min': None, 'parttime.max': None,
            'driving-license-required': None, 'driving-license': None, 'employment-type': None, 'experience': None,
            'municipality': None, 'region': None, 'country': None, 'unspecified-sweden-workplace': None, 'abroad': None,
            'position': None, 'position.radius': None, 'employer': None, 'q': 'systemutvecklare/programmerare',
            'qfields': None, 'relevance-threshold': None, 'sort': None, 'stats': None, 'stats.limit': None}

    expected_query_dsl = {'from': 0, 'size': 10, 'track_total_hits': True, 'track_scores': True, 'query': {'bool': {
        'must': [{'bool': {'must': [{'bool': {'should': [{'multi_match': {'query': 'systemutvecklare/programmerare',
                                                                          'type': 'cross_fields', 'operator': 'and',
                                                                          'fields': ['headline^3',
                                                                                     'keywords.extracted.employer^2',
                                                                                     'description.text', 'id',
                                                                                     'external_id', 'source_type',
                                                                                     'keywords.extracted.location^5']}},
                                                         {'match': {'headline.words': {
                                                             'query': 'systemutvecklare/programmerare',
                                                             'operator': 'and', 'boost': 5}}}]}}]}}],
        'filter': [{'range': {'publication_date': {'lte': 'now+1H/m'}}},
                   {'range': {'last_publication_date': {'gte': 'now+1H/m'}}}, {'term': {'removed': False}}]}},
                          'aggs': {'positions': {'sum': {'field': 'number_of_vacancies'}}, 'complete_00_occupation': {
                              'terms': {'field': 'keywords.enriched_typeahead_terms.occupation.raw', 'size': 20.0,
                                        'include': '.*'}}, 'complete_00_skill': {
                              'terms': {'field': 'keywords.enriched_typeahead_terms.skill.raw', 'size': 20.0,
                                        'include': '.*'}}, 'complete_00_location': {
                              'terms': {'field': 'keywords.enriched_typeahead_terms.location.raw', 'size': 20.0,
                                        'include': '.*'}}}, 'sort': ['_score', {'publication_date': 'desc'}]}

    querybuilder = QueryBuilder(mock.MockTextToConcept())
    assert querybuilder.parse_args(args) == expected_query_dsl


@pytest.mark.parametrize("from_datetime", ["2018-09-28T00:00:00", '2018-09-28', '', None, []])
@pytest.mark.parametrize("to_datetime", ["2018-09-28T00:01", '2018-09-27', '', None, []])
def test_filter_timeframe(from_datetime, to_datetime):
    querybuilder = QueryBuilder(mock.MockTextToConcept())
    if not from_datetime and not to_datetime:  # from and to date are empty
        assert querybuilder._filter_timeframe(from_datetime, to_datetime) is None
        return
    if from_datetime and to_datetime:
        d = querybuilder._filter_timeframe(from_datetime,
                                           parser.parse(to_datetime))
        assert d['range']['publication_date']['gte'] == parser.parse(from_datetime).isoformat()
        assert d['range']['publication_date']['lte'] == parser.parse(to_datetime).isoformat()
        return
    if from_datetime:
        d = querybuilder._filter_timeframe(from_datetime, to_datetime)
        assert d['range']['publication_date']['gte'] == parser.parse(from_datetime).isoformat()
        return
    if to_datetime:
        d = querybuilder._filter_timeframe(from_datetime, parser.parse(to_datetime))
        assert d['range']['publication_date']['lte'] == parser.parse(to_datetime).isoformat()


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
    querybuilder = QueryBuilder(mock.MockTextToConcept())
    query_dsl = querybuilder.parse_args(args)
    assert (expected in query_dsl["query"]["bool"]["filter"]) == exist


@pytest.mark.parametrize("args, expected_pos, expected_neg",
                         [({settings.APIKEY: "",
                            taxonomy.REGION: ["01", "02"]},
                           [
                               {"term": {"workplace_address.region_code": {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.region_code": {"value": "02", "boost": 1.0}}},
                               {"term": {"workplace_address.region_concept_id": {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.region_concept_id": {"value": "02", "boost": 1.0}}}
                           ],
                           []),
                          ({settings.APIKEY: "",
                            taxonomy.MUNICIPALITY: ["0111"]},
                           [
                               {"term": {"workplace_address.municipality_code": {"value": "0111", "boost": 2.0}}},
                               {"term": {
                                   "workplace_address.municipality_concept_id": {"value": "0111", "boost": 2.0}}}
                           ],
                           []),
                          ({settings.APIKEY: "",
                            taxonomy.REGION: ["01", "02"],
                            taxonomy.MUNICIPALITY: ["1111", "2222"]},
                           [
                               {"term": {"workplace_address.region_code": {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.region_code": {"value": "02", "boost": 1.0}}},
                               {"term": {"workplace_address.region_concept_id": {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.region_concept_id": {"value": "02", "boost": 1.0}}},
                               {"term": {"workplace_address.municipality_code": {"value": "1111", "boost": 2.0}}},
                               {"term": {"workplace_address.municipality_code": {"value": "2222", "boost": 2.0}}},
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
                               {"term": {"workplace_address.region_code": {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.municipality_code": {"value": "1111", "boost": 2.0}}},
                               {"term": {"workplace_address.region_code": {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.municipality_code": {"value": "1111", "boost": 2.0}}}
                           ],
                           [
                               {"term": {"workplace_address.region_code": {"value": "02"}}},
                               {"term": {"workplace_address.municipality_code": {"value": "2222"}}},
                               {"term": {"workplace_address.region_concept_id": {"value": "02"}}},
                               {"term": {
                                   "workplace_address.municipality_concept_id": {"value": "2222"}}}
                           ]),
                          ({settings.APIKEY: "",
                            taxonomy.REGION: ["01", "-02"],
                            taxonomy.MUNICIPALITY: ["1111"]},
                           [
                               {"term": {"workplace_address.region_code": {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.municipality_code": {"value": "1111", "boost": 2.0}}},
                               {"term": {"workplace_address.region_concept_id": {"value": "01", "boost": 1.0}}},
                               {"term": {
                                   "workplace_address.municipality_concept_id": {"value": "1111", "boost": 2.0}}},
                           ],
                           [
                               {"term": {"workplace_address.region_code": {"value": "02"}}},
                               {"term": {"workplace_address.region_concept_id": {"value": "02"}}}
                           ]),
                          ({settings.APIKEY: "",
                            taxonomy.REGION: ["01"],
                            taxonomy.MUNICIPALITY: ["1111", "-2222"]},
                           [
                               {"term": {"workplace_address.region_code": {"value": "01", "boost": 1.0}}},
                               {"term": {"workplace_address.municipality_code": {"value": "1111", "boost": 2.0}}},
                               {"term": {"workplace_address.region_concept_id": {"value": "01", "boost": 1.0}}},
                               {"term": {
                                   "workplace_address.municipality_concept_id": {"value": "1111", "boost": 2.0}}},
                           ],
                           [
                               {"term": {"workplace_address.municipality_code": {"value": "2222"}}},
                               {"term": {"workplace_address.municipality_concept_id": {"value": "2222"}}}
                           ])])
def test_region_municipality_query(args, expected_pos, expected_neg):
    print('================', sys._getframe().f_code.co_name, '===============')
    querybuilder = QueryBuilder(mock.MockTextToConcept())
    query_dsl = querybuilder.parse_args(args)
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


def test_rewrite_word_for_regex():
    querybuilder = QueryBuilder(mock.MockTextToConcept())
    assert querybuilder._rewrite_word_for_regex("[python3]") == "\\[python3\\]"
    assert querybuilder._rewrite_word_for_regex("python3") == "python3"
    assert querybuilder._rewrite_word_for_regex("asp.net") == "asp\\.net"
    assert querybuilder._rewrite_word_for_regex("c++") == "c\\+\\+"


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
    querybuilder = QueryBuilder(mock.MockTextToConcept())
    assert querybuilder._rewrite_querystring("specialpedagog lärare speciallärare", concepts) == ""
    assert querybuilder._rewrite_querystring("specialpedagog speciallärare lärare", concepts) == ""
    assert querybuilder._rewrite_querystring("lärare speciallärare flärgare", concepts) == "flärgare"
    assert querybuilder._rewrite_querystring("korvprånglare c++ asp.net [python3] flärgare",
                                             concepts) == "korvprånglare [python3] flärgare"
    assert querybuilder._rewrite_querystring("tcp/ip", concepts) == ""


@pytest.mark.parametrize("querystring, expected_phrase, expected_returned_query, test_id", [
    # With these quotes, the query will be returned with some quote modification
    # the 'matches' field will be empty
    ("'gymnasielärare'", [], 'gymnasielärare', 'a'),
    ("""gymnasielärare""", [], 'gymnasielärare', 'b'),
    ('''gymnasielärare''', [], 'gymnasielärare', 'c'),
    ("gymnasielärare\"", [], 'gymnasielärare', 'd'),
    ("gymnasielärare\'", [], 'gymnasielärare', 'e'),
    ("\'gymnasielärare", [], 'gymnasielärare', 'f'),
    (r"""gymnasielärare""", [], 'gymnasielärare', 'g'),
    (r'''gymnasielärare''', [], 'gymnasielärare', 'h'),
    ("gymnasielärare lärare", [], 'gymnasielärare lärare', 'i'),
    ("""'gymnasielärare'""", [], 'gymnasielärare', 'j'),
    ('''"gymnasielärare" "lärare"''', [], 'gymnasielärare lärare', 'aa'),
    ('''"gymnasielärare lärare"''', [], 'gymnasielärare lärare', 'ab'),
    ('"gymnasielärare"', [], 'gymnasielärare', 'ac'),
    ("\"gymnasielärare\"", [], 'gymnasielärare', 'ad'),
    ("\"gymnasielärare", [], 'gymnasielärare', 'ae'),
    ("\"gymnasielärare", [], 'gymnasielärare', 'af'),
    ('''"gymnasielärare"''', [], 'gymnasielärare', 'ag'),

    # "normal" quotes, 'phrases' field empty, query returned
    ("gymnasielärare", [], 'gymnasielärare', 'x'),
    ('gymnasielärare', [], 'gymnasielärare', 'y'),
    ('python', [], 'python', 'z'),
])
def test_extract_querystring_different_quotes(querystring, expected_phrase, expected_returned_query, test_id):
    """
        Test behavior of querybuilder.extract_quoted_phrases
        when sending strings with different types of quotes
    """
    querybuilder = QueryBuilder(mock.MockTextToConcept())
    actual_result = querybuilder.extract_quoted_phrases(querystring)
    # no plus or minus used in this test, so these fields must be empty
    assert actual_result[0]['phrases_must'] == []
    assert actual_result[0]['phrases_must_not'] == []

    actual_phrases = actual_result[0]['phrases']
    assert actual_phrases == expected_phrase, f"got {actual_phrases} but expected {expected_phrase}"

    actual_returned_query = actual_result[1]
    assert actual_returned_query == expected_returned_query, f"got {actual_returned_query} but expected {expected_returned_query}"


@pytest.mark.parametrize("querystring, expected", [
    ("python \"grym kodare\"",
     ({'phrases': [], 'phrases_must': [], 'phrases_must_not': []}, 'python grym kodare')),
    ("java \"malmö stad\"",
     ({'phrases': [], 'phrases_must': [], 'phrases_must_not': []}, 'java malmö stad')),
    ("python -\"grym kodare\" +\"i am lazy\"",
     ({'phrases': [], 'phrases_must': [], 'phrases_must_not': []}, 'python - grym kodare + i am lazy')
     ),
    ("\"python på riktigt\" -\"grym kodare\" +\"i am lazy\"",
     ({'phrases': [], 'phrases_must': [], 'phrases_must_not': []}, 'python på riktigt - grym kodare + i am lazy')),
])
def test_extract_querystring_phrases(querystring, expected):
    querybuilder = QueryBuilder(mock.MockTextToConcept())
    assert querybuilder.extract_quoted_phrases(querystring) == expected


@pytest.mark.parametrize("querystring, expected", [
    ("\"i am lazy", ({'phrases': [], 'phrases_must': [], 'phrases_must_not': []}, 'i am lazy')),
    ("python \"grym kodare\" \"i am lazy java",
     ({'phrases': [], 'phrases_must': [], 'phrases_must_not': []}, 'python grym kodare i am lazy java')),
    ("python \"grym kodare\" +\"i am lazy",
     ({'phrases': [], 'phrases_must': [], 'phrases_must_not': []}, 'python grym kodare + i am lazy')),
    ("python \"grym kodare\" -\"i am lazy",
     ({'phrases': [], 'phrases_must': [], 'phrases_must_not': []}, 'python grym kodare - i am lazy')),
])
def test_extract_querystring_phrases_with_unbalanced_quotes(querystring, expected):
    querybuilder = QueryBuilder(mock.MockTextToConcept())
    assert querybuilder.extract_quoted_phrases(querystring)== expected



@pytest.mark.parametrize("querystring, expected", [
    ("-php", {"bool": {"must_not": {"term": {"keywords.enriched.skill.raw": {"value": "php"}}}}}),
    ("+java", {"bool": {"must": {"term": {"keywords.enriched.skill.raw": {"value": "java"}}}}}),
    ("python",
     {"bool": {"must": {
         "bool": {"should": {"term": {"keywords.enriched.skill.raw": {"value": "python"}}}}}}}),
    ("systemutvecklare python +java",
     {"bool": {
         "must": {"bool": {"should": {"term": {"keywords.enriched.skill.raw": {"value": "python"}}}}}}}),
    ("systemutvecklare python +java",
     {"bool": {"must": {"term": {"keywords.enriched.skill.raw": {"value": "java"}}}}}),
    ("systemutvecklare python +java", {"bool": {
        "must": {"bool": {
            "should": {"term": {"keywords.enriched.occupation.raw": {"value": "systemutvecklare"}}}}}}}),
    ("systemutvecklare python +java", {"bool": {
        "must": {"bool": {
            "should": {"term": {"keywords.extracted.occupation.raw": {"value": "systemutvecklare"}}}}}}}),
    ("systemutvecklare python +java -php",
     {"bool": {
         "must": {"bool": {"should": {"term": {"keywords.enriched.skill.raw": {"value": "python"}}}}}}}),
    ("systemutvecklare python +java -php",
     {"bool": {"must": {"term": {"keywords.enriched.skill.raw": {"value": "java"}}}}}),
    ("systemutvecklare python +java -php", {"bool": {
        "must": {"bool": {
            "should": {"term": {"keywords.enriched.occupation.raw": {"value": "systemutvecklare"}}}}}}}),
    ("systemutvecklare python +java -php",
     {"bool": {"must_not": {"term": {"keywords.enriched.skill.raw": {"value": "php"}}}}}),
])
def test_freetext_bool_structure(querystring, expected):
    querybuilder = QueryBuilder(mock.MockTextToConcept())
    result = querybuilder._build_freetext_query(querystring, queryfields=None, freetext_bool_method="and",
                                                disable_smart_freetext=False)
    assert _assert_json_structure(result, expected)


def utc_offset():
    offset = datetime.datetime.now(pytz.timezone('Europe/Stockholm')).utcoffset()
    return int(offset.seconds / 3600)


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
