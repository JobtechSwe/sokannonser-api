import logging
from flask_restx import Resource

from sokskrapade.repository.querybuilder import QueryBuilder
from sokskrapade.rest import fetchfunction
from sokskrapade.rest import ns_skrapade, jl_query

log = logging.getLogger(__name__)

GROUP = 'occupation-group'
FIELD = 'occupation-field'
MUNICIPALITY = 'municipality'
REGION = 'region'
COUNTRY = 'country'
QUERY = 'q'
LIMIT = 'limit'
OFFSET = 'offset'

#OCCUPATION = 'occupation-name'
#SKILL = 'skill'
#PLACE = 'place'

@ns_skrapade.route('joblinks')
class SearchJobLink(Resource):
    @ns_skrapade.doc(


        description='Search scraped ads using parameters and/or freetext\n'
        'Taxonomy service can be found: https://taxonomy.api.jobtechdev.se/v1/taxonomy/swagger-ui/ '
        'Use it to lookup concept IDs for occupation and location.',
        params={
            GROUP: "One or more occupational group concept ID according to the taxonomy",
            FIELD: "One or more occupational field concept ID according to the taxonomy",
            MUNICIPALITY: "One or more municipality concept ID according to the taxonomy",
            REGION: "One or more region concept ID according to the taxonomy",
            COUNTRY: "One or more country concept ID according to the taxonomy",
            QUERY: "Freetext query",
            OFFSET: "The offset parameter defines the offset "
                    "from the first result you want to fetch. Valid range: (0-%d)" % 2000,
            LIMIT: "Number of results to fetch. Valid range: (0-%d)" % 100,
        }
    )
    @ns_skrapade.expect(jl_query)
    def get(self, **kwargs):
        querybuilder = QueryBuilder()
        args = jl_query.parse_args()
        result = fetchfunction.find_all(args, querybuilder)
        log.info(f'ARGS: {args}')
        log.debug(f'Result: {result}')
        max_score = result.get('max_score', 1.0)
        hits = [dict(hit['_source'],
                     **{'relevance': (hit['_score'] / max_score)
                     if max_score > 0 else 0.0})
                for hit in result.get('hits', [])]
        return self.marshal_results(result, hits)

    def marshal_results(self, esresult, hits):
        total_results = {'value': esresult.get('total', {}).get('value')}
        result = {
            "total": total_results,
            "hits": self.mock_hits_result(hits)
        }
        return result

    def mock_hits_result(self, hits):
        result = []
        for hit in hits:
            result.append({
                "id": str(hit.get('id', "")),
                "external_id": hit.get("originalJobPosting", {}).get("identifier", ""),
                "webpage_url": hit.get("originalJobPosting", {}).get("url", ""),
                "headline": hit.get("originalJobPosting", {}).get("title", ""),
                "brief": hit.get("originalJobPosting", {}).get("brief", ""),
                "workplace_address": hit.get("workplace_address", ""),
                "occupation_group": hit.get("occupation_group", ""),
                "occupation_field": hit.get("occupation_field", ""),
                "sameAs": "",
                "hashsum": hit.get("hashsum", "")
            })
        return result
