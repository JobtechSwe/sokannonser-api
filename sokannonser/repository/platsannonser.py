import logging
from flask_restplus import abort
from elasticsearch import exceptions
from valuestore import taxonomy
from valuestore.taxonomy import tax_type
from sokannonser import settings
from . import elastic
import json
from datetime import datetime

log = logging.getLogger(__name__)


def get_stats_for(taxonomy_type):
    log.info("Looking for %s" % taxonomy_type)
    value_path = {
        tax_type[taxonomy.OCCUPATION]: "yrkesroll.kod.keyword",
        tax_type[taxonomy.GROUP]: "yrkesgrupp.kod.keyword",
        tax_type[taxonomy.FIELD]: "yrkesomrade.kod.keyword",
        tax_type[taxonomy.SKILL]: "krav.kompetenser.kod.keyword",
        tax_type[taxonomy.WORKTIME_EXTENT]: "arbetstidstyp.kod.keyword",
        tax_type[taxonomy.MUNICIPALITY]: "arbetsplatsadress.kommun.keyword",
        tax_type[taxonomy.REGION]: "arbetsplatsadress.lan.keyword"
    }
    # Make sure we don't crash if we want to stat on missing type
    if taxonomy_type not in value_path:
        log.warn("Taxonomy type %s not configured for aggs." % taxonomy_type)
        return {}

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
    results = query_result.get('hits', {})
    if 'aggregations' in query_result:
        results['aggs'] = query_result.get('aggregations', {}) \
                            .get('complete', {}).get('buckets', [])
    return results


def _parse_args(args):
    query_dsl = _bootstrap_query(args)

    # Check for empty query
    if not any(v is not None for v in args.values()):
        log.debug("Constructing match-all query")
        query_dsl['query']['bool']['must'].append({'match_all': {}})
        return query_dsl

    must_queries = []

    must_queries.append(_build_freetext_query(args.get(settings.FREETEXT_QUERY)))
    must_queries.append(_build_yrkes_query(args.get(taxonomy.OCCUPATION),
                                           args.get(taxonomy.GROUP),
                                           args.get(taxonomy.FIELD)))
    must_queries.append(_build_bool_should_query("krav.kompetenser.kod",
                                                 args.get(taxonomy.SKILL)))
    must_queries.append(_build_plats_query(args.get(taxonomy.MUNICIPALITY),
                                           args.get(taxonomy.REGION)))
    must_queries.append(_build_worktime_query(args.get(taxonomy.WORKTIME_EXTENT)))
    must_queries.append(_build_timeframe_query(args.get(settings.PUBLISHED_AFTER),
                                               args.get(settings.PUBLISHED_BEFORE)))
    must_queries.append(_build_drivers_licens_query(args.get(taxonomy.DRIVING_LICENCE)))
    must_queries.append(_build_employment_type_query(args.get(taxonomy.EMPLOYMENT_TYPE)))
    # sprak_bool_query =  _build_bool_should_query("erfarenhet.sprak.kod",
    #                                              args.get(taxonomy.LANGUAGE))

    # TODO: Maybe check if NO skills are listed in ad instead?
    if args.get(settings.NO_EXPERIENCE):
        must_queries.append({"term": {"erfarenhet_kravs": False}})

    query_dsl = _assemble_queries(query_dsl, must_queries)

    return query_dsl


