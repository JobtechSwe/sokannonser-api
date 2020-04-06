import logging
import time
from datetime import datetime, timedelta
from flask import send_file, Response
from flask_restx import Resource
from jobtech.common.rest.decorators import check_api_key, check_api_key_and_return_metadata
from bulkloader.rest import ns_bulk, bulk_zip_query, bulk_stream_query
from bulkloader import repository
from sokannonser import settings
import elasticapm

log = logging.getLogger(__name__)


# @ns_bulk.route('zip')
class BulkZip(Resource):
    method_decorators = [check_api_key_and_return_metadata('bulk', 300)]

    @ns_bulk.doc(
        params={
            settings.DATE: "Date to zip ads for. Accepts date as YYYY-MM-DD or 'all'. "
            "(Note that 'all' can take a couple of minutes to compile.)"
            " Rate limit is one request every five minutes."
        },
        responses={
            200: 'OK',
            401: 'Invalid API-key',
            429: 'Rate limit exceeded',
            500: 'Technical error'
        }
    )
    @ns_bulk.expect(bulk_zip_query)
    def get(self, **kwargs):
        elasticapm.set_user_context(username=kwargs.get('key_app'), user_id=kwargs.get('key_id'))
        start_time = int(time.time()*1000)
        args = bulk_zip_query.parse_args()
        bytes_result = repository.zip_ads(args.get(settings.DATE), start_time)
        filename = "ads_%s.zip" % args.get(settings.DATE)
        log.debug("Elapsed time for completion: %d" % int((time.time()*1000)-start_time))
        return send_file(bytes_result,
                         attachment_filename=filename, cache_timeout=60,
                         as_attachment=True)


@ns_bulk.route('stream')
class BulkLoad(Resource):
    method_decorators = [check_api_key_and_return_metadata('bulk', 60)]
    example_date = (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")

    @ns_bulk.doc(
        params={
            settings.DATE: "Stream ads updated since datetime. "
            "Accepts datetime as YYYY-MM-DDTHH:MM:SS, "
            "for example %s. Rate limit is one request per minute." % example_date,
            settings.OCCUPATION: "Filter Stream ads by occupations"
        },
        responses={
            200: 'OK',
            401: 'Invalid API-key',
            429: 'Rate limit exceeded',
            500: 'Technical error'
        }
    )
    @ns_bulk.expect(bulk_stream_query)
    def get(self, **kwargs):
        elasticapm.set_user_context(username=kwargs.get('key_app'), user_id=kwargs.get('key_id'))
        args = bulk_stream_query.parse_args()
        return Response(repository.load_all(args),
                        mimetype='application/json')
