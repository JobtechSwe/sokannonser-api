import logging
import json
import time
from flask_restplus import abort
from elasticsearch import exceptions
from valuestore import taxonomy
from sokannonser import settings
from sokannonser.repository import elastic
from sokannonser.rest.model import fields

log = logging.getLogger(__name__)


def get_stats_for(taxonomy_type):
    log.info("Looking for %s" % taxonomy_type)
    value_path = {
        taxonomy.JobtechTaxonomy.OCCUPATION_NAME: "%s.%s.keyword" % (fields.OCCUPATION, fields.LEGACY_AMS_TAXONOMY_ID),
        taxonomy.JobtechTaxonomy.OCCUPATION_GROUP: "%s.%s.keyword" % (
        fields.OCCUPATION_GROUP, fields.LEGACY_AMS_TAXONOMY_ID),
        taxonomy.JobtechTaxonomy.OCCUPATION_FIELD: "%s.%s.keyword" % (
        fields.OCCUPATION_FIELD, fields.LEGACY_AMS_TAXONOMY_ID),
        taxonomy.JobtechTaxonomy.SKILL: "%s.%s.keyword" % (fields.MUST_HAVE_SKILLS, fields.LEGACY_AMS_TAXONOMY_ID),
        taxonomy.JobtechTaxonomy.WORKTIME_EXTENT: "%s.%s.keyword" % (
        fields.WORKING_HOURS_TYPE, fields.LEGACY_AMS_TAXONOMY_ID),
        taxonomy.JobtechTaxonomy.MUNICIPALITY: "%s.keyword" % fields.WORKPLACE_ADDRESS_MUNICIPALITY,
        taxonomy.JobtechTaxonomy.MUNICIPALITY: "%s.keyword" % fields.WORKPLACE_ADDRESS_MUNICIPALITY,
        taxonomy.JobtechTaxonomy.REGION: "%s.keyword" % fields.WORKPLACE_ADDRESS_REGION
    }
    # Make sure we don't crash if we want to stat on missing type
    if taxonomy_type not in value_path:
        log.warning("Taxonomy type %s not configured for aggs." % taxonomy_type)
        return {}

    aggs_query = {
        "from": 0, "size": 0,
        "query": {
            "bool": {
                "must": [{"match_all": {}}],
                'filter': [
                    {
                        'range': {
                            fields.PUBLICATION_DATE: {
                                'lte': 'now/m'
                            }
                        }
                    },
                    {
                        'range': {
                            fields.LAST_PUBLICATION_DATE: {
                                'gte': 'now/m'
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
    if start_time == 0:
        start_time = int(time.time() * 1000)
    query_dsl = querybuilder.parse_args(args)
    log.debug(json.dumps(query_dsl, indent=2))
    log.debug("Query constructed after %d milliseconds."
              % (int(time.time() * 1000) - start_time))

    log.debug(json.dumps(query_dsl, indent=2))
    try:
        query_result = elastic.search(index=settings.ES_INDEX, body=query_dsl)
        log.debug("Elastic results after %d milliseconds."
                  % (int(time.time() * 1000) - start_time))
    except exceptions.ConnectionError as e:
        logging.exception('Failed to connect to elasticsearch: %s' % str(e))
        abort(500, 'Failed to establish connection to database')
        return
    log.debug("Elasticsearch reports: took=%d, timed_out=%s"
              % (query_result.get('took', 0), query_result.get('timed_out', '')))
    return transform_platsannons_query_result(args, query_result, querybuilder)


def fetch_platsannons(id):
    try:
        query_result = elastic.get(settings.ES_INDEX, 'document', id)
        if query_result and '_source' in query_result:
            source = query_result['_source']
            keyword_node = source['keywords']
            try:
                del keyword_node['enriched']
            except KeyError:
                pass
            return source
    except exceptions.NotFoundError:
        logging.exception('Failed to find id: %s' % id)
        abort(404, 'Ad not found')
        return
    except exceptions.ConnectionError as e:
        logging.exception('Failed to connect to elasticsearch: %s' % str(e))
        abort(500, 'Failed to establish connection to database')
        return


def transform_platsannons_query_result(args, query_result, querybuilder):
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

    delete_ml_enriched_values(results)

    # log.debug(json.dumps(results, indent=2))
    return results


def delete_ml_enriched_values(results):
    for hit in results['hits']:
        keyword_node = hit['_source']['keywords']
        try:
            del keyword_node['enriched']
        except KeyError:
            pass
