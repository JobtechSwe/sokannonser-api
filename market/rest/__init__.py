from flask_restplus import Api, Namespace, reqparse, inputs
from sokannonser import settings

api = Api(version='1.1.1', title='Market Search',
          description='An API for searching and retrieving job listings from the '
          'entire job market',
          default='market',
          default_label="An API for searching job listings.")

# Namespace configuration
ns_market = Namespace('All job ads',
                      description='Search and retrieve ~97% of all job ads.')

api.add_namespace(ns_market, '/')

# Queries
market_query = reqparse.RequestParser()
market_query.add_argument(settings.APIKEY, location='headers', required=True)
market_query.add_argument(settings.OFFSET,
                          type=inputs.int_range(0, settings.MAX_OFFSET),
                          default=0)
market_query.add_argument(settings.LIMIT,
                          type=inputs.int_range(0, settings.MAX_LIMIT),
                          default=10)
market_query.add_argument(settings.SHOW_EXPIRED, choices=['true', 'false'])
market_query.add_argument(settings.FREETEXT_QUERY)
market_query.add_argument(settings.PLACE, action='append')
market_query.add_argument(settings.EMPLOYER, action='append')
market_query.add_argument(settings.STATISTICS,
                          choices=list(settings.auranest_stats_options.keys()),
                          action='append')
market_query.add_argument(settings.STAT_LMT, type=inputs.int_range(0, 100), default=10)

market_typeahead = reqparse.RequestParser()
market_typeahead.add_argument(settings.APIKEY, location='headers', required=True)
market_typeahead.add_argument(settings.FREETEXT_QUERY)

# Results
