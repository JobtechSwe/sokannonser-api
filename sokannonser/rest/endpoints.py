from sokannonser.rest import api
from flask import request
from flask_restplus import Resource, abort
from valuestore import taxonomy
from valuestore.taxonomy import tax_type, reverse_tax_type
from sokannonser.repository import platsannonser, auranest, elastic
from sokannonser import settings
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
            settings.SORT: "Sortering.\npubdate-desc: publiceringsdatum, nyast först\n"
            "pubdate-asc: publiceringsdatum, äldst först\n"
            "applydate-desc: sista ansökningsdatum, nyast först\n"
            "applydate-asc: sista ansökningsdatum, äldst först\n"
            "relevance: Relevans (poäng)",
            settings.PUBLISHED_AFTER: "Visa annonser publicerade efter angivet datum "
            "(på formen YYYY-mm-ddTHH:MM:SS)",
            settings.PUBLISHED_BEFORE: "Visa annonser publicerade innan angivet datum "
            "(på formen YYYY-mm-ddTHH:MM:SS)",
            settings.FREETEXT_QUERY: "Fritextfråga",
            taxonomy.OCCUPATION: "En eller flera yrkesbenämningskoder enligt taxonomi",
            taxonomy.GROUP: "En eller flera yrkesgruppskoder enligt taxonomi",
            taxonomy.FIELD: "En eller flera yrkesområdeskoder enligt taxonomi",
            taxonomy.SKILL: "En eller flera kompetenskoder enligt taxonomi",
            taxonomy.DRIVING_LICENCE: "Typ av körkort som efterfrågas (taxonomikod)",
            taxonomy.EMPLOYMENT_TYPE: "Anställningstyp enligt taxonomi",
            settings.NO_EXPERIENCE: "Visa enbart jobb som inte kräver erfarenhet",
            # settings.PLACE: "Generellt platsnamn",
            taxonomy.WORKTIME_EXTENT: "En eller flera arbetstidsomfattningskoder enligt "
            "taxonomi",
            taxonomy.MUNICIPALITY: "En eller flera kommunkoder",
            taxonomy.REGION: "En eller flera länskoder",
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
        dataset = args.pop(settings.DATASET)
        if dataset not in settings.AVAILABLE_DATASETS:
            abort(400, 'Dataset %s is not available' % dataset)

        if dataset == settings.DATASET_AURA:
            result = auranest.find_annonser(args)
        else:
            result = platsannonser.find_platsannonser(args)

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
            "kod": "Begränsa sökning till taxonomivärden som har angiven kod som "
            "förälder (användbart tillsammans med typ)",
            "typ": "Visa enbart taxonomivärden av typ "
            "(giltiga värden: %s)" % list(tax_type.keys()),
            settings.SHOW_COUNT: "Visa antal annonser som matchar taxonomivärde "
            "(endast i kombination med val av typ)"
        }
    )
    @api.expect(taxonomy_query)
    def get(self):
        q = request.args.get('q', None)
        kod = request.args.get('kod', None)
        typ = tax_type.get(request.args.get('typ', None), None)
        offset = request.args.get(settings.OFFSET, 0)
        limit = request.args.get(settings.LIMIT, 10)
        response = taxonomy.find_concepts(elastic, q, kod, typ, offset, limit)
        statistics = platsannonser.get_stats_for(typ) if typ \
            and request.args.get(settings.SHOW_COUNT) == "true" else {}
        if not response:
            abort(500, custom="The server failed to respond properly")
        query_dict = {}
        if q:
            query_dict['filter'] = q
        if kod:
            query_dict['foralder'] = kod
        if typ:
            query_dict['typ'] = reverse_tax_type.get(typ)
        return self._build_response(query_dict, response, statistics)

    def _build_response(self, query, response, statistics):
        results = []
        for hit in response.get('hits', {}).get('hits', []):
            type_label = taxonomy.reverse_tax_type.get(hit['_source']['type'],
                                                       "UNKNOWN: %s" %
                                                       hit['_source']['type'])
            entity = {"kod": hit['_source']['id'], "term": hit['_source']['label'],
                      "typ": type_label}
            if statistics:
                entity['antal'] = statistics.get(hit['_source']['id'], 0)
            results.append(entity)
        return {'sokning': query, 'resultat': results}
