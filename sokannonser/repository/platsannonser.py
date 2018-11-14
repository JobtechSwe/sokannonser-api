import logging
from flask_restplus import abort
from elasticsearch import exceptions
from valuestore import taxonomy
from valuestore.taxonomy import tax_type
from sokannonser import settings
from sokannonser.repository import elastic
import json

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
        log.warning("Taxonomy type %s not configured for aggs." % taxonomy_type)
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


def find_platsannonser(args, querybuilder):
    query_dsl = querybuilder.parse_args(args)
    log.debug(json.dumps(query_dsl, indent=2))
    try:
        query_result = elastic.search(index=settings.ES_INDEX, body=query_dsl)
    except exceptions.ConnectionError as e:
        logging.exception('Failed to connect to elasticsearch: %s' % str(e))
        abort(500, 'Failed to establish connection to database')
        return
    results = query_result.get('hits', {})
    if 'aggregations' in query_result:
        results['positions'] = int(query_result.get('aggregations', {})
                                   .get('positions', {}).get('value', 0))
        results['aggs'] = querybuilder.filter_aggs(query_result.get('aggregations', {})
                                                   .get('complete', {}).get('buckets', []),
                                                   args.get(settings.FREETEXT_QUERY))
        for stat in args.get(settings.STATISTICS) if args.get(settings.STATISTICS) else []:
            if 'stats' not in results:
                results['stats'] = []
            results['stats'].append({
                "type": stat,
                "values": [
                    {
                        "term": taxonomy.get_term(elastic, stat, b['key']),
                        "code": b['key'],
                        "count": b['doc_count']}
                    for b in query_result.get('aggregations',
                                              {}).get(stat, {}).get('buckets', [])
                ]

            })
    log.debug(json.dumps(results, indent=2))
    return results
