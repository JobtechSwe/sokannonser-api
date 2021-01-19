import pytest
import copy

from tests.test_resources.helper import get_search, get_search_with_headers, get_complete, get_complete_with_headers
from tests.test_resources.settings import TEST_USE_STATIC_DATA
from sokannonser.settings import X_FEATURE_FREETEXT_BOOL_METHOD
from tests.test_resources.settings import headers_search


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.parametrize("query, expected, bool_method", [
    ('Bauhaus Kundtjänst', 1, 'and'),
    ('Bauhaus Kundtjänst', 33, 'or'),
    ('Bauhaus Kundtjänst', 33, None),
    ('Sirius crew', 1, 'and'),
    ('Sirius crew', 2, 'or'),
    ('Sirius crew',2, None),
    ('lagstiftning anställning ', 2, 'and'),
    ('lagstiftning anställning ', 252, 'or'),
    ('lagstiftning anställning ', 252, None),
    ('TechBuddy uppdrag', 1, 'and'),
    ('TechBuddy uppdrag', 284, 'or'),
    ('TechBuddy uppdrag', 284, None),
])
def test_freetext_bool_method(session, search_url, query, expected, bool_method):
    """
    Test with 'or' & 'and' values for X_FEATURE_FREETEXT_BOOL_METHOD header flag
    Default value is 'OR' (used in test cases with None as param)
    Searches with 'or' returns more hits
    """
    params = {'q': query, 'limit': 0}
    # use default setting for X_FEATURE_FREETEXT_BOOL_METHOD == 'OR'
    if not bool_method:
        response_json = get_search(session, search_url, params)
    else:
        tmp_headers = copy.deepcopy(headers_search)
        tmp_headers[X_FEATURE_FREETEXT_BOOL_METHOD] = bool_method
        response_json = get_search_with_headers(search_url, params, tmp_headers)

    if TEST_USE_STATIC_DATA:
        assert response_json['total']['value'] == expected


@pytest.mark.integration
@pytest.mark.parametrize("query",
                         ['stockholm sj', 'stor s', 'lärare st', 'special a', 'stockholm  ', '  ', 'programmering  '])
def test_complete_endpoint_with_freetext_bool_method(session, search_url, query):
    """
    test of /complete endpoint with X_FEATURE_FREETEXT_BOOL_METHOD set to 'and' / 'or' / default value
    Verifies that results are identical regardless of bool method
    """
    params = {'q': query, 'limit': 50}

    # no special header, default valuse is used
    result_default = get_complete(session, search_url, params)

    # use 'and'
    tmp_headers = copy.deepcopy(headers_search)
    tmp_headers[X_FEATURE_FREETEXT_BOOL_METHOD] = 'and'
    result_and = get_complete_with_headers(session, search_url, params, tmp_headers)
    # use 'or
    tmp_headers[X_FEATURE_FREETEXT_BOOL_METHOD] = 'or'
    result_or = get_complete_with_headers(session, search_url, params, tmp_headers)
    # check that results are identical regardless of which bool_method is used
    assert result_default['typeahead'] == result_and['typeahead'] == result_or['typeahead']
