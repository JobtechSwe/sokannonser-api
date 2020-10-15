from sokannonser.repository.querybuilder import QueryBuilder
import pytest


@pytest.mark.unit
@pytest.mark.parametrize("collection_id, expected", [(["UdVa_jRr_9DE"],
                                                      {'bool': {'should': {'terms': {
                                                          'occupation.concept_id.keyword': ['fFkk_8X8_pym',
                                                                                            '4zLr_jP5_peZ',
                                                                                            '5NxT_WeC_C31']}}}}),
                                                     (["-UdVa_jRr_9DE"],
                                                      {'bool': {'must_not': {'terms': {
                                                          'occupation.concept_id.keyword': ['fFkk_8X8_pym',
                                                                                            '4zLr_jP5_peZ',
                                                                                            '5NxT_WeC_C31']}}}}),
                                                     ([None], None), ([[]], None),
                                                     (["None_existing_concept_id"], None)])
def test_build_occupation_collection_query(collection_id, expected):
    querybuilder = QueryBuilder()
    querybuilder.occupation_collections = {
        "UdVa_jRr_9DE": [
            "fFkk_8X8_pym",
            "4zLr_jP5_peZ",
            "5NxT_WeC_C31"]
    }
    query_result = querybuilder.build_yrkessamlingar_query(collection_id)
    assert query_result == expected
