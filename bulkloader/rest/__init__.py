from flask_restplus import Api, Namespace, reqparse, inputs
from sokannonser import settings

api = Api(version='1.0', title='Download job ads',
          description='An API for retrieving job ads',
          default='bulkloader',
          default_label="An API for retrieving job ads.")

ns_bulk = Namespace('Bulk loader', description='Endpoint for downloading all ads in '
                                               'zip-file format or stream.')

api.add_namespace(ns_bulk, '/bulk')

bulk_zip_query = reqparse.RequestParser()
bulk_zip_query.add_argument(settings.APIKEY, location='headers', required=True)

bulk_regex = '^\\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])|\\ball\\b|\\byesterday\\b$'
bulk_zip_query.add_argument(settings.DATE, type=inputs.regex(bulk_regex), required=True)

bulk_stream_query = reqparse.RequestParser()
bulk_stream_query.add_argument(settings.APIKEY, location='headers', required=True)
bulk_stream_query.add_argument(settings.DATE,
                               type=inputs.datetime_from_iso8601,
                               required=True)
