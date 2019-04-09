import logging
from flask_restplus import Resource
from jobtech.common.rest.decorators import check_api_key
from sokannonser.rest import ns_open
from sokannonser.rest.model.platsannons_results import simple_lista
from sokannonser.rest.model.queries import pb_query
from sokannonser.rest.model.queries import swagger_doc_params, swagger_filter_doc_params
from sokannonser.repository.querybuilder import QueryBuilder
from sokannonser.repository import platsannonser

log = logging.getLogger(__name__)


@ns_open.route('/search')
class OpenSearch(Resource):
    method_decorators = [check_api_key('open')]
    querybuilder = QueryBuilder()

    @ns_open.doc(
        params={**swagger_doc_params, **swagger_filter_doc_params},
        responses={
            200: 'OK',
            401: 'Invalid API-key',
            500: 'Technical exception'
        }
    )
    @ns_open.expect(pb_query)
    def get(self):
        args = pb_query.parse_args()
        result = platsannonser.find_platsannonser(args, self.querybuilder)

        return self.marshal_results(result)

    @ns_open.marshal_with(simple_lista)
    def marshal_results(self, result):
        return result
