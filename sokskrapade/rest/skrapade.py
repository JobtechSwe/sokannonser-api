import logging
from flask_restx import Resource

from sokskrapade.repository.querybuilder import QueryBuilder
from sokskrapade.rest import fetchfunction
from sokskrapade.rest import ns_skrapade, jl_query

log = logging.getLogger(__name__)


@ns_skrapade.route('scraped')
class SearchJobLink(Resource):
    @ns_skrapade.doc(
        description='Search scraped ads',
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
                "originalJobPosting": {
                    "identifier": hit.get("originalJobPosting", {}).get("identifier", ""),
                    "title": hit.get("originalJobPosting", {}).get("title", ""),
                    "url": hit.get("originalJobPosting", {}).get("url", ""),
                    "sameAs": ""
                },
                "workplace_address": hit.get("workplace_address", ""),
                "occupation": hit.get("occupation", ""),
                "occupation_group": hit.get("occupation_group", ""),
                "occupation_field": hit.get("occupation_field", ""),
                "hashsum": hit.get("hashsum", "")
            })
        return result

