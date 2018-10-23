from flask_restplus import Resource
from sokannonser import settings
from sokannonser.rest.decorators import check_api_key
from sokannonser.rest import ns_auranest
from sokannonser.rest.model.queries import auranest_query, auranest_typeahead
from sokannonser.rest.model.auranest_results import auranest_lista
from sokannonser.repository import auranest


@ns_auranest.route('search')
class AuranestSearch(Resource):
    method_decorators = [check_api_key]

    @ns_auranest.doc(description='Sök med fritextfråga')
    @ns_auranest.expect(auranest_query)
    @ns_auranest.marshal_with(auranest_lista)
    def get(self):
        args = auranest_query.parse_args()
        results = auranest.find_annonser(args)
        return results


@ns_auranest.route('complete')
class AuranestSearch(Resource):
    method_decorators = [check_api_key]

    @ns_auranest.doc(description='Ge förslag på nästa sökord')
    @ns_auranest.expect(auranest_typeahead)
    def get(self):
        args = auranest_typeahead.parse_args()
        return auranest.autocomplete(args.get(settings.FREETEXT_QUERY))
