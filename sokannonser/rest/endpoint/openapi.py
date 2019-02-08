import logging
from flask_restplus import Resource, abort
from requests import get, exceptions
from sokannonser import settings
from sokannonser.rest import ns_platsannons, ns_open
from sokannonser.rest.decorators import check_api_key
from sokannonser.rest.model.platsannons_results import simple_lista
from sokannonser.rest.model.queries import pb_query
from sokannonser.rest.model.queries import swagger_doc_params, swagger_filter_doc_params
from sokannonser.repository.querybuilder import QueryBuilder
from sokannonser.repository import platsannonser

log = logging.getLogger(__name__)


@ns_open.route('/search')
class OpenSearch(Resource):
    method_decorators = [check_api_key]
    querybuilder = QueryBuilder()

    @ns_open.doc(
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

    @ns_open.marshal_with(simple_lista)
    def marshal_results(self, result):
        return result


@ns_open.route('/ad/<id>')
class Proxy(Resource):

    @ns_platsannons.doc(
        responses={
            200: 'OK',
            401: 'Felaktig API-nyckel',
            404: 'Annonsen saknas',
            500: 'Serverfel'
        }
    )
    def get(self, id):
        url = "%s%s" % (settings.AD_PROXY_URL, id)
        headers = {'Accept-Language': 'sv', 'Accept': 'application/json'}
        try:
            response = get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                abort(response.status_code)
        except exceptions.RequestException as e:
            log.error('Failed to connect', e)
            abort(500)