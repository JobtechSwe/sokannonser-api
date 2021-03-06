import logging
import json
import time
import io
import os
from flask_restx import abort
from flask import send_file
import requests
from elasticsearch import exceptions
from sokannonser import settings
from sokannonser.repository import elastic, taxonomy
from sokannonser.rest.model import fields
from operator import itemgetter

log = logging.getLogger(__name__)

currentdir = os.path.dirname(os.path.realpath(__file__)) + '/'


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
        taxonomy.MUNICIPALITY: "%s" % fields.WORKPLACE_ADDRESS_MUNICIPALITY_CODE,
        taxonomy.REGION: "%s" % fields.WORKPLACE_ADDRESS_REGION_CODE
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
                "terms": {"field": value_path[taxonomy_type[0]], "size": 5000},
            }
        }
    }
    log.debug('aggs_query: %s' % json.dumps(aggs_query))
    aggs_result = elastic.search(index=settings.ES_INDEX, body=aggs_query)

    code_count = {
        item['key']: item['doc_count']
        for item in aggs_result['aggregations']['antal_annonser']['buckets']}
    return code_count


def suggest(args, querybuilder):
    result = find_platsannonser(args, querybuilder, start_time=0, x_fields=None)
    if result.get('aggs'):
        # before only return one word, add prefix word here, will change the logic in future
        search_text = args[settings.FREETEXT_QUERY].strip()
        search_text_type = _check_search_word_type(search_text, querybuilder)
        if search_text_type == 'location' and not args[settings.TYPEAHEAD_QUERY].split(' ')[-1]:
            extra_words = suggest_extra_word(args, args[settings.TYPEAHEAD_QUERY].strip(), querybuilder)
            result['aggs'] = extra_words
        else:
            for item in result.get('aggs'):
                value = item['value']
                item['value'] = (args[settings.FREETEXT_QUERY] + ' ' + value).strip()
                item['found_phrase'] = (args[settings.FREETEXT_QUERY] + ' ' + value).strip()
    elif args.get(settings.TYPEAHEAD_QUERY):  # TODO: this elif is not covered by tests (2020-04-21)
        result = complete_suggest(args, querybuilder, start_time=0)
        if not result:
            result = phrase_suggest(args, querybuilder, start_time=0)
    return result


def suggest_extra_word(args, search_text, querybuilder):
    # input one word and suggest extra word
    search_text_type = _check_search_word_type(search_text, querybuilder)
    new_suggest_list = []
    if search_text_type:
        if search_text_type == 'location':
            second_suggest_type = 'occupation'
        else:
            second_suggest_type = 'location'  # TODO never executed by tests
        query_dsl = querybuilder.create_suggest_extra_word_query(search_text, search_text_type, second_suggest_type)
        log.debug('QUERY(suggest_extra_word): %s' % query_dsl)
        query_result = elastic.search(index=settings.ES_INDEX, body=query_dsl)
        results = query_result.get('aggregations').get('first_word').get('second_word').get('buckets')
        for result in results:
            if result.get('key') != 'sverige':
                new_suggest = {}
                new_suggest['value'] = search_text + ' ' + result.get('key')
                new_suggest['found_phrase'] = search_text + ' ' + result.get('key')
                new_suggest['type'] = search_text_type + '_' + second_suggest_type
                new_suggest['occurrences'] = result.get('doc_count')
                new_suggest_list.append(new_suggest)
    log.debug('List suggest: %s' % new_suggest_list)
    return new_suggest_list


def _check_search_word_type(search_text, querybuilder):
    # this function is used for checking input words type, return type location/skill/occupation
    query_dsl = querybuilder.create_check_search_word_type_query(search_text)
    log.debug('QUERY word_type: %s' % query_dsl)
    query_result = elastic.search(index=settings.ES_INDEX, body=query_dsl)
    result = query_result['aggregations']
    for key in result.keys():
        if result[key]['buckets']:
            return key.split('_')[-1]
    return None


