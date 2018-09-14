from sokannonser.rest import api
from flask import request
from flask_restplus import Resource, abort
from sokannonser.repository import platsannonser
from sokannonser.repository import auranest
from sokannonser.repository import taxonomy
from sokannonser import settings
from sokannonser.settings import taxonomy_type
from sokannonser.rest.decorators import check_api_key
from sokannonser.rest.models import pbapi_lista, simple_lista, \
                                    sok_platsannons_query, taxonomy_query


@api.route('/sok')
class Search(Resource):
    method_decorators = [check_api_key]

    @api.doc(
        params={
            settings.APIKEY: "Nyckel som krävs för att använda API:et",
            settings.OFFSET: "Börja lista resultat från denna position "
            "(0-%d)" % settings.MAX_OFFSET,
            settings.LIMIT: "Antal resultat att visa (0-%d)" % settings.MAX_LIMIT,
            settings.SORT: "Sortering.\ndate-desc: publiceringsdatum, nyast först\n"
            "date-asc: publiceringsdatum, äldst först\nrelevance: Relevans (poäng)",
            settings.PUBLISHED_AFTER: "Visa annonser publicerade efter angivet datum "
            "(på formen YYYY-mm-ddTHH:MM:SS)",
            settings.PUBLISHED_BEFORE: "Visa annonser publicerade innan angivet datum "
            "(på formen YYYY-mm-ddTHH:MM:SS)",
            settings.FREETEXT_QUERY: "Fritextfråga",
            settings.OCCUPATION: "En eller flera yrkesbenämningskoder enligt taxonomi",
            settings.GROUP: "En eller flera yrkesgruppskoder enligt taxonomi",
            settings.FIELD: "En eller flera yrkesområdeskoder enligt taxonomi",
            settings.SKILL: "En eller flera kompetenskoder enligt taxonomi",
            # settings.PLACE: "Generellt platsnamn",
            settings.WORKTIME_EXTENT: "En eller flera arbetstidsomfattningskoder enligt "
            "taxonomi",
            settings.MUNICIPALITY: "En eller flera kommunkoder",
            settings.REGION: "En eller flera länskoder",
            # settings.PLACE_RADIUS: "Inom vilken ungefärlig radie i kilometer från "
            # "valda platser som annonser ska hittas",
            settings.RESULT_MODEL: "Resultatmodell",
            settings.DATASET: "Sök bland AF:s annonser eller alla på marknaden (auranest)"
        },
        responses={
            200: 'OK',
            401: 'Felaktig API-nyckel',
            500: 'Bad'
        }
    )
    @api.expect(sok_platsannons_query)
    def get(self):
        args = sok_platsannons_query.parse_args()
        dataset = args.get(settings.DATASET)
        if dataset not in settings.AVAILABLE_DATASETS:
            abort(400, 'Dataset %s is not available' % dataset)

        if args.get(settings.DATASET) == settings.DATASET_AF:
            result = platsannonser.find_platsannonser(args)
        else:
            result = auranest.find_annonser(args)

        if args.get(settings.RESULT_MODEL, '') == 'pbabi':
            return self.marshal_pbapi(result)
        elif args.get(settings.RESULT_MODEL, '') == 'simple':
            return self.marshal_simple(result)
        else:
            return self.marshal_full(result)

    # Marshal with pbapi model
    @api.marshal_with(pbapi_lista)
    def marshal_pbapi(self, result):
        return result

    def marshal_full(self, esresult):
        result = {
            "total": esresult['total'],
            "hits": [hit['_source'] for hit in esresult['hits']]
        }
        return result

    @api.marshal_with(simple_lista)
    def marshal_simple(self, result):
        return result


@api.route('/vardeforrad')
class Valuestore(Resource):
    @api.doc(
        params={
            settings.OFFSET: "Börja lista resultat från denna position",
            settings.LIMIT: "Antal resultat att visa",
            settings.FREETEXT_QUERY: "Fritextfråga mot taxonomin. "
            "(Kan t.ex. användas för autocomplete / type ahead)",
            "kod": "Begränsa sökning till taxonomier som har överliggande kod (förälder) "
            "(används med fördel tillsammans med typ)",
            "typ": "Visa enbart taxonomivärden av typ "
            "(giltiga värden: %s)" % list(taxonomy_type.keys()),
            settings.SHOW_COUNT: "Visa antal annonser som matchar taxonomivärde "
            "(endast i kombination med val av typ)"
        }
    )
    @api.expect(taxonomy_query)
    def get(self):
        q = request.args.get('q', None)
        kod = request.args.get('kod', None)
        typ = taxonomy_type.get(request.args.get('typ', None), None)
        offset = request.args.get(settings.OFFSET, 0)
        limit = request.args.get(settings.LIMIT, 10)
        response = taxonomy.find_concepts(q, kod, typ, offset, limit)
        statistics = platsannonser.get_stats_for(typ) if typ \
            and request.args.get(settings.SHOW_COUNT, False) else {}
        if not response:
            abort(500, custom="The server failed to respond properly")
        return self._build_response(response, statistics)

    def _build_response(self, response, statistics):
        results = []
        for hit in response['hits']:
            entity = {"kod": hit['_source']['id'], "term": hit['_source']['label'],
                      "typ": settings.reverse_taxonomy_type[hit['_source']['type']]}
            if statistics:
                entity['antal'] = statistics.get(hit['_source']['id'], 0)
            results.append(entity)
        return results
