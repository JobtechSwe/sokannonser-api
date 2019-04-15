from flask_restplus import Resource
from jobtech.common.rest.decorators import check_api_key
from sokannonser import settings
from market.rest import ns_market, market_query, market_typeahead
from market.rest.results import market_list, autocomplete_list
from market import repository


@ns_market.route('/search')
class MarketSearch(Resource):
    method_decorators = [check_api_key('all')]

    @ns_market.doc(description='Search with freetext query')
    @ns_market.expect(market_query)
    @ns_market.marshal_with(market_list)
    def get(self):
        args = market_query.parse_args()
        return repository.find_annonser(args)


@ns_market.route('/complete')
class MarketComplete(Resource):
    method_decorators = [check_api_key('all')]

    @ns_market.doc(description='Typeahead / Suggest the next search term')
    @ns_market.expect(market_typeahead)
    @ns_market.marshal_with(autocomplete_list)
    def get(self):
        args = market_typeahead.parse_args()
        return {'typeahead': repository.autocomplete(args.get(settings.FREETEXT_QUERY))}
