import logging
import json
import time
from flask_restplus import abort
from elasticsearch import exceptions
from sokannonser import settings
from sokannonser.repository import elastic, taxonomy
from sokannonser.rest.model import fields
from sokannonser.repository.querybuilder import ttc

log = logging.getLogger(__name__)


def get_stats_for(taxonomy_type):
    value_path = {
        taxonomy.OCCUPATION: "%s.%s.keyword" %
        (fields.OCCUPATION, fields.LEGACY_AMS_TAXONOMY_ID),
        taxonomy.GROUP: "%s.%s.keyword" % (
            fields.OCCUPATION_GROUP, fields.LEGACY_AMS_TAXONOMY_ID),
        taxonomy.FIELD: "%s.%s.keyword" % (
            fields.OCCUPATION_FIELD, fields.LEGACY_AMS_TAXONOMY_ID),
        taxonomy.SKILL: "%s.%s.keyword" % (fields.MUST_HAVE_SKILLS,
                                           fields.LEGACY_AMS_TAXONOMY_ID),
        taxonomy.MUNICIPALITY: "%s.keyword" % fields.WORKPLACE_ADDRESS_MUNICIPALITY,
        taxonomy.REGION: "%s.keyword" % fields.WORKPLACE_ADDRESS_REGION
    }
    # Make sure we don't crash if we want to stat on missing type
    for tt in taxonomy_type:
        if tt not in value_path:
            log.warning("Taxonomy type \"%s\" not configured for aggs." % taxonomy_type)
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
                    {
                        'term': {
                            fields.REMOVED: False
                        }
                    },
                ]
            }
        },
        "aggs": {
            "antal_annonser": {
                "terms": {"field": value_path[taxonomy_type[0]], "size": 50},
            }
        }
    }
    log.debug('aggs_query: %s' % json.dumps(aggs_query))
    aggs_result = elastic.search(index=settings.ES_INDEX, body=aggs_query)

    code_count = {
        item['key']: item['doc_count']
        for item in aggs_result['aggregations']['antal_annonser']['buckets']}
    return code_count


def find_platsannonser(args, querybuilder, start_time=0, x_fields=None):
    if start_time == 0:
        start_time = int(time.time() * 1000)
    query_dsl = querybuilder.parse_args(args, x_fields)
    log.debug("Query constructed after %d milliseconds."
              % (int(time.time() * 1000) - start_time))
    try:
        # First pass, find highest score:
        if args.get(settings.MIN_RELEVANCE):
            max_score_query = query_dsl.copy()
            max_score_query['from'] = 0
            max_score_query['size'] = 1
            max_score_query['track_total_hits'] = False
            del max_score_query['aggs']
            del max_score_query['sort']
            max_score_result = elastic.search(index=settings.ES_INDEX,
                                              body=max_score_query)
            max_score = max_score_result.get('hits', {}).get('max_score')
            if max_score:
                query_dsl['min_score'] = max_score * args.get(settings.MIN_RELEVANCE)
        log.debug("ARGS %s => QUERY: %s" % (args, json.dumps(query_dsl)))
        query_result = elastic.search(index=settings.ES_INDEX, body=query_dsl)
        log.debug("Elastic results after %d milliseconds."
                  % (int(time.time() * 1000) - start_time))
    except exceptions.ConnectionError as e:
        logging.exception('Failed to connect to elasticsearch: %s' % str(e))
        abort(500, 'Failed to establish connection to database')
        return

    if args.get(settings.FREETEXT_QUERY):
        query_result['concepts'] = \
            _extract_concept_from_concepts(
                ttc.text_to_concepts(args.get(settings.FREETEXT_QUERY))
            )

    log.debug("Elasticsearch reports: took=%d, timed_out=%s"
              % (query_result.get('took', 0), query_result.get('timed_out', '')))
    return transform_platsannons_query_result(args, query_result, querybuilder)


def _extract_concept_from_concepts(concepts):
    main_concepts = dict()
    for key, value in concepts.items():
        main_concepts[key] = [v['concept'].lower() for v in value]
    return main_concepts


def _format_ad(result):
        source = result.get('_source')
        if source:
            try:
                source[fields.AD_URL] = "%s%s" % (settings.BASE_PB_URL,
                                                  source[fields.ID])
                print("Setting url:", source[fields.AD_URL])
                # Remove personal number
                org_nr = source['employer']['organization_number']
                if org_nr and int(org_nr[2]) < 2:
                    source['employer']['organization_number'] = None
            except KeyError:
                pass
            except ValueError:
                pass
        return source


def fetch_platsannons(ad_id):
    try:
        query_result = elastic.get(index=settings.ES_INDEX, id=ad_id, ignore=404)
        if query_result and '_source' in query_result:
            return _format_ad(query_result)
        else:
            ext_id_query = {
                'query': {
                    'term': {
                        fields.EXTERNAL_ID: ad_id
                    }
                }
            }
            query_result = elastic.search(index=settings.ES_INDEX, body=ext_id_query)
            hits = query_result.get('hits', {}).get('hits', [])
            if hits:
                return _format_ad(hits[0])

            log.info("Job ad %s not found, returning 404 message" % ad_id)
            abort(404, 'Ad not found')
    except exceptions.NotFoundError:
        logging.exception('Failed to find id: %s' % ad_id)
        abort(404, 'Ad not found')
        return
    except exceptions.ConnectionError as e:
        logging.exception('Failed to connect to elasticsearch: %s' % str(e))
        abort(500, 'Failed to establish connection to database')
        return


def transform_platsannons_query_result(args, query_result, querybuilder):
    results = query_result.get('hits', {})
    results['took'] = query_result.get('took', 0)
    results['concepts'] = query_result.get('concepts', {})
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

    # create_found_in_enriched(results, query_result)
    _modify_results(results)

    # log.debug(json.dumps(results, indent=2))
    return results


def create_found_in_enriched(results, query_result):
    found_in_enriched = False
    freetext_concepts_node = query_result.get('concepts', {})

    input_type_vals = []
    type_names = ['occupation', 'skill', 'trait']

    for type_name in type_names:
        if type_name in freetext_concepts_node:
            input_type_vals.extend(freetext_concepts_node[type_name])
        must_key = '%s_must' % type_name
        if must_key in freetext_concepts_node:
            input_type_vals.extend(freetext_concepts_node[must_key])

    if len(input_type_vals) == 0:
        for hit in results['hits']:
            hit['_source']['found_in_enriched'] = False
        return

    for hit in results['hits']:
        enriched_node = hit['_source'].get('keywords', {}).get('enriched', {})
        enriched_vals = []
        for type_name in type_names:
            enriched_vals.extend(enriched_node.get(type_name, {}))

        for type_val in input_type_vals:
            if type_val in enriched_vals:
                found_in_enriched = True
                break

        hit['_source']['found_in_enriched'] = found_in_enriched


def _modify_results(results):
    for hit in results['hits']:
        try:
            hit['_source'] = _format_ad(hit)
        except KeyError:
            pass
        except ValueError:
            pass
