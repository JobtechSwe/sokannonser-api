import logging
import time
from flask import send_file, Response
from flask_restplus import Resource
from jobtech.common.rest.decorators import check_api_key
from bulkloader.rest import ns_bulk, bulk_zip_query, bulk_stream_query
from bulkloader import repository
from sokannonser import settings

log = logging.getLogger(__name__)


@ns_bulk.route('/zip')
class BulkZip(Resource):
    method_decorators = [check_api_key('bulk')]

    @ns_bulk.doc(
        params={
            settings.DATE: "Date to zip ads for. Accepts date as YYYY-MM-DD or 'all'. "
            "(Note that 'all' can take a couple of minutes to compile.)"
        },
        responses={
            200: 'OK',
            401: 'Invalid API-key',
            500: 'Technical error'
        }
    )
    @ns_bulk.expect(bulk_zip_query)
    def get(self):
        start_time = int(time.time()*1000)
        args = bulk_zip_query.parse_args()
        bytes_result = repository.zip_ads(args.get(settings.DATE), start_time)
        filename = "ads_%s.zip" % args.get(settings.DATE)
        log.debug("Elapsed time for completion: %d" % int((time.time()*1000)-start_time))
        return send_file(bytes_result,
                         attachment_filename=filename, cache_timeout=None,
                         as_attachment=True)


@ns_bulk.route('/stream')
class BulkLoad(Resource):
    method_decorators = [check_api_key('bulk')]

    @ns_bulk.doc(
        params={
            settings.DATE: "Stream ads updated since datetime"
        },
        responses={
            200: 'OK',
            401: 'Invalid API-key',
            500: 'Technical error'
        }
    )
    @ns_bulk.expect(bulk_stream_query)
    def get(self):
        args = bulk_stream_query.parse_args()
        return Response(repository.load_all(args.get(settings.DATE)),
                        mimetype='application/json')
