import json
import logging
import time

from elasticsearch import exceptions
from flask_restx import Namespace
from flask_restx import abort
from sokannonser import settings
from sokannonser.repository import elastic
from sokannonser.repository.querybuilder import calculate_utc_offset

log = logging.getLogger(__name__)
marshaller = Namespace('Marshaller')
offset = calculate_utc_offset()


def find_all(args, querybuilder, start_time=0):
    if start_time == 0:
        start_time = int(time.time() * 1000)
    query_dsl = querybuilder.parse_args(args)
    log.debug('Query: %s' % json.dumps(query_dsl))
    log.debug("Query constructed after %d milliseconds." % (int(time.time() * 1000) - start_time))
    try:
        query_result = elastic.search(index=settings.ES_SKRAPADE_INDEX, body=query_dsl)
        log.debug("Elastic results after %d milliseconds." % (int(time.time() * 1000) - start_time))
    except exceptions.ConnectionError as e:
        log.exception('Failed to connect to elasticsearch: %s' % str(e))
        abort(500, 'Failed to establish connection to database')
        return

    log.debug("Elasticsearch reports: took=%d, timed_out=%s"
              % (query_result.get('took', 0), query_result.get('timed_out', '')))
    return transform_platsannons_query_result(query_result)


def transform_platsannons_query_result(query_result):
    results = query_result.get('hits', {})
    results['took'] = query_result.get('took', 0)
    results['concepts'] = query_result.get('concepts', {})
    return results