def find_platsannonser(args, querybuilder, start_time=0, x_fields=None):
    if start_time == 0:
        start_time = int(time.time() * 1000)
    query_dsl = querybuilder.parse_args(args, x_fields)
    log.debug("Query constructed after %d milliseconds." % (int(time.time() * 1000) - start_time))
    try:
        # First pass, find highest score:
        if args.get(settings.MIN_RELEVANCE):  # TODO: not executed by tests
            max_score_query = query_dsl.copy()
            max_score_query['from'] = 0
            max_score_query['size'] = 1
            max_score_query['track_total_hits'] = False
            del max_score_query['aggs']
            del max_score_query['sort']
            max_score_result = elastic.search(index=settings.ES_INDEX, body=max_score_query)
            max_score = max_score_result.get('hits', {}).get('max_score')
            if max_score:
                query_dsl['min_score'] = (max_score - 1) * args.get(settings.MIN_RELEVANCE)
        log.info("ARGS: %s" % args)
        log.info("QUERY: %s" % json.dumps(query_dsl))
        query_result = elastic.search(index=settings.ES_INDEX, body=query_dsl)
        log.debug("(find_platsannonser)Elastic results after %d milliseconds." % (int(time.time() * 1000) - start_time))
    except exceptions.ConnectionError as e:
        log.exception(f'Failed to connect to elasticsearch: {e}')
        abort(500, 'Failed to establish connection to database')
        return

    if args.get(settings.FREETEXT_QUERY) \
            and not args.get(settings.X_FEATURE_DISABLE_SMART_FREETEXT):
        # First remove any phrases
        (phrases, qs) = querybuilder.extract_quoted_phrases(args.get(settings.FREETEXT_QUERY))
        query_result['concepts'] = \
            _extract_concept_from_concepts(
                querybuilder.ttc.text_to_concepts(qs)
            )

    log.debug("Elasticsearch reports: took: %d, timed_out: %s"
              % (query_result.get('took', 0), query_result.get('timed_out', '')))
    return transform_platsannons_query_result(args, query_result, querybuilder)


# TODO not called at all
def complete_suggest(args, querybuilder, start_time=0):
    if start_time == 0:
        start_time = int(time.time() * 1000)

    input_words = args.get(settings.TYPEAHEAD_QUERY)

    word_list = input_words.split()
    args_middle = args.copy()
    prefix_word = word_list[:-1] if word_list else ''
    if prefix_word:
        args_middle[settings.TYPEAHEAD_QUERY] = ' '.join(prefix_word)
        result = find_platsannonser(args_middle, querybuilder, start_time=0, x_fields=None)
        if not result.get('aggs'):
            return None

    word = word_list[-1] if word_list else ''
    if word_list and word_list[:-1]:
        prefix = ' '.join(input_words.split()[:-1])  # TODO not executed by tests
    else:
        prefix = ''

    query_dsl = querybuilder.create_auto_complete_suggester(word)

    log.debug("Query(complete_suggest) constructed after: %d milliseconds." % (int(time.time() * 1000) - start_time))
    try:
        log.debug("ARGS(complete_suggest): %s" % args)
        log.debug("QUERY(complete_suggest): %s" % json.dumps(query_dsl))
        query_result = elastic.search(index=settings.ES_INDEX, body=query_dsl)
        log.debug("Elastic(complete_suggest) results after: %d milliseconds." % (int(time.time() * 1000) - start_time))
    except exceptions.ConnectionError as e:
        log.exception(f'Failed to connect to elasticsearch: {e}')
        abort(500, 'Failed to establish connection to database')
        return

    log.debug("Elasticsearch(complete_suggest) reports. took: %d, timed_out: %s"
              % (query_result.get('took', 0), query_result.get('timed_out', '')))
    log.debug('QUERY(complete_suggest) result: %s' % query_result.get('suggest', {}))

    aggs = []
    suggests = query_result.get('suggest', {})

    for key in suggests:
        if suggests[key][0].get('options', []):
            for ads in suggests[key][0]['options']:
                value = prefix + ' ' + ads.get('text', '') if prefix else ads.get('text', '')
                aggs.append(
                    {
                        'value': value.strip(),
                        'found_phrase': value.strip(),
                        'type': key.split('-')[0],
                        'occurrences': 0
                    }
                )

    # check occurrences even i think it will take some trouble and stupid
    query_result['aggs'] = suggest_check_occurrence(aggs[:50], querybuilder)

    return query_result


