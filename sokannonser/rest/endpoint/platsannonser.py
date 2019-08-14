import logging
import time
from flask import request
from flask_restplus import Resource
from jobtech.common.rest.decorators import check_api_key, check_api_key_and_return_metadata
from sokannonser import settings
from sokannonser.rest import ns_platsannons
from sokannonser.rest.model.queries import annons_complete_query, pb_query, load_ad_query
from sokannonser.rest.model.queries import swagger_doc_params, swagger_filter_doc_params
from sokannonser.repository import platsannonser
from sokannonser.rest.model.platsannons_results import (open_results, job_ad,
                                                        typeahead_results)
from sokannonser.repository.querybuilder import QueryBuilder
import elasticapm
log = logging.getLogger(__name__)


@ns_platsannons.route('ad/<id>', endpoint='ad')
class Proxy(Resource):
    method_decorators = [check_api_key_and_return_metadata('pb')]

    @ns_platsannons.doc(
        description='Load a job ad by ID',
    )
    @ns_platsannons.response(401, 'Invalid API-key')
    @ns_platsannons.response(404, 'Job ad not found')
    @ns_platsannons.expect(load_ad_query)
    @ns_platsannons.marshal_with(job_ad)
    def get(self, id, *args, **kwargs):
        elasticapm.set_user_context(username=kwargs['key_app'], user_id=kwargs['key_id'])
        return platsannonser.fetch_platsannons(str(id))


@ns_platsannons.route('search')
class PBSearch(Resource):
    method_decorators = [check_api_key_and_return_metadata('pb')]
    querybuilder = QueryBuilder()

    @ns_platsannons.doc(
        description='Search using parameters and/or freetext',
        params={**swagger_doc_params, **swagger_filter_doc_params},
    )
    @ns_platsannons.response(401, 'Invalid API key')
    @ns_platsannons.expect(pb_query)
    @ns_platsannons.marshal_with(open_results)
    def get(self, **kwargs):
        elasticapm.set_user_context(username=kwargs['key_app'], user_id=kwargs['key_id'])
        start_time = int(time.time()*1000)
        args = pb_query.parse_args()
        log.debug("Query parsed after %d milliseconds."
                  % (int(time.time()*1000)-start_time))
        result = platsannonser.find_platsannonser(args,
                                                  self.querybuilder,
                                                  start_time,
                                                  request.headers.get('X-Fields'))

        log.debug("Query results after %d milliseconds."
                  % (int(time.time()*1000)-start_time))

        max_score = result.get('max_score', 1.0)
        hits = [dict(hit['_source'],
                     **{'relevance': (hit['_score'] / max_score)
                        if max_score > 0 else 0.0})
                for hit in result.get('hits', [])]

        return self.marshal_results(result, hits, start_time)

    def marshal_results(self, esresult, hits, start_time):
        total_results = {'value': esresult.get('total', {}).get('value')}
        result = {
            "total": total_results,
            "positions": esresult.get('positions', 0),
            "query_time_in_millis": esresult.get('took', 0),
            "result_time_in_millis": int(time.time()*1000) - start_time,
            "stats": esresult.get('stats', []),
            "freetext_concepts": esresult.get('concepts', {}),
            "hits": hits
        }
        log.debug("Sending results after %d milliseconds."
                  % (int(time.time()*1000) - start_time))
        return result


@ns_platsannons.route('complete')
class PBComplete(Resource):
    method_decorators = [check_api_key_and_return_metadata('pb')]
    querybuilder = QueryBuilder()

    @ns_platsannons.doc(
        description='Typeahead / Suggest next searchword',
        params=swagger_doc_params
    )
    @ns_platsannons.response(401, 'Invalid API-key')
    @ns_platsannons.expect(annons_complete_query)
    @ns_platsannons.marshal_with(typeahead_results)
    def get(self, **kwargs):
        elasticapm.set_user_context(username=kwargs['key_app'], user_id=kwargs['key_id'])
        start_time = int(time.time()*1000)
        args = annons_complete_query.parse_args()
        # This could be prettier
        args[settings.LIMIT] = 0  # Always return 0 ads when calling typeahead
        query_string = args.pop(settings.FREETEXT_QUERY) or ''
        args[settings.TYPEAHEAD_QUERY] = query_string
        args[settings.FREETEXT_QUERY] = ' '.join(query_string.split(' ')[0:-1])

        result = platsannonser.find_platsannonser(args, self.querybuilder)
        log.debug("Query results after %d milliseconds."
                  % (int(time.time()*1000)-start_time))

        return self.marshal_results(result, start_time)

    def marshal_results(self, esresult, start_time):
        result = {
            "time_in_millis": esresult.get('took', 0),
            "typeahead": esresult.get('aggs', []),
        }
        log.debug("Sending results after %d milliseconds."
                  % (int(time.time()*1000) - start_time))
        return result
