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
            "_source": ["id", "source.url", "source.site.name"],
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

    freetext_query = _build_query(args.get(settings.FREETEXT_QUERY),
                                  __freetext_fields)
    if freetext_query:
        query_dsl['query']['bool']['must'].append(freetext_query)
    place_query = _build_query(args.get(settings.PLACE),
                               __place_fields)
    if place_query:
        query_dsl['query']['bool']['must'].append(place_query)
    return query_dsl


def __freetext_fields(searchword):
    search_fields = ["header^3", "title.freetext^3", "keywords",
                     "employer.name^2", "content.text"]
    return [
        {
            "multi_match": {
                "query": searchword,
                "type": "cross_fields",
                "operator": "and",
                "fields": search_fields
            }
        }
    ]


def __place_fields(searchword):
    return [
        {
            "match": {
                "location.translations.sv-SE": searchword,
            }
        }
    ]


def _build_query(querystring, fields_method):
    if not querystring:
        return None
    inc_words = ' '.join([w for w in querystring.split(' ') if not w.startswith('-')])
    exc_words = ' '.join([w[1:] for w in querystring.split(' ') if w.startswith('-')])
    shoulds = fields_method(inc_words) if inc_words else None
    mustnts = fields_method(exc_words) if exc_words else None
    ft_query = {"bool": {}}
    if shoulds:
        ft_query['bool']['should'] = shoulds
    if mustnts:
        ft_query['bool']['must_not'] = mustnts

    return ft_query if shoulds or mustnts else None
