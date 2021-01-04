import sys

import pytest

from tests.test_resources.helper import get_search


@pytest.mark.integration
def test_search_freetext_and_occupation_name( session):
    """
    Do search with freetext and 'occupation-name' and compare the results
    """


    param_1 = {'q': 'restaurangbiträde stockholm', 'limit': '100'}
    json_response = get_search(session,  param_1)
    ids_freetext = [hit['id'] for hit in json_response['hits']]

    param_2 = {'q': 'restaurangbiträde stockholm', 'limit': '100', 'offset': 80}
    json_response_2 = get_search(session,  param_2)
    ids_freetext.extend([hit['id'] for hit in json_response_2['hits']])

    param_3 = {'occupation-name': '5555', 'q': 'stockholm', 'limit': '100'}
    json_response_tax = get_search(session,  param_3)
    ids_tax = [hit['id'] for hit in json_response_tax['hits']]

    param_4 = {'occupation-name': '5555', 'q': 'stockholm', 'limit': '100', 'offset': 80}
    json_response_tax2 = get_search(session,  param_4)
    ids_tax.extend([hit['id'] for hit in json_response_tax2['hits']])

    result_ids_tax_minus_freetext = sorted(list(set(ids_tax) - set(ids_freetext)))

    # All hits in structured search should be covered when doing an equivalent freetext search.
    assert len(result_ids_tax_minus_freetext) == 0
