import logging
from flask_restx import Resource

from sokskrapade.repository.querybuilder import QueryBuilder
from sokskrapade.rest import fetchfunction
from sokskrapade.rest import ns_skrapade, jl_query

log = logging.getLogger(__name__)

OCCUPATION = 'occupation-name'
GROUP = 'occupation-group'
FIELD = 'occupation-field'
SKILL = 'skill'
PLACE = 'place'
MUNICIPALITY = 'municipality'
REGION = 'region'
COUNTRY = 'country'
QUERY = 'q'
LIMIT = 'limit'
OFFSET = 'offset'
API_VERSION = '1.0.0'


@ns_skrapade.route('joblinks')
class SearchJobLink(Resource):
    @ns_skrapade.doc(
        description='Search scraped ads using parameters and/or freetext',
        params={
            QUERY: "Fields to freetext search in, in addition to default "
                                     "freetext search",
            OCCUPATION: "One or more occupational concept ID according to the taxonomy",
            GROUP: "One or more occupational group concept ID according to the taxonomy",
            FIELD: "One or more occupational area concept ID according to the taxonomy",
            MUNICIPALITY: "One or more municipality concept ID according to the taxonomy",
            REGION: "One or more region concept ID according to the taxonomy",
            COUNTRY: "One or more country concept ID according to the taxonomy",
            OFFSET: "The offset parameter defines the offset "
                    "from the first result you want to fetchValid range is (0-2000)",
            LIMIT: "Number of results to fetch (0-%d)" % 100,
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
                "id": hit.get('id', ""),
                "external_id": hit.get("originalJobPosting", {}).get("identifier", ""),
                "webpage_url": hit.get("originalJobPosting", {}).get("url", ""),
                "headline": hit.get("originalJobPosting", {}).get("title", ""),
                "workplace_address": hit.get("workplace_address", ""),
                "occupation": hit.get("occupation", ""),
                "occupation_group": hit.get("occupation_group", ""),
                "occupation_field": hit.get("occupation_field", ""),
                "sameAs": "",
                "hashsum": hit.get("hashsum", "")
            })
        return result
