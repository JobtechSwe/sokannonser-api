import logging
from flask_restplus import abort
from elasticsearch import exceptions
from valuestore import taxonomy
from sokannonser import settings
from . import elastic
import json
from datetime import datetime

log = logging.getLogger(__name__)


def get_stats_for(taxonomy_type):
    log.info("Looking for %s" % taxonomy_type)
    value_path = {
        settings.taxonomy_type[settings.OCCUPATION]: "yrkesroll.kod.keyword",
        settings.taxonomy_type[settings.GROUP]: "yrkesgrupp.kod.keyword",
        settings.taxonomy_type[settings.FIELD]: "yrkesomrade.kod.keyword",
        settings.taxonomy_type[settings.SKILL]: "krav.kompetenser.kod.keyword",
        settings.taxonomy_type[settings.WORKTIME_EXTENT]: "arbetstidstyp.kod.keyword",
    }
    aggs_query = {
        "from": 0, "size": 0,
        "query": {
            "match_all": {
            }
        },
        "aggs": {
            "antal_annonser": {
                "terms": {"field": value_path[taxonomy_type], "size": 5000},
            }
        }
    }
    aggs_result = elastic.search(index=settings.ES_INDEX, body=aggs_query)
    code_count = {
        item['key']: item['doc_count']
        for item in aggs_result['aggregations']['antal_annonser']['buckets']}
    return code_count


def find_platsannonser(args):
    query_dsl = _parse_args(args)
    log.debug(json.dumps(query_dsl, indent=2))
    try:
        query_result = elastic.search(index=settings.ES_INDEX, body=query_dsl)
    except exceptions.ConnectionError as e:
        log.error('Failed to connect to elasticsearch: %s' % str(e), e)
        abort(500, 'Failed to establish connection to database')
    return query_result.get('hits', {})


# Todo: Refactor
def _parse_args(args):
    query_dsl = dict()
    query_dsl['from'] = args.pop(settings.OFFSET, 0)
    query_dsl['size'] = args.pop(settings.LIMIT, 10)

    if args.get(settings.SORT):
        query_dsl['sort'] = [settings.sort_options.get(args.pop(settings.SORT))]

    # Check for empty query
    if not any(v is not None for v in args.values()):
        log.debug("Constructing match-all query")
        query_dsl['query'] = {"match_all": {}}
        return query_dsl

    freetext_query = _build_freetext_query(args.get(settings.FREETEXT_QUERY))
    yrke_bool_query = _build_yrkes_query(args.get(settings.OCCUPATION),
                                         args.get(settings.GROUP),
                                         args.get(settings.FIELD))
    kompetens_bool_query = _build_bool_should_query("krav.kompetenser.kod",
                                                    args.get(settings.SKILL))
    plats_bool_query = _build_plats_query(args.get(settings.MUNICIPALITY),
                                          args.get(settings.REGION))
    # sprak_bool_query =  _build_bool_should_query("erfarenhet.sprak.kod",
    #                                              args.get(settings.LANGUAGE))
    sprak_bool_query = None
    worktime_bool_query = _build_worktimeextent_should_query(
        args.get(settings.WORKTIME_EXTENT))
    timeframe_query = _build_timeframe_query(args.get(settings.PUBLISHED_AFTER),
                                             args.get(settings.PUBLISHED_BEFORE))

    query_dsl['query'] = {"bool": {"must": []}}

    if freetext_query:
        query_dsl['query']['bool']['must'].append(freetext_query)
    if yrke_bool_query:
        query_dsl['query']['bool']['must'].append(yrke_bool_query)
    if kompetens_bool_query:
        query_dsl['query']['bool']['must'].append(kompetens_bool_query)
    if plats_bool_query:
        query_dsl['query']['bool']['must'].append(plats_bool_query)
    if sprak_bool_query:
        query_dsl['query']['bool']['must'].append(sprak_bool_query)
    if worktime_bool_query:
        query_dsl['query']['bool']['must'].append(worktime_bool_query)
    if timeframe_query:
        query_dsl['query']['bool']['must'].append(timeframe_query)

    return query_dsl


def _build_freetext_query(querystring):
    return {
        "multi_match": {
            "query": querystring,
            "fields": ["beskrivning.information", "beskrivning.behov", "beskrivning.krav"]
        }
    } if querystring else None


def _build_yrkes_query(yrkesroller, yrkesgrupper, yrkesomraden):
    yrken = [] if not yrkesroller else yrkesroller
    yrkesgrupper = [] if not yrkesgrupper else yrkesgrupper
    yrkesomraden = [] if not yrkesomraden else yrkesomraden

    yrke_term_query = [{
        "term": {
            "yrkesroll.kod": {
                "value": y,
                "boost": 1.0}}} for y in yrken if y]
    yrke_term_query += [{
        "term": {
            "yrkesgrupp.kod": {
                "value": y,
                "boost": 1.0}}} for y in yrkesgrupper if y]
    yrke_term_query += [{
        "term": {
            "yrkesomrade.kod": {
                "value": y,
                "boost": 1.0}}} for y in yrkesomraden if y]

    if yrke_term_query:
        return {"bool": {"should": yrke_term_query}}
    else:
        return None


def _build_plats_query(kommunkoder, lanskoder):
    kommuner = [] if not kommunkoder else kommunkoder
    kommunlanskoder = []
    for lanskod in lanskoder if lanskoder is not None else []:
        kommun_results = taxonomy.find_concepts(None, lanskod,
                                                settings.taxonomy_type.get(
                                                    settings.MUNICIPALITY)).get(
                                                        'hits', [])
        kommunlanskoder += [entitet['_source']['id'] for entitet in kommun_results]

    # OBS: Casting kommunkod values to ints the way currently stored in elastic
    plats_term_query = [{"term": {
        "arbetsplatsadress.kommunkod": {
            "value": int(kkod), "boost": 2.0}}} for kkod in kommuner]
    plats_term_query += [{"term": {
        "arbetsplatsadress.kommunkod": {
            "value": int(lkod), "boost": 1.0}}} for lkod in kommunlanskoder]
    return {"bool": {"should": plats_term_query}} if plats_term_query else None


def _build_timeframe_query(from_datetime, to_datetime):
    if not from_datetime and not to_datetime:
        return None
    range_query = {"range": {"publiceringsdatum": {}}}
    if from_datetime:
        range_query['range']['publiceringsdatum']['gte'] = _datetime2millis(from_datetime)
    if to_datetime:
        range_query['range']['publiceringsdatum']['lte'] = _datetime2millis(to_datetime)
    return range_query


def _datetime2millis(utc_time):
    millis = (utc_time - datetime(1970, 1, 1)).total_seconds() * 1000  # We want millis
    return int(millis)


def _build_worktimeextent_should_query(lista):
    arbetstidskoder = [] if not lista else lista

    term_query = [{"term": {
        "arbetstidstyp.kod": {"value": kod}}} for kod in arbetstidskoder]

    return {"bool": {"should": term_query}} if term_query else None


def _build_bool_should_query(key, itemlist):
    items = [] if not itemlist else itemlist

    term_query = [{"term": {key: {"value": item}}} for item in items]

    return {"bool": {"should": term_query}} if term_query else None