def phrase_suggest(args, querybuilder, start_time=0):
    if start_time == 0:
        start_time = int(time.time() * 1000)

    input_words = args.get(settings.TYPEAHEAD_QUERY)
    query_dsl = querybuilder.create_phrase_suggester(input_words)

    log.debug("Query(phrase_suggest) constructed after: %d milliseconds." % (int(time.time() * 1000) - start_time))
    try:
        log.debug("ARGS(phrase_suggest): %s" % args)
        log.debug("QUERY(phrase_suggest): %s" % json.dumps(query_dsl))
        query_result = elastic.search(index=settings.ES_INDEX, body=query_dsl)
        log.debug("Elastic(phrase_suggest) results after: %d milliseconds." % (int(time.time() * 1000) - start_time))
    except exceptions.ConnectionError as e:
        log.exception(f'Failed to connect to elasticsearch: {e}')
        abort(500, 'Failed to establish connection to database')
        return

    log.debug("Elasticsearch(phrase_suggest) reports: took: %d, timed_out: %s"
              % (query_result.get('took', 0), query_result.get('timed_out', '')))

    aggs = []
    suggests = query_result.get('suggest', {})
    for key in suggests:
        if suggests[key][0].get('options', []):
            for ads in suggests[key][0]['options']:
                value = ads.get('text', '')
                aggs.append(
                    {
                        'value': value,
                        'found_phrase': value,
                        'type': key.split('.')[-1].split('_')[0],
                        'occurrences': 0
                    }
                )
    query_result['aggs'] = aggs[:10]

    # check occurrences even i think it will take some trouble and stupid
    query_result['aggs'] = suggest_check_occurrence(aggs[:50], querybuilder)

    return query_result


def suggest_check_occurrence(aggs, querybuilder):
    # check the frequency one by one, future will change it
    for agg in aggs:
        query_dsl = querybuilder.create_suggest_search(agg['value'])
        query_result = elastic.search(index=settings.ES_INDEX, body=query_dsl)
        occurrences = query_result.get('hits').get('total').get('value')
        agg['occurrences'] = occurrences

    aggs = sorted(aggs, key=itemgetter('occurrences'), reverse=True)
    return aggs


def _extract_concept_from_concepts(concepts):
    main_concepts = dict()
    for key, value in concepts.items():
        main_concepts[key] = [v['concept'].lower() for v in value]
    return main_concepts


def _format_ad(result):
    source = result.get('_source')
    if source:
        try:
            # Remove personal number
            # TODO: Not needed once loader (where this also happens) is deployed :
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
            log.debug('Ad found by la id: %s' % ad_id)
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
            if hits:  # TODO: never executed by tests
                log.debug('Ad found by external id: %s' % ad_id)
                return _format_ad(hits[0])

            log.info("Ad: %s not found, returning 404 message" % ad_id)
            abort(404, 'Ad not found')
    except exceptions.NotFoundError:
        log.exception('Failed to find id: %s' % ad_id)
        abort(404, 'Ad not found')
        return
    except exceptions.ConnectionError as e:
        log.exception(f'Failed to connect to elasticsearch: {e}')
        abort(500, 'Failed to establish connection to database')
        return


