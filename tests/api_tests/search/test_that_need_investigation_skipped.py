import pytest
from tests.test_resources.helper import get_search, compare


@pytest.mark.skip(
    reason="Temporarily disabled. Needs fix according to Trello Card #137, Multipla ord i ett yrke")
def test_freetext_query_ssk(session):
    query = 'stockholm grundutbildad sjuksköterska'
    json_response = get_search(session, params={'q': query, 'limit': '0'})

    assert json_response['freetext_concepts']['occupation'][0] == 'sjuksköterska'
    assert json_response['freetext_concepts']['location'][0] == 'stockholm'
    expected = 999999
    compare(json_response['total']['value'], expected=expected)
