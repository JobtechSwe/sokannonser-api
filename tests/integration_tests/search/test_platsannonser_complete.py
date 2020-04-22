import os
import sys
import pytest

from sokannonser import app
from sokannonser import settings
from tests.integration_tests.test_resources.check_response import check_response_return_json
from sokannonser.settings import test_api_key


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.parametrize("query, synonyms, expect_success",
                         [('servit', ['servitris', 'servitör'], True),
                          ('servit', ['servitris', 'servitör', 'servitriser', 'servitörer'], True),
                          ('systemutvecklare angu', ['angular', 'angularjs'], True),
                          ('angu', ['angular', 'angularjs'], True),
                          ('ang', ['angularjs', 'angular', 'angular.js', 'angered'], True),
                          ('c#', ['c#'], True),
                          ('pyth', ['python'], True),
                          # check that synonyms are not suggested
                          ('c#', ['c++'], False),
                          ('c#', ['java'], False)])
def test_complete_endpoint_synonyms_typeahead(query, synonyms, expect_success):
    """
    Test that incomplete search queries will return synonyms
    when 'x-feature-include-synonyms-typeahead' is set in headers
    first arg is the query
    second arg is a list of expected synonyms, which all must be found in the response
    third arg True/False determines if synonyms are supposed to be found or not
    """
    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json',
                   settings.X_FEATURE_INCLUDE_SYNONYMS_TYPEAHEAD: 'true'}

        result = testclient.get('/complete', headers=headers, data={'q': query})
        json_response = check_response_return_json(result)
        assert 'typeahead' in json_response
        json_typeahead = json_response['typeahead']
        complete_values = [item['value'] for item in json_typeahead]
        assert len(complete_values) > 0, f"no synonyms found for '{query}'"
        for s in synonyms:
            if expect_success:
                assert s in complete_values, f"Synonym '{s}' not found in response"
            else:
                assert s not in complete_values, f"Synonym '{s}' was found in response"

@pytest.mark.skip("4 failing test cases, skipped until investigated")
@pytest.mark.integration
@pytest.mark.parametrize("query, expected_suggestions", [
    ('servit', ['servicetekniker', 'servicearbete', 'service och underhåll', 'servicedesk', 'servicehandläggare',
                'servicemedarbetare', 'serviceyrke', 'service manager', 'servicebiträde', 'serviceelektriker']),
    ('systemutvecklare angu', ['systemutvecklare angularjs']),
    ('angu', ['angularjs']),
    ('c#', ['c#']),
    ('c+', ['c++']),
    ('ang', ['angularjs', 'angered']),
    ('c', ['civilingenjör', 'c#', 'c', 'can', 'c körkort', 'cnc- operatör', 'c++', 'cad', 'cloud', 'css']),
    ('pyth', ['python']),

    # Failing
    ('servit', ['servitris', 'servitör', 'servitriser', 'servitörer']),
    ('servi', ['servicetekniker', 'servicearbete', 'service och underhåll', 'servicedesk', 'servicehandläggare',
               'servicemedarbetare', 'serviceyrke', 'service manager', 'servicebiträde', 'serviceelektriker']),
    ('angu', ['angular', 'angularjs']),
    ('ang', ['angular', 'angularjs', 'angered'])
])
def test_complete_endpoint_with_auto_complete_suggest(query, expected_suggestions):
    """
    test of /complete endpoint with 'x-feature-spellcheck-typeahead' header
    parameters: query and list of expected result(s)
    """
    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json',
                   settings.X_FEATURE_SPELLCHECK_TYPEAHEAD: 'true'}
        result = testclient.get('/complete', headers=headers, data={'q': query})
        json_response = check_response_return_json(result)
        assert 'typeahead' in json_response
        actual_suggestions = [suggest.get('value') for suggest in json_response.get('typeahead')]
        assert len(actual_suggestions) > 0, f"no suggested values as auto-complete for '{query}'"
        assert len(actual_suggestions) == len(
            expected_suggestions), f"\nQuery: {query}\nExpected suggestions: {expected_suggestions}\nActual suggestions: {actual_suggestions} "
        for s in expected_suggestions:
            assert s in actual_suggestions, f"\Did not find {query} in {actual_suggestions} "



if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
