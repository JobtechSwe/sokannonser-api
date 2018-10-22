import logging
import json
from sokannonser import settings
from sokannonser.repository import elastic

log = logging.getLogger(__name__)


def find_annonser(args):
    query_dsl = _parse_args(args)
    log.debug(json.dumps(query_dsl, indent=2))
    query_result = elastic.search(index=settings.ES_AURANEST, body=query_dsl)
    return query_result.get('hits', {})


def autocomplete(querystring):
    return []


def _parse_args(args):
    query_dsl = dict()
    query_dsl['from'] = args.pop(settings.OFFSET, 0)
    query_dsl['size'] = args.pop(settings.LIMIT, 10)
    # Remove api-key from args to make sure an empty query can occur
    args.pop(settings.APIKEY)

    # Make sure to only serve published ads
    query_dsl['query'] = {
        'bool': {
            'must': [],
            'filter': [{'bool': {'must_not': {'exists': {'field': 'source.removedAt'}}}}]
        },
    }

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
