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
    print(args.values())
    if not any(v is not None for v in args.values()):
        log.debug("Constructing match-all query")
        query_dsl['query']['bool']['must'].append({'match_all': {}})
        return query_dsl

    freetext_query = _build_freetext_query(args.get(settings.FREETEXT_QUERY))
    if freetext_query:
        query_dsl['query']['bool']['must'].append(freetext_query)
    return query_dsl


def _build_freetext_query(freetext):
    return {
        "bool": {
            "should": [
                {
                    "match": {
                        "header": {
                            "query": freetext,
                            "boost": 3
                        }
                    }
                },
                {
                    "match": {
                        "title.freetext": {
                            "query": freetext,
                            "boost": 3
                        }
                    }
                },
                {
                    "match": {
                        "employer.name": {
                            "query": freetext,
                            "boost": 2
                        }
                    }
                },
                {
                    "match": {
                        "content.text": {
                            "query": freetext,
                        }
                    }
                }
            ]
        }
    } if freetext else None
