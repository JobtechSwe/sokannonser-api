from flask import request
from flask_restplus import Resource, abort
from valuestore.taxonomy import tax_type, reverse_tax_type
from valuestore import taxonomy
from sokannonser import settings
from sokannonser.repository import elastic, platsannonser
from sokannonser.rest import ns_valuestore
from sokannonser.rest.model.queries import taxonomy_query


@ns_valuestore.route('/search')
class Valuestore(Resource):
    @ns_valuestore.doc(
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
    @ns_valuestore.expect(taxonomy_query)
    def get(self):
        args = taxonomy_query.parse_args()
        q = request.args.get('q', None)
        kod = args.get('kod') if args.get('kod') else []
        typ = tax_type.get(request.args.get('typ', None), None)
        offset = request.args.get(settings.OFFSET, 0)
        limit = request.args.get(settings.LIMIT, 10)
        response = taxonomy.find_concepts(elastic, q, kod, typ, offset, limit)
        show_count = request.args.get(settings.SHOW_COUNT) == "true"
        statistics = platsannonser.get_stats_for(typ) if typ and show_count else {}
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
            entity = {"kod": hit['_source'].get('id'),
                      "uuid": hit['_source'].get('concept_id'),
                      "term": hit['_source']['label'],
                      "typ": type_label}
            foralder = hit['_source'].get('parent', {}).get('id')
            if foralder:
                entity['foralder'] = foralder
            if statistics:
                entity['antal'] = statistics.get(hit['_source']['id'], 0)
            results.append(entity)
        return {'sokning': query, 'resultat': results}
