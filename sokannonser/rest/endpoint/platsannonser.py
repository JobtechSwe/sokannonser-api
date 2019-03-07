import logging
import time
from flask_restplus import Resource
from sokannonser import settings
from sokannonser.rest import ns_platsannons
from sokannonser.rest.decorators import check_api_key
from sokannonser.rest.model.queries import annons_complete_query, pb_query
from sokannonser.rest.model.queries import swagger_doc_params, swagger_filter_doc_params
from sokannonser.repository import platsannonser
from sokannonser.repository.querybuilder import QueryBuilder

log = logging.getLogger(__name__)


@ns_platsannons.route('/search')
class PBSearch(Resource):
    method_decorators = [check_api_key('pb')]
    querybuilder = QueryBuilder()

    @ns_platsannons.doc(
        params={**swagger_doc_params, **swagger_filter_doc_params},
        responses={
            200: 'OK',
            401: 'Invalid API-key',
            500: 'Technical exception'
        }
    )
    @ns_platsannons.expect(pb_query)
    def get(self):
        start_time = int(time.time()*1000)
        args = pb_query.parse_args()
        log.debug("Query parsed after %d milliseconds."
                  % (int(time.time()*1000)-start_time))
        result = platsannonser.find_platsannonser(args,
                                                  self.querybuilder, start_time)
        log.debug("Query results after %d milliseconds."
                  % (int(time.time()*1000)-start_time))

        hits = [hit['_source'] for hit in result.get('hits', [])]

        return self.marshal_results(result, hits, start_time)

    def marshal_results(self, esresult, hits, start_time):
        result = {
            "total": esresult.get('total', 0),
            "positions": esresult.get('positions', 0),
            "query_time_in_millis": esresult.get('took', 0),
            "result_time_in_millis": int(time.time()*1000) - start_time,
            "stats": esresult.get('stats', {}),
            "hits": hits
        }
        log.debug("Sending results after %d milliseconds."
                  % (int(time.time()*1000) - start_time))
        return result


@ns_platsannons.route('/complete')
class PBComplete(Resource):
    method_decorators = [check_api_key('pb')]
    querybuilder = QueryBuilder()

    @ns_platsannons.doc(
        params=swagger_doc_params,
        responses={
            200: 'OK',
            401: 'Invalid API-key',
            500: 'Technical exception'
        }
    )
    @ns_platsannons.expect(annons_complete_query)
    def get(self):
        args = annons_complete_query.parse_args()
        # This could be prettier
        args[settings.LIMIT] = 0  # Always return 0 ads when calling typeahead
        args[settings.TYPEAHEAD_QUERY] = args.pop(settings.FREETEXT_QUERY)

        result = platsannonser.find_platsannonser(args, self.querybuilder)

        return self.marshal_results(result)

    def marshal_results(self, esresult):
        result = {
            "time_in_millis": esresult.get('took', 0),
            "typeahead": esresult.get('aggs', []),
        }
        return result
