from sokannonser.repository.querybuilder import QueryBuilder
import pytest


@pytest.mark.unit
@pytest.mark.parametrize("yrkessamlingar_id, expected", [(["UdVa_jRr_9DE"],
                                                         {'bool': {'should': {'terms': {
                                                             'occupation.concept_id.keyword': ['fFkk_8X8_pym',
                                                                                               '4zLr_jP5_peZ',
                                                                                               '5NxT_WeC_C31']}}}}),
                                                         (["-UdVa_jRr_9DE"],
                                                          {'bool': {'must_not': {'terms': {
                                                              'occupation.concept_id.keyword': ['fFkk_8X8_pym',
                                                                                                '4zLr_jP5_peZ',
                                                                                                '5NxT_WeC_C31']}}}}),
                                                         ([None],
                                                          None),
                                                         ([[]],
                                                          None),
                                                         (["None_existing_concept_id"],
                                                          None)])
def test_build_yrkessamlingar_query(yrkessamlingar_id, expected):
    querybuilder = QueryBuilder()
    querybuilder.occupation_collections = [
        {
            "id": "UdVa_jRr_9DE",
            "related": [
                {
                    "id": "fFkk_8X8_pym"
                },
                {
                    "id": "4zLr_jP5_peZ"
                },
                {
                    "id": "5NxT_WeC_C31"
                }
            ]
        }
    ]
    queryresult = querybuilder.build_yrkessamlingar_query(yrkessamlingar_id)
    assert queryresult == expected
