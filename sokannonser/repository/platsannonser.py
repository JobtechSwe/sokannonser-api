import logging
import json
import time
from flask_restplus import abort
from elasticsearch import exceptions
from valuestore import taxonomy
from sokannonser import settings
from sokannonser.repository import elastic

log = logging.getLogger(__name__)


def get_stats_for(taxonomy_type):
    log.info("Looking for %s" % taxonomy_type)
    value_path = {
        taxonomy.JobtechTaxonomy.OCCUPATION_NAME: "yrkesroll.taxonomi-kod.keyword",
        taxonomy.JobtechTaxonomy.OCCUPATION_GROUP: "yrkesgrupp.taxonomi-kod.keyword",
        taxonomy.JobtechTaxonomy.OCCUPATION_FIELD: "yrkesomrade.taxonomi-kod.keyword",
        taxonomy.JobtechTaxonomy.SKILL: "krav.kompetenser.taxonomi-kod.keyword",
        taxonomy.JobtechTaxonomy.WORKTIME_EXTENT: "arbetstidstyp.taxonomi-kod.keyword",
        taxonomy.JobtechTaxonomy.MUNICIPALITY: "arbetsplatsadress.taxonomi-kommun.keyword",
        taxonomy.JobtechTaxonomy.COUNTY: "arbetsplatsadress.taxonomi-lan.keyword"
    }
    # Make sure we don't crash if we want to stat on missing type
    if taxonomy_type not in value_path:
        log.warning("Taxonomy type %s not configured for aggs." % taxonomy_type)
        return {}

    aggs_query = {
        "from": 0, "size": 0,
        "query": {
            "bool": {
                "must": [{ "match_all": {}}],
                'filter': [
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
            }
        },
        "aggs": {
            "antal_annonser": {
                "terms": {"field": value_path[taxonomy_type], "size": 5000},
            }
        }
    }
    log.debug('aggs_query', aggs_query)
    aggs_result = elastic.search(index=settings.ES_INDEX, body=aggs_query)
    code_count = {
        item['key']: item['doc_count']
        for item in aggs_result['aggregations']['antal_annonser']['buckets']}
    return code_count


def find_platsannonser(args, querybuilder, start_time=0):
    query_dsl = querybuilder.parse_args(args)
    log.debug(json.dumps(query_dsl, indent=2))
    log.debug("Query constructed after %d milliseconds." % (int(time.time()*1000)-start_time))

    try:
        query_result = elastic.search(index=settings.ES_INDEX, body=query_dsl)
        log.debug("Elastic results after %d milliseconds." % (int(time.time()*1000)-start_time))
    except exceptions.ConnectionError as e:
        logging.exception('Failed to connect to elasticsearch: %s' % str(e))
        abort(500, 'Failed to establish connection to database')
        return
    results = query_result.get('hits', {})
    results['took'] = query_result.get('took', 0)
    if 'aggregations' in query_result:
        results['positions'] = int(query_result.get('aggregations', {})
                                   .get('positions', {}).get('value', 0))
        results['aggs'] = querybuilder.filter_aggs(query_result.get('aggregations', {}),
                                                   args.get(settings.FREETEXT_QUERY))

        for stat in args.get(settings.STATISTICS) or []:
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

    # log.debug(json.dumps(results, indent=2))
    return results
