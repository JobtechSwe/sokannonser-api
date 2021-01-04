import sys
import pytest
from tests.test_resources.helper import get_search, compare


@pytest.mark.skip(
    reason="Temporarily disabled. Needs fix according to Trello Card #137, Multipla ord i ett yrke")  # Missing test data?
@pytest.mark.integration
def test_freetext_query_ssk( session):

    query = 'stockholm grundutbildad sjuksköterska'
    json_response = get_search(session,  params={'q': query, 'limit': '100'})

    assert json_response['freetext_concepts']['occupation'][0] == 'sjuksköterska'
    assert json_response['freetext_concepts']['location'][0] == 'stockholm'
    expected = 999999
    compare(json_response['total']['value'], expected=expected)


@pytest.mark.skip("Test does not find expected ad")
@pytest.mark.integration
@pytest.mark.parametrize("synonym", ['montessori'])
def test_freetext_query_synonym_param(session, synonym):
    json_response = get_search(session,  params={'q': synonym, 'limit': '100'})
    assert json_response['freetext_concepts']['skill'][0] == 'montessoripedagogik'

    hits_total = json_response['total']['value']
    compare(hits_total, 1)
    # todo: Should get hits enriched with 'montessoripedagogik'.
    #  ad 23891324 in testdata mentions 'montessoripedagogik' in description
