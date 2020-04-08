import logging
import time
from flask import request
from flask_restx import Resource
from jobtech.common.rest.decorators import check_api_key_and_return_metadata
from sokannonser import settings
from sokannonser.rest import ns_platsannons
from sokannonser.rest.model.queries import annons_complete_query, pb_query, load_ad_query
from sokannonser.rest.model.queries import swagger_doc_params, swagger_filter_doc_params
from sokannonser.repository import platsannonser
from sokannonser.rest.model.result_models import (open_results, job_ad,
                                                  typeahead_results, suggest_typeahead_results)
from sokannonser.repository.querybuilder import QueryBuilder
import elasticapm
log = logging.getLogger(__name__)


@ns_platsannons.route('ad/<id>', endpoint='ad')
class Proxy(Resource):
    method_decorators = [check_api_key_and_return_metadata('pb')]

    @ns_platsannons.doc(
        description='Load a job ad by ID',
    )
    @ns_platsannons.response(401, 'Invalid API-key')
    @ns_platsannons.response(404, 'Job ad not found')
    @ns_platsannons.expect(load_ad_query)
    @ns_platsannons.marshal_with(job_ad)
    def get(self, id, *args, **kwargs):
        elasticapm.set_user_context(username=kwargs.get('key_app'), user_id=kwargs.get('key_id'))
        return platsannonser.fetch_platsannons(str(id))


@ns_platsannons.route('ad/<id>/logo', endpoint='ad_logo')
class AdLogo(Resource):
    @ns_platsannons.doc(
        description='Load a logo binary file by ID',
    )
    @ns_platsannons.response(404, 'Job ad not found')
    def get(self, id):
        return platsannonser.fetch_platsannons_logo(str(id))


@ns_platsannons.route('search')
class Search(Resource):
    method_decorators = [check_api_key_and_return_metadata('pb')]
    querybuilder = QueryBuilder()

    @ns_platsannons.doc(
        description='Search using parameters and/or freetext',
        params={**swagger_doc_params, **swagger_filter_doc_params},
    )
    @ns_platsannons.response(401, 'Invalid API key')
    @ns_platsannons.expect(pb_query)
    @ns_platsannons.marshal_with(open_results)
    def get(self, **kwargs):
        elasticapm.set_user_context(username=kwargs.get('key_app'), user_id=kwargs.get('key_id'))
        start_time = int(time.time()*1000)
        args = pb_query.parse_args()
        log.debug("Query parsed after %d milliseconds."
                  % (int(time.time()*1000)-start_time))
        result = platsannonser.find_platsannonser(args,
                                                  self.querybuilder,
                                                  start_time,
                                                  request.headers.get('X-Fields'))

        log.debug("Query results after %d milliseconds."
                  % (int(time.time()*1000)-start_time))

        max_score = result.get('max_score', 1.0)
        hits = [dict(hit['_source'],
                     **{'relevance': (hit['_score'] / max_score)
                        if max_score > 0 else 0.0})
                for hit in result.get('hits', [])]

        return self.marshal_results(result, hits, start_time)

    def marshal_results(self, esresult, hits, start_time):
        total_results = {'value': esresult.get('total', {}).get('value')}
        result = {
            "total": total_results,
            "positions": esresult.get('positions', 0),
            "query_time_in_millis": esresult.get('took', 0),
            "result_time_in_millis": int(time.time()*1000) - start_time,
            "stats": esresult.get('stats', []),
            "freetext_concepts": esresult.get('concepts', {}),
            "hits": hits
        }
        log.debug("Sending results after %d milliseconds."
                  % (int(time.time()*1000) - start_time))
        return result


