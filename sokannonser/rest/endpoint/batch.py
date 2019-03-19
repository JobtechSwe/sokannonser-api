import logging
from flask import send_file
from flask_restplus import Resource
from jobtech.common.rest.decorators import check_api_key
from sokannonser import settings
from sokannonser.rest import ns_batch
from sokannonser.rest.model.queries import batch_query
from sokannonser.repository import platsannonser

log = logging.getLogger(__name__)


@ns_batch.route('/load')
class BatchLoad(Resource):
    # method_decorators = [check_api_key('open')]

    @ns_batch.doc(
        params={
            "zip": "Date to zip ads for"
        },
        responses={
            200: 'OK',
            401: 'Invalid API-key',
            500: 'Technical exception'
        }
    )
    @ns_batch.expect(batch_query)
    def get(self):
        args = batch_query.parse_args()
        bytes_result = platsannonser.zip_ads(args.get(settings.ZIPDATE))
        filename = "ads_%s.zip" % args.get(settings.ZIPDATE)
        return send_file(bytes_result,
                         attachment_filename=filename,
                         as_attachment=True)
