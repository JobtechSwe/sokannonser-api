from flask_restplus import Resource
from sokannonser.rest.decorators import check_api_key
from sokannonser.rest import ns_auranest
from sokannonser.rest.models import auranest_query
from sokannonser.repository import auranest


@ns_auranest.route('/sok')
class AuranestSearch(Resource):
    method_decorators = [check_api_key]

    @ns_auranest.expect(auranest_query)
    def get(self):
        args = auranest_query.parse_args()
        return auranest.find_annonser(args)