@ns_platsannons.route('complete')
class Complete(Resource):
    method_decorators = [check_api_key_and_return_metadata('pb')]
    querybuilder = QueryBuilder()

    @ns_platsannons.doc(
        description='Typeahead / Suggest next searchword',
        params={
            settings.CONTEXTUAL_TYPEAHEAD: "Set to false to disable contextual typeahead"
                                           " (default: true)",
            settings.X_FEATURE_ALLOW_EMPTY_TYPEAHEAD: "Allow empty querystring in typeahead.",
            settings.X_FEATURE_INCLUDE_SYNONYMS_TYPEAHEAD: "Include enriched synonyms in typeahead.",
            settings.X_FEATURE_SPELLCHECK_TYPEAHEAD: "Use spellchecking in typeahead. Disables contextual typeahead.",
            settings.X_FEATURE_SUGGEST_EXTRA_WORD: "Suggest extra word in autocomplete",
            **swagger_doc_params
        }
    )
    @ns_platsannons.response(401, 'Invalid API-key')
    @ns_platsannons.expect(annons_complete_query)
    @ns_platsannons.marshal_with(typeahead_results)
    def get(self, **kwargs):
        elasticapm.set_user_context(username=kwargs.get('key_app'), user_id=kwargs.get('key_id'))
        start_time = int(time.time()*1000)
        args = annons_complete_query.parse_args()
        freetext_query = args.get(settings.FREETEXT_QUERY) or ''
        limit = args[settings.LIMIT] if args[settings.LIMIT] <= settings.MAX_COMPLETE_LIMIT else settings.MAX_COMPLETE_LIMIT
        result = {}
        # if last input is space, and suggest extra word feature allow empty feature both are true,
        # check suggest without space
        if not freetext_query.split(' ')[-1] and args[settings.X_FEATURE_SUGGEST_EXTRA_WORD] \
                and args[settings.X_FEATURE_ALLOW_EMPTY_TYPEAHEAD]:
            args[settings.TYPEAHEAD_QUERY] = freetext_query.strip()
            args[settings.FREETEXT_QUERY] = ' '.join(freetext_query.strip().split(' ')[0:-1])

            if args[settings.X_FEATURE_SPELLCHECK_TYPEAHEAD]:
                result = platsannonser.suggest(args, self.querybuilder)
            else:
                result = platsannonser.find_platsannonser(args, self.querybuilder)

        # have not get result or suggest have not get one suggest
        if not result or len(result.get('aggs')) != 1:
            args[settings.TYPEAHEAD_QUERY] = freetext_query
            args[settings.FREETEXT_QUERY] = ' '.join(freetext_query.split(' ')[0:-1])
            if args[settings.X_FEATURE_SPELLCHECK_TYPEAHEAD]:
                result = platsannonser.suggest(args, self.querybuilder)
            else:
                result = platsannonser.find_platsannonser(args, self.querybuilder)

        # only get one suggestion
        if args[settings.X_FEATURE_SUGGEST_EXTRA_WORD] and len(result.get('aggs')) == 1:
            extra_words = platsannonser.suggest_extra_word(args, result.get('aggs')[0], self.querybuilder)
            result['aggs'] += extra_words
            log.debug('Extra words: %s' % result['aggs'])

        # If there is space delete the same word with with input word
        if args[settings.X_FEATURE_ALLOW_EMPTY_TYPEAHEAD] and not freetext_query.split(' ')[-1]:
            result['aggs'] = platsannonser.find_agg_and_delete(freetext_query.strip().split(' ')[0], result['aggs'])
            log.debug('Empty typeahead. Removed item: %s Aggs after removal: %s' % (result['aggs'], result['aggs']))

        log.debug("Query results after %d milliseconds."
                  % (int(time.time()*1000)-start_time))

        return self.marshal_results(result, limit, start_time)

    def marshal_results(self, esresult, limit, start_time):
        typeahead_result = esresult.get('aggs', [])
        if len(typeahead_result) > limit:
            typeahead_result = typeahead_result[:limit]

        result = {
            "time_in_millis": esresult.get('took', 0),
            "typeahead": typeahead_result,
        }
        log.debug("Sending results after %d milliseconds."
                  % (int(time.time()*1000) - start_time))
        return result
