import logging
import time
from flask import send_file
from flask_restplus import Resource
from jobtech.common.rest.decorators import check_api_key
from sokannonser import settings
from sokannonser.rest import ns_bulk
from sokannonser.rest.model.queries import bulk_query
from sokannonser.repository import platsannonser

log = logging.getLogger(__name__)


@ns_bulk.route('/load')
class BulkLoad(Resource):
    method_decorators = [check_api_key('bulk')]

    @ns_bulk.doc(
        params={
            "zip": "Date to zip ads for. Accepts date as YYYY-MM-DD, 'all' "
            "or 'yesterday'. (Note that 'all' can take a couple of minutes to compile.)"
        },
        responses={
            200: 'OK',
            401: 'Invalid API-key',
            500: 'Technical exception'
        }
    )
    @ns_bulk.expect(bulk_query)
    def get(self):
        start_time = int(time.time()*1000)
        args = bulk_query.parse_args()
        bytes_result = platsannonser.zip_ads(args.get(settings.ZIPDATE), start_time)
        filename = "ads_%s.zip" % args.get(settings.ZIPDATE)
        log.debug("Elapsed time for completion: %d" % int((time.time()*1000)-start_time))
        return send_file(bytes_result,
                         attachment_filename=filename,
                         as_attachment=True)
