import logging
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
    method_decorators = [check_api_key]
    querybuilder = QueryBuilder()

    @ns_platsannons.doc(
        params={**swagger_doc_params, **swagger_filter_doc_params},
        responses={
            200: 'OK',
            401: 'Felaktig API-nyckel',
            500: 'Bad'
        }
    )
    @ns_platsannons.expect(pb_query)
    def get(self):
        args = pb_query.parse_args()
        result = platsannonser.find_platsannonser(args, self.querybuilder)

        return self.marshal_results(result)

    def marshal_results(self, esresult):
        result = {
            "total": esresult.get('total', 0),
            "positions": esresult.get('positions', 0),
            "typeahead": esresult.get('aggs', []),
            "stats": esresult.get('stats', {}),
            "hits": [hit['_source'] for hit in esresult['hits']],
        }
        return result


@ns_platsannons.route('/complete')
class PBComplete(Resource):
    method_decorators = [check_api_key]
    querybuilder = QueryBuilder()

    @ns_platsannons.doc(
        params=swagger_doc_params,
        responses={
            200: 'OK',
            401: 'Felaktig API-nyckel',
            500: 'Bad'
        }
    )
    @ns_platsannons.expect(annons_complete_query)
    def get(self):
        args = annons_complete_query.parse_args()
        # This could be prettier
        args[settings.LIMIT] = 0  # Always return 0 ads when calling typeahead
        args[settings.TYPEAHEAD_QUERY] = args.get(settings.FREETEXT_QUERY)

        result = platsannonser.find_platsannonser(args, self.querybuilder)

        return self.marshal_results(result)

    def marshal_results(self, esresult):
        result = {
            "total": esresult.get('total', 0),
            "positions": esresult.get('positions', 0),
            "typeahead": esresult.get('aggs', []),
        }
        return result