def get_correct_logo_url(ad_id):
    ad = fetch_platsannons(ad_id)

    logo_url = None

    if ad and 'employer' in ad:
        if 'workplace_id' in ad['employer'] and ad['employer']['workplace_id'] and int(
                ad['employer']['workplace_id']) > 0:  # TODO: never executed by tests
            '''
            Special logo for workplace_id for ads with source_type VIA_AF_FORMULAR eller VIA_PLATSBANKEN_AD or 
            VIA_ANNONSERA (workplace_id > 0)
            '''
            workplace_id = ad['employer']['workplace_id']
            eventual_logo_url = '%sarbetsplatser/%s/logotyper/logo.png' % (settings.COMPANY_LOGO_BASE_URL, workplace_id)
            r = requests.head(eventual_logo_url, timeout=10)
            r.raise_for_status()
            if r.status_code == 200:
                logo_url = eventual_logo_url
        elif 'organization_number' in ad['employer'] and ad['employer']['organization_number']:
            org_number = ad['employer']['organization_number']
            eventual_logo_url = '%sorganisation/%s/logotyper/logo.png' % (settings.COMPANY_LOGO_BASE_URL, org_number)
            r = requests.head(eventual_logo_url, timeout=10)
            r.raise_for_status()
            if r.status_code == 200:
                logo_url = eventual_logo_url
    return logo_url


not_found_file = None


# TODO not called by tests
def get_not_found_logo_file():
    global not_found_file
    if not_found_file is None:
        not_found_filepath = currentdir + "../resources/1x1-00000000.png"
        log.debug('Opening global file %s' % not_found_filepath)
        not_found_file = open(not_found_filepath, 'rb')
        not_found_file = not_found_file.read()
    return not_found_file


def fetch_platsannons_logo(ad_id):
    if settings.COMPANY_LOGO_FETCH_DISABLED:  # TODO: not executed by tests
        logo_url = None
    else:
        logo_url = get_correct_logo_url(ad_id)

    attachment_filename = 'logo.png'
    mimetype = 'image/png'

    if logo_url is None:  # TODO not executed by tests
        return send_file(
            io.BytesIO(get_not_found_logo_file()),
            attachment_filename=attachment_filename,
            mimetype=mimetype
        )
    else:
        r = requests.get(logo_url, stream=True, timeout=5)
        r.raise_for_status()
        return send_file(
            io.BytesIO(r.raw.read(decode_content=False)),
            attachment_filename=attachment_filename,
            mimetype=mimetype
        )


def transform_platsannons_query_result(args, query_result, querybuilder):
    results = query_result.get('hits', {})
    results['took'] = query_result.get('took', 0)
    results['concepts'] = query_result.get('concepts', {})
    if 'aggregations' in query_result:
        results['positions'] = int(query_result.get('aggregations', {})
                                   .get('positions', {}).get('value', 0))
        results['aggs'] = querybuilder.filter_aggs(query_result.get('aggregations', {}),
                                                   args.get(settings.FREETEXT_QUERY))

        for stat in args.get(settings.STATISTICS) or []:  # TODO: never executed by tests
            log.debug("Statistic for field: %s" % stat)
            if 'stats' not in results:
                results['stats'] = []
            results['stats'].append({
                "type": stat,
                "values": [
                    {
                        "term": taxonomy.get_term(elastic, stat, b['key']),
                        "concept_id": taxonomy.get_concept_id(elastic, stat, b['key']),
                        "code": b['key'],
                        "count": b['doc_count']}
                    for b in query_result.get('aggregations', {}).get(stat, {}).get('buckets', [])
                ]
            })

    _modify_results(results)
    return results


def _modify_results(results):
    for hit in results['hits']:
        try:
            hit['_source'] = _format_ad(hit)
        except KeyError:
            pass
        except ValueError:
            pass


# TODO not executed by tests
def find_agg_and_delete(value, aggs):
    # use to find item from aggs result
    remove_agg = ''
    for agg in aggs:
        if agg['value'] == value:
            remove_agg = agg
            break

    if remove_agg:
        aggs.remove(remove_agg)
    return aggs
