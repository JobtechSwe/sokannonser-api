from elasticsearch.exceptions import RequestError
import logging as log
from sokannonser import settings
from . import elastic


def get_concept(tax_id, tax_typ):
    query_dsl = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"id": tax_id}},
                        {"term": {"type": tax_typ}}
                    ]
                }
            }
        }
    return _format_response(elastic.search(index=settings.ES_TAX_INDEX, body=query_dsl))


def find_concepts(query_string=None, parent_code=None, entity_type=None, offset=0, limit=10):
    musts = []
    sort = None
    if query_string:
        musts.append({"term": {"label.autocomplete": query_string}})
    else:
        offset = 0
        limit = 5000
        # No numerical sorting for autocomplete-query
        sort = [
            {
                "num_id": {"order": "asc"}
            }
        ]
    if parent_code:
        musts.append({"term": {"parent.id": parent_code}})
    if entity_type:
        musts.append({"term": {"type": entity_type}})

    if not musts:
        query_dsl = {"query": {"match_all": {}}, "from": offset, "size": limit}
    else:
        query_dsl = {
                "query": {
                    "bool": {
                        "must": musts
                    }
                },
                "from": offset,
                "size": limit
            }
    if sort:
        query_dsl['sort'] = sort
    try:
        log.debug("Taxonomy query: %s" % query_dsl)
        result = elastic.search(index=settings.ES_TAX_INDEX, body=query_dsl)
        return result.get('hits', {})
    except RequestError:
        log.error("Failed to query Elasticsearch")
        return None


