from datetime import datetime, timedelta

from flask_restx import Api, Namespace, reqparse, inputs
from sokannonser import settings

api = Api(version=settings.API_VERSION, title='Download job ads',
          description='An API for retrieving job ads',
          default='bulkloader',
          default_label="An API for retrieving job ads.")

ns_bulk = Namespace('Bulk loader', description='Endpoint for downloading ads in '
                                               'stream.')

api.add_namespace(ns_bulk, '/')

bulk_zip_query = reqparse.RequestParser()
bulk_zip_query.add_argument(settings.APIKEY, location='headers', required=True)
# r for raw, PEP8
bulk_regex = r'^(\d{4}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])|all)$'

bulk_zip_query.add_argument(settings.DATE, type=inputs.regex(bulk_regex), required=True)

default_time = (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")

bulk_stream_query = reqparse.RequestParser()
bulk_stream_query.add_argument(settings.APIKEY, location='headers', required=True)
bulk_stream_query.add_argument(settings.SNAPSHOT, type=inputs.boolean, default=False)
bulk_stream_query.add_argument(settings.DATE, type=inputs.datetime_from_iso8601,
                               required=True, default=default_time)
