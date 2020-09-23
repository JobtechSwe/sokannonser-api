import logging
import time
from datetime import datetime, timedelta
from flask import send_file, Response
from flask_restx import Resource
from jobtech.common.rest.decorators import check_api_key_and_return_metadata
from bulkloader.rest import ns_bulk, bulk_zip_query, bulk_stream_query, bulk_snapshot_query
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
        start_time = int(time.time() * 1000)
        args = bulk_zip_query.parse_args()
        bytes_result = repository.zip_ads(args.get(settings.DATE), start_time)
        filename = "ads_%s.zip" % args.get(settings.DATE)
        log.debug("Elapsed time for completion: %d" % int((time.time() * 1000) - start_time))
        return send_file(bytes_result,
                         attachment_filename=filename, cache_timeout=60,
                         as_attachment=True)


@ns_bulk.route('stream')
class BulkLoad(Resource):
    method_decorators = [check_api_key_and_return_metadata('bulk', settings.API_KEY_RATE_LIMIT)]
    example_date = (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")

    @ns_bulk.doc(
        description="Download all the ads that has been changed (e.g. added, updated, unpublished) during requested time interval. "
                    "Rate limit is one request per minute.",
        params={
            settings.DATE: "Stream ads changed since datetime. "
                           "Accepts datetime as YYYY-MM-DDTHH:MM:SS, "
                           "for example %s." % example_date,
            settings.UPDATED_BEFORE_DATE: "Stream ads changed before datetime. "
                                          "Accepts datetime as YYYY-MM-DDTHH:MM:SS. "
                                          "Optional if you want to set a custom time span. "
                                          "Defaults to 'now' if not set.",
            settings.OCCUPATION_CONCEPT_ID: "Filter stream ads by one or more occupation concept ids "
                                            "(from occupation, occupation_group, occupation_field).",
            settings.LOCATION_CONCEPT_ID: "Filter stream ads by one or more location concept ids "
                                          "(from municipality_concept_id, region_concept_id, country_concept_id)."
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
        log.info('ARGS: %s' % args)
        return Response(repository.load_all(args), mimetype='application/json')


@ns_bulk.route('snapshot')
class SnapshotLoad(Resource):
    method_decorators = [check_api_key_and_return_metadata('bulk', settings.API_KEY_RATE_LIMIT)]

    @ns_bulk.doc(
        description="Download all the ads currently published in Platsbanken. "
                    "The intended usage for this endpoint is to make an initial copy of the job ad dataset "
                    "and then use the stream endpoint to keep it up to date. ",
        responses={
            200: 'OK',
            401: 'Invalid API-key',
            429: 'Rate limit exceeded',
            500: 'Technical error'
        }
    )
    @ns_bulk.expect(bulk_snapshot_query)
    def get(self, **kwargs):
        elasticapm.set_user_context(username=kwargs.get('key_app'), user_id=kwargs.get('key_id'))
        args = bulk_snapshot_query.parse_args()
        log.info('ARGS: %s' % args)
        return Response(repository.load_snapshot(),
                        mimetype='application/json')
