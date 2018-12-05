import logging
import json
from flask_restplus import abort
from elasticsearch import exceptions
from sokannonser import settings
from sokannonser.repository import elastic

log = logging.getLogger(__name__)


def find_annonser(args):
    aggregates = _statistics(args.pop(settings.STATISTICS),
                             args.pop(settings.STAT_LMT))
    query_dsl = _parse_args(args)
    log.debug(json.dumps(query_dsl, indent=2))
    if aggregates:
        query_dsl['aggs'] = aggregates
    try:
        query_result = elastic.search(index=settings.ES_AURANEST, body=query_dsl)
    except exceptions.ConnectionError as e:
        logging.exception('Failed to connect to elasticsearch: %s' % str(e))
        abort(500, 'Failed to establish connection to database')
        return
    log.debug(json.dumps(query_result, indent=2))
    return query_result


def autocomplete(querystring):
    if not querystring:
        querystring = ''
    without_last = ' '.join(querystring.split(' ')[:-1])
    query_dsl = _parse_args({
        settings.FREETEXT_QUERY: without_last,
        settings.LIMIT: 0,
        settings.SHOW_EXPIRED: 'false'
    })
    complete = querystring.split(' ')[-1]
    query_dsl['aggs'] = {'complete': {
        "terms": {
            "field": "keywords.raw",
            "size": 20,
            "include": "%s.*" % complete
        }
    }}
    query_result = elastic.search(index=settings.ES_AURANEST, body=query_dsl)
    if 'aggregations' in query_result:
        return [c['key'] for c in query_result.get('aggregations', {})
                                              .get('complete', {})
                                              .get('buckets', [])]
    return []


def _statistics(agg_fields, agg_size):
    aggs = dict()
    size = agg_size if agg_size else 10

    for agg in agg_fields if agg_fields else []:
        aggs[agg] = {
            "terms": {
                "field": settings.auranest_stats_options[agg],
                "size": size
            }
        }
    return aggs


def _parse_args(args):
    args = dict(args)
    query_dsl = dict()
    query_dsl['from'] = args.pop(settings.OFFSET, 0)
    query_dsl['size'] = args.pop(settings.LIMIT, 10)
    # Remove api-key from args to make sure an empty query can occur
    args.pop(settings.APIKEY, None)

    # Make sure to only serve published ads
    query_dsl['query'] = {
        'bool': {
            'must': [],
        }
    }
    query_dsl['collapse'] = {
        "field": "group.id",
        "inner_hits": {
            "name": "other",
            "size": 20
        }
    }
    if args.pop(settings.SHOW_EXPIRED) != 'true':
        query_dsl['query']['bool']['filter'] = \
            [{'bool': {'must_not': {'exists': {'field': 'source.removedAt'}}}}]

    if args.get(settings.SORT):
        query_dsl['sort'] = [settings.auranest_sort_options.get(args.pop(settings.SORT))]

    # Check for empty query
    if not any(v is not None for v in args.values()):
        log.debug("Constructing match-all query")
        query_dsl['query']['bool']['must'].append({'match_all': {}})
        return query_dsl

    freetext_query = _build_freetext_query(args.get(settings.FREETEXT_QUERY))
    if freetext_query:
        query_dsl['query']['bool']['must'].append(freetext_query)
    return query_dsl


def __freetext_fields(searchword):
    return [
        {
            "match": {
                "header": {
                    "query": searchword,
                    "boost": 3
                }
            }
        },
        {
            "match": {
                "title.freetext": {
                    "query": searchword,
                    "boost": 3
                }
            }
        },
        {
            "match": {
                "keywords": {
                    "query": searchword,
                    "boost": 1
                }
            }
        },
        {
            "match": {
                "employer.name": {
                    "query": searchword,
                    "boost": 2
                }
            }
        },
        {
            "match": {
                "content.text": {
                    "query": searchword,
                }
            }
        }
    ]


def _build_freetext_query(freetext):
    if not freetext:
        return None
    inc_words = ' '.join([w for w in freetext.split(' ') if not w.startswith('-')])
    exc_words = ' '.join([w[1:] for w in freetext.split(' ') if w.startswith('-')])
    shoulds = __freetext_fields(inc_words) if inc_words else None
    mustnts = __freetext_fields(exc_words) if exc_words else None
    ft_query = {"bool": {}}
    if shoulds:
        ft_query['bool']['should'] = shoulds
    if mustnts:
        ft_query['bool']['must_not'] = mustnts

    return ft_query if shoulds or mustnts else None
