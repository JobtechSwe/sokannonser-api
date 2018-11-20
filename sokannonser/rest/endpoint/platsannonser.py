from flask_restplus import Resource
from requests import get
from sokannonser.rest.model import queries
from valuestore import taxonomy
from sokannonser import settings
from sokannonser.rest import ns_platsannons
from sokannonser.rest.decorators import check_api_key
from sokannonser.rest.model.platsannons_results import pbapi_lista, simple_lista
from sokannonser.rest.model.queries import sok_platsannons_query
from sokannonser.repository import platsannonser
from sokannonser.repository.querybuilder import QueryBuilder


@ns_platsannons.route('/ad/<id>')
class Proxy(Resource):

    def get(self, id):
        url = "%s%s" % (settings.AD_PROXY_URL, id)
        headers = {'Accept-Language': 'sv', 'Accept': 'application/json'}
        return get(url, headers=headers).json()


@ns_platsannons.route('/search')
class Search(Resource):
    method_decorators = [check_api_key]
    querybuilder = QueryBuilder()

    @ns_platsannons.doc(
        params={
            settings.APIKEY: "Nyckel som krävs för att använda API:et",
            settings.OFFSET: "Börja lista resultat från denna position "
                             "(0-%d)" % settings.MAX_OFFSET,
            settings.LIMIT: "Antal resultat att visa (0-%d)" % settings.MAX_LIMIT,
            settings.SORT: "Sortering.\npubdate-desc: publiceringsdatum, nyast först\n"
                           "pubdate-asc: publiceringsdatum, äldst först\n"
                           "applydate-desc: sista ansökningsdatum, nyast först\n"
                           "applydate-asc: sista ansökningsdatum, äldst först\n"
                           "relevance: Relevans (poäng) (default)",
            settings.PUBLISHED_AFTER: "Visa annonser publicerade efter angivet datum "
                                      "(på formen YYYY-mm-ddTHH:MM:SS)",
            settings.PUBLISHED_BEFORE: "Visa annonser publicerade innan angivet datum "
                                       "(på formen YYYY-mm-ddTHH:MM:SS)",
            settings.FREETEXT_QUERY: "Fritextfråga",
            settings.TYPEAHEAD_QUERY: "Ge förslag på sökord utifrån nuvarande sökning "
                                      "(autocomplete)",
            settings.FREETEXT_FIELDS: "Välj vilka fält utöver standardfälten (rubrik, "
                                      "arbetsplatsnamn och annonstext) "
                                      "som ska användas för fritextfråga "
                                      "(" + settings.FREETEXT_QUERY + "). Påverkar också "
                                      "autocomplete (" + settings.TYPEAHEAD_QUERY + ").\n"
                                      "Alternativ: " + str(queries.QF_CHOICES) + "\n"
                                      "Default: samtliga",
            taxonomy.OCCUPATION: "En eller flera yrkesbenämningskoder enligt taxonomi",
            taxonomy.GROUP: "En eller flera yrkesgruppskoder enligt taxonomi",
            taxonomy.FIELD: "En eller flera yrkesområdeskoder enligt taxonomi",
            taxonomy.SKILL: "En eller flera kompetenskoder enligt taxonomi",
            taxonomy.DRIVING_LICENCE: "Typ av körkort som efterfrågas (taxonomikod)",
            taxonomy.EMPLOYMENT_TYPE: "Anställningstyp enligt taxonomi",
            settings.EXPERIENCE_REQUIRED: "Sätt till 'false' för att visa enbart jobb "
                                          "som inte kräver erfarenhet",
            # settings.PLACE: "Generellt platsnamn",
            taxonomy.WORKTIME_EXTENT: "En eller flera arbetstidsomfattningskoder enligt "
                                      "taxonomi",
            settings.PARTTIME_MIN: "För deltidsjobb, minsta omfattning",
            settings.PARTTIME_MAX: "För deltidsjobb, maximal omfattning",
            taxonomy.MUNICIPALITY: "En eller flera kommunkoder",
            taxonomy.REGION: "En eller flera länskoder",
            settings.LONGITUDE: "Longitud för punkt",
            settings.LATITUDE: "Latitud för punkt",
            settings.POSITION_RADIUS: "Radie från punkt i km",
            # settings.PLACE_RADIUS: "Inom vilken ungefärlig radie i kilometer från "
            # "valda platser som annonser ska hittas",
            settings.STATISTICS: "Visa sökstatistik för angivna fält "
                                 "(tillgängliga fält: %s, %s och %s)" % (
                                     taxonomy.OCCUPATION,
                                     taxonomy.GROUP,
                                     taxonomy.FIELD),
            settings.RESULT_MODEL: "Resultatmodell",
        },
        responses={
            200: 'OK',
            401: 'Felaktig API-nyckel',
            500: 'Bad'
        }
    )
    @ns_platsannons.expect(sok_platsannons_query)
    def get(self):
        args = sok_platsannons_query.parse_args()
        resultmodel = args.get(settings.RESULT_MODEL)
        result = platsannonser.find_platsannonser(args, self.querybuilder)

        if resultmodel == 'pbapi':
            return self.marshal_pbapi(result)
        elif resultmodel == 'simple':
            return self.marshal_simple(result)
        else:
            return self.marshal_full(result)

    # Marshal with pbapi model
    @ns_platsannons.marshal_with(pbapi_lista)
    def marshal_pbapi(self, result):
        return result

    def marshal_full(self, esresult):
        result = {
            "total": esresult.get('total', 0),
            "positions": esresult.get('positions', 0),
            "typeahead": esresult.get('aggs', []),
            "stats": esresult.get('stats', {}),
            "hits": [hit['_source'] for hit in esresult['hits']],
        }
        return result

    @ns_platsannons.marshal_with(simple_lista)
    def marshal_simple(self, result):
        return result