def _bootstrap_query(args):
    query_dsl = dict()
    query_dsl['from'] = args.pop(settings.OFFSET, 0)
    query_dsl['size'] = args.pop(settings.LIMIT, 10)
    # Remove api-key from args to make sure an empty query can occur
    args.pop(settings.APIKEY)

    # Make sure to only serve published ads
    query_dsl['query'] = {
        'bool': {
            'must': [],
            'filter': [
                # {'term': {'status.publicerad': True}},
                {
                    'range': {
                        'publiceringsdatum': {
                            'lte': 'now'
                        }
                    }
                },
                {
                    'range': {
                        'status.sista_publiceringsdatum': {
                            'gte': 'now'
                        }
                    }
                },
            ]
        },
    }
    complete = args.pop(settings.TYPEAHEAD_QUERY)
    if complete:
        query_dsl['aggs'] = {
            "complete": {
                "terms": {
                    "field": "keywords.raw",
                    "size": 20,
                    "include": "%s.*" % complete
                }
            }
        }

    if args.get(settings.SORT):
        query_dsl['sort'] = [settings.sort_options.get(args.pop(settings.SORT))]
    return query_dsl


def _assemble_queries(query_dsl, additional_queries):
    for query in additional_queries:
        if query:
            query_dsl['query']['bool']['must'].append(query)
    return query_dsl


def _build_freetext_query(querystring):
    return {
        "bool": {
            "should": [
                {
                    "match": {
                        "rubrik": {
                            "query": querystring,
                            "boost": 3
                        }
                    }
                },
                {
                    "match": {
                        "arbetsgivare.namn": {
                            "query": querystring,
                            "boost": 2
                        }
                    }
                },
                {
                    "match": {
                        "keywords": {
                            "query": querystring,
                            "boost": 2
                        }
                    }
                },
                {
                    "multi_match": {
                        "query": querystring,
                        "fields": ["beskrivning.information",
                                   "beskrivning.behov",
                                   "beskrivning.krav",
                                   "beskrivning.annonstext"]
                    }
                }
            ]
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
        kommun_results = taxonomy.find_concepts(elastic, None, lanskod,
                                                tax_type.get(taxonomy.MUNICIPALITY)
                                                ).get('hits', {}).get('hits', [])
        kommunlanskoder += [entitet['_source']['id'] for entitet in kommun_results]

    # Verify kommunkod is string
    plats_term_query = [{"term": {
        "arbetsplatsadress.kommunkod": {
            "value": kkod, "boost": 2.0}}} for kkod in kommuner]
    plats_term_query += [{"term": {
        "arbetsplatsadress.kommunkod": {
            "value": lkod, "boost": 1.0}}} for lkod in kommunlanskoder]
    return {"bool": {"should": plats_term_query}} if plats_term_query else None


def _build_drivers_licens_query(license_types):
    dlic_query = []
    if license_types:
        for license_type in license_types:
            dlic_query.append({
                "term": {
                    "korkort.kod": {"value": license_type}
                }
            })
    return {"bool": {"should": dlic_query}} if dlic_query else None


def _build_employment_type_query(emp_types):
    emp_query = []
    if emp_types:
        for emp_type in emp_types:
            emp_query.append({
                "term": {
                    "anstallningstyp.kod": {"value": emp_type}
                }
            })
    return {"bool": {"should": emp_query}} if emp_query else None


def _build_timeframe_query(from_datetime, to_datetime):
    if not from_datetime and not to_datetime:
        return None
    range_query = {"range": {"publiceringsdatum": {}}}
    if from_datetime:
        range_query['range']['publiceringsdatum']['gte'] = from_datetime.isoformat()
    if to_datetime:
        range_query['range']['publiceringsdatum']['lte'] = to_datetime.isoformat()
    return range_query


# Deprecated. Previously used to build timeframe queries
def _datetime2millis(utc_time):
    millis = (utc_time - datetime(1970, 1, 1)).total_seconds() * 1000  # We want millis
    return int(millis)


def _build_worktime_query(lista):
    arbetstidskoder = [] if not lista else lista

    term_query = [{"term": {
        "arbetstidstyp.kod": {"value": kod}}} for kod in arbetstidskoder]

    return {"bool": {"should": term_query}} if term_query else None


def _build_bool_should_query(key, itemlist):
    items = [] if not itemlist else itemlist

    term_query = [{"term": {key: {"value": item}}} for item in items]

    return {"bool": {"should": term_query}} if term_query else None
