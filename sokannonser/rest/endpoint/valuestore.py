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
            "parent-id": "Begränsa sökning till taxonomivärden som har angiven conceptId"
                         " som förälder (användbart tillsammans med typ)",
            "type": "Visa enbart taxonomivärden av typ ",
            settings.SHOW_COUNT: "Visa antal annonser som matchar taxonomivärde "
                                 "(endast i kombination med val av typ)"
        }
    )
    @ns_valuestore.expect(taxonomy_query)
    def get(self):
        args = taxonomy_query.parse_args()
        q = request.args.get('q', None)
        parent_id = args.get('parent-id') if args.get('parent-id') else []
        concept_type = request.args.get('type', None)
        offset = request.args.get(settings.OFFSET, 0)
        limit = request.args.get(settings.LIMIT, 10)
        response = taxonomy.find_concepts(elastic, q, parent_id, concept_type, offset, limit)
        show_count = request.args.get(settings.SHOW_COUNT) == "true"
        statistics = platsannonser.get_stats_for(concept_type) if concept_type and show_count else {}
        if not response:
            abort(500, custom="The server failed to respond properly")
        query_dict = {}
        if q:
            query_dict['filter'] = q
        if parent_id:
            query_dict['parentId'] = parent_id
        if concept_type:
            query_dict['type'] = concept_type
        query_dict['offset'] = offset
        query_dict['limit'] = limit
        return self._build_response(query_dict, response, statistics)

    def _build_response(self, query, response, statistics):
        results = []
        for hit in response.get('hits', {}).get('hits', []):
            type_label = hit['_source']['type']
            entity = {"conceptId": hit['_source'].get('concept_id'),
                      "id": hit['_source'].get('legacy_ams_taxonomy_id'),
                      "term": hit['_source']['label'],
                      "typ": taxonomy.reverse_tax_type.get(type_label, type_label),
                      "type": type_label}
            foralder = hit['_source'].get('parent', {}).get('concept_id')
            if foralder:
                entity['parentId'] = foralder
            if statistics:
                entity['antal'] = statistics.get(hit['_source']['legacy_ams_taxonomy_id'], 0)
            results.append(entity)
        return {'search': query,
                'total': response.get('hits', {}).get('total', 0),
                'result': results}
