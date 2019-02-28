#  -*- coding: utf-8 -*-
import logging
import pytest
import sys

from dateutil import parser

from sokannonser import settings
from sokannonser.repository.querybuilder import QueryBuilder

log = logging.getLogger(__name__)
pbquery = QueryBuilder()


@pytest.mark.unit
@pytest.mark.parametrize("from_datetime", ["2018-09-28T00:00:00",
                                           '2018-09-28', '', None, []])
@pytest.mark.parametrize("to_datetime", ["2018-09-28T00:01",
                                         '2018-09-27', '', None, []])
def test_filter_timeframe(from_datetime, to_datetime):
    print('===========', sys._getframe().f_code.co_name, '============================ ')
    print(from_datetime, to_datetime)
    if not from_datetime and not to_datetime:  # from and to date are empty
        assert pbquery._filter_timeframe(from_datetime, to_datetime) is None
        return
    if from_datetime and to_datetime:
        d = pbquery._filter_timeframe(parser.parse(from_datetime),
                                      parser.parse(to_datetime))
        print(d)
        assert d['range']['publiceringsdatum']['gte'] == \
            parser.parse(from_datetime).isoformat()
        assert d['range']['publiceringsdatum']['lte'] == \
            parser.parse(to_datetime).isoformat()
        return
    if from_datetime:
        d = pbquery._filter_timeframe(parser.parse(from_datetime), to_datetime)
        assert d['range']['publiceringsdatum']['gte'] == \
            parser.parse(from_datetime).isoformat()
        return
    if to_datetime:
        d = pbquery._filter_timeframe(from_datetime, parser.parse(to_datetime))
        assert d['range']['publiceringsdatum']['lte'] == \
            parser.parse(to_datetime).isoformat()


@pytest.mark.unit
@pytest.mark.parametrize("args, exist, expected", [({settings.APIKEY: "",
                                                     settings.POSITION: ["60.5, 17.1"],
                                                     settings.POSITION_RADIUS: [5]},
                                                    True,
                                                    {"bool": {
                                                        "should":
                                                        [{"geo_distance": {
                                                            "distance": "5km",
                                                            "arbetsplatsadress.coordinates": [
                                                                17.1, 60.5
                                                            ]}}]}}),
                                                   ({settings.APIKEY: "",
                                                     settings.POSITION: ["60.5, 399.1"],
                                                     settings.POSITION_RADIUS: [5]},
                                                    False,
                                                    {"bool": {
                                                        "should":
                                                        [{"geo_distance": {
                                                            "distance": "5km",
                                                            "arbetsplatsadress.coordinates": [
                                                                399.1, 60.5
                                                            ]}}]}}),
                                                   ({settings.APIKEY: "",
                                                     settings.POSITION: ["60.5, 17.1"],
                                                     settings.POSITION_RADIUS: [-5]},
                                                    False,
                                                    {"bool": {
                                                        "should":
                                                        [{"geo_distance": {
                                                            "distance": "-5km",
                                                            "arbetsplatsadress.coordinates": [
                                                                17.1, 60.5
                                                            ]}}]}}),
                                                   ({settings.APIKEY: "",
                                                     settings.POSITION: ["60.5, 17.1", "61.5, 18.1"],
                                                     settings.POSITION_RADIUS: [5, 10]},
                                                    True,
                                                    {"bool": {
                                                        "should":
                                                        [{"geo_distance": {
                                                            "distance": "5km",
                                                            "arbetsplatsadress.coordinates": [
                                                                17.1, 60.5
                                                            ]}},
                                                         {"geo_distance": {
                                                            "distance": "10km",
                                                            "arbetsplatsadress.coordinates": [
                                                                18.1, 61.5
                                                            ]
                                                         }}]
                                                    }}),
                                                   ({settings.APIKEY: "",
                                                     settings.POSITION: ["60.5, 17.1", "61.5, 18.1"],
                                                     settings.POSITION_RADIUS: [5, 10, 15]},
                                                    True,
                                                    {"bool": {
                                                        "should":
                                                        [{"geo_distance": {
                                                            "distance": "5km",
                                                            "arbetsplatsadress.coordinates": [
                                                                17.1, 60.5
                                                            ]}},
                                                         {"geo_distance": {
                                                            "distance": "10km",
                                                            "arbetsplatsadress.coordinates": [
                                                                18.1, 61.5
                                                            ]
                                                         }}]
                                                    }}),
                                                   ({settings.APIKEY: "",
                                                     settings.POSITION: ["60.5, 17.1", "61.5, 18.1"],
                                                     settings.POSITION_RADIUS: [10]},
                                                    True,
                                                    {"bool": {
                                                        "should":
                                                        [{"geo_distance": {
                                                            "distance": "10km",
                                                            "arbetsplatsadress.coordinates": [
                                                                17.1, 60.5
                                                            ]}},
                                                         {"geo_distance": {
                                                            "distance": "5km",
                                                            "arbetsplatsadress.coordinates": [
                                                                18.1, 61.5
                                                            ]
                                                         }}]
                                                    }}),
                                                   ({settings.APIKEY: "",
                                                     settings.POSITION: ["60.5, 17.1", "61.5, 18.1"]},
                                                    True,
                                                    {"bool": {
                                                        "should":
                                                        [{"geo_distance": {
                                                            "distance": "5km",
                                                            "arbetsplatsadress.coordinates": [
                                                                17.1, 60.5
                                                            ]}},
                                                         {"geo_distance": {
                                                            "distance": "5km",
                                                            "arbetsplatsadress.coordinates": [
                                                                18.1, 61.5
                                                            ]
                                                         }}]
                                                    }})])
def test_geo_distance_filter(args, exist, expected):
    print('====================', sys._getframe().f_code.co_name, '==================== ')
    query_dsl = pbquery.parse_args(args)
    assert (expected in query_dsl["query"]["bool"]["filter"]) == exist
