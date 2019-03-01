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
            settings.OFFSET: "The offset parameter defines the offset from the first result you want to fetch",
            settings.LIMIT: "Number of result rows to fetch",
            settings.FREETEXT_QUERY: "Freetext query for fetching a filtered result. "
                                     "(for example for autocomplete / type ahead)",
            "parent-id": "filter search for taxonomy values by specific parent conceptId"
                         " (useful in combination with the type parameter)",
            "type": "filter by type ",
            settings.SHOW_COUNT: "fetch the number of job ads that matches a taxonomy value "
                                 "(only available when chosen type is provided)"
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
