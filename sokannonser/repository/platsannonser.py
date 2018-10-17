import logging
from flask_restplus import abort
from elasticsearch import exceptions
from valuestore import taxonomy
from valuestore.taxonomy import tax_type
from sokannonser import settings
from sokannonser.repository import elastic
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
        results['positions'] = int(query_result.get('aggregations', {})
                                   .get('positions', {}).get('value', 0))
        results['aggs'] = _filter_aggs(query_result.get('aggregations', {})
                                       .get('complete', {}).get('buckets', []),
                                       args.get(settings.FREETEXT_QUERY))
        for stat in args.get(settings.STATISTICS):
            if 'stats' not in results:
                results['stats'] = []
            results['stats'].append({
                "type": stat,
                "values": [
                    {
                        "term": taxonomy.get_term(elastic, stat, b['key']),
                        "kod": b['key'],
                        "count": b['doc_count']}
                    for b in query_result.get('aggregations',
                                              {}).get(stat, {}).get('buckets', [])
                ]

            })
    return results


def _filter_aggs(aggs, freetext):
    fwords = freetext.split(' ') if freetext else []
    filtered_aggs = []
    for agg in aggs:
        if not agg.get('key') in fwords:
            filtered_aggs.append(agg)

    return filtered_aggs


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
    must_queries.append(_build_timeframe_query(args.get(settings.PUBLISHED_AFTER),
                                               args.get(settings.PUBLISHED_BEFORE)))
    must_queries.append(_build_plats_query(args.get(taxonomy.MUNICIPALITY),
                                           args.get(taxonomy.REGION)))
    must_queries.append(_build_generic_query("krav.kompetenser.kod",
                                             args.get(taxonomy.SKILL)))
    must_queries.append(_build_generic_query("arbetstidstyp.kod",
                                             args.get(taxonomy.WORKTIME_EXTENT)))
    must_queries.append(_build_generic_query("korkort.kod",
                                             args.get(taxonomy.DRIVING_LICENCE)))
    must_queries.append(_build_generic_query("anstallningstyp.kod",
                                             args.get(taxonomy.EMPLOYMENT_TYPE)))

    # TODO: Maybe check if NO skills are listed in ad instead?
    if args.get(settings.NO_EXPERIENCE):
        must_queries.append({"term": {"erfarenhet_kravs": False}})

    query_dsl = _assemble_queries(query_dsl, must_queries)

    for stat in args.get(settings.STATISTICS):
        query_dsl['aggs'][stat] = {
            "terms": {
                "field": settings.stats_options[stat],
                "size": args.get(settings.STAT_LMT) if args.get(settings.STAT_LMT) else 5
            }
        }

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
    complete_string = args.get(settings.TYPEAHEAD_QUERY)
    query_dsl['aggs'] = {
        "positions": {
            "sum": {"field": "antal_platser"}
        }
    }
    if complete_string:
        complete = complete_string.split(' ')[-1]
        query_dsl['aggs']['complete'] = {
            "terms": {
                "field": "keywords.raw",
                "size": 20,
                "include": "%s.*" % complete
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
    if not querystring:
        return None
    inc_words = ' '.join([w for w in querystring.split(' ') if not w.startswith('-')])
    exc_words = ' '.join([w[1:] for w in querystring.split(' ') if w.startswith('-')])
    shoulds = __freetext_fields(inc_words) if inc_words else None
    mustnts = __freetext_fields(exc_words) if exc_words else None
    ft_query = {"bool": {}}
    if shoulds:
        ft_query['bool']['should'] = shoulds
    if mustnts:
        ft_query['bool']['must_not'] = mustnts

    return ft_query


# Conveniance method to create list of queries for freetext (either should or must_not)
def __freetext_fields(searchword):
    return [
        {
            "match": {
                "rubrik": {
                    "query": searchword,
                    "boost": 3
                }
            }
        },
        {
            "match": {
                "arbetsgivare.namn": {
                    "query": searchword,
                    "boost": 2
                }
            }
        },
        {
            "match": {
                "keywords": {
                    "query": searchword,
                    "boost": 2
                }
            }
        },
        {
            "multi_match": {
                "query": searchword,
                "fields": ["beskrivning.information",
                           "beskrivning.behov",
                           "beskrivning.krav",
                           "beskrivning.annonstext"]
            }
        }
    ]


def _build_yrkes_query(yrkesroller, yrkesgrupper, yrkesomraden):
    yrken = [] if not yrkesroller else yrkesroller
    yrkesgrupper = [] if not yrkesgrupper else yrkesgrupper
    yrkesomraden = [] if not yrkesomraden else yrkesomraden

    yrke_term_query = [{
        "term": {
            "yrkesroll.kod": {
                "value": y,
                "boost": 2.0}}} for y in yrken if y and not y.startswith('-')]
    yrke_term_query += [{
        "term": {
            "yrkesgrupp.kod": {
                "value": y,
                "boost": 1.0}}} for y in yrkesgrupper if y and not y.startswith('-')]
    yrke_term_query += [{
        "term": {
            "yrkesomrade.kod": {
                "value": y,
                "boost": 1.0}}} for y in yrkesomraden if y and not y.startswith('-')]

    neg_yrke_term_query = [{
        "term": {
            "yrkesroll.kod": {
                "value": y[1:]}}} for y in yrken if y and y.startswith('-')]
    neg_yrke_term_query += [{
        "term": {
            "yrkesgrupp.kod": {
                "value": y[1:]}}} for y in yrkesgrupper if y and y.startswith('-')]
    neg_yrke_term_query += [{
        "term": {
            "yrkesomrade.kod": {
                "value": y[1:]}}} for y in yrkesomraden if y and y.startswith('-')]

    if yrke_term_query or neg_yrke_term_query:
        query = {'bool': {}}
        if yrke_term_query:
            query['bool']['should'] = yrke_term_query
        if neg_yrke_term_query:
            query['bool']['must_not'] = neg_yrke_term_query
        return query
    else:
        return None


def _build_plats_query(kommunkoder, lanskoder):
    kommuner = []
    neg_komm = []
    for kkod in kommunkoder if kommunkoder else []:
        if kkod.startswith('-'):
            neg_komm.append(kkod[1:])
        else:
            kommuner.append(kkod)

    kommunlanskoder = []
    for lanskod in lanskoder if lanskoder is not None else []:
        if lanskod.startswith('-'):
            kommun_results = taxonomy.find_concepts(elastic, None, lanskod[1:],
                                                    tax_type.get(taxonomy.MUNICIPALITY)
                                                    ).get('hits', {}).get('hits', [])
            neg_komm += [entitet['_source']['id'] for entitet in kommun_results]
        else:
            kommun_results = taxonomy.find_concepts(elastic, None, lanskod,
                                                    tax_type.get(taxonomy.MUNICIPALITY)
                                                    ).get('hits', {}).get('hits', [])
            kommunlanskoder += [entitet['_source']['id'] for entitet in kommun_results]

    plats_term_query = [{"term": {
        "arbetsplatsadress.kommunkod": {
            "value": kkod, "boost": 2.0}}} for kkod in kommuner]
    plats_term_query += [{"term": {
        "arbetsplatsadress.kommunkod": {
            "value": lkod, "boost": 1.0}}} for lkod in kommunlanskoder]
    plats_bool_query = {"bool": {"should": plats_term_query}} if plats_term_query else {}
    if neg_komm:
        neg_plats_term_query = [{"term": {
            "arbetsplatsadress.kommunkod": {
                "value": kkod}}} for kkod in neg_komm]
        if 'bool' not in plats_bool_query:
            plats_bool_query['bool'] = {}
        plats_bool_query['bool']['must_not'] = neg_plats_term_query
    return plats_bool_query


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


def _build_generic_query(key, itemlist):
    items = [] if not itemlist else itemlist

    term_query = [{"term": {key: {"value": item}}}
                  for item in items if not item.startswith('-')]

    neg_term_query = [{"term": {key: {"value": item[1:]}}}
                      for item in items if item.startswith('-')]

    if term_query or neg_term_query:
        query = {'bool': {}}
        if term_query:
            query['bool']['should'] = term_query
        if neg_term_query:
            query['bool']['must_not'] = neg_term_query
        return query

    return None
