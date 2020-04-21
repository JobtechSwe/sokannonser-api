import os
import sys
import pytest

from sokannonser import app
from sokannonser import settings
from tests.integration_tests.test_resources.check_response import check_response_return_json
from sokannonser.settings import headers


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
    """
    app.testing = True
    with app.test_client() as testclient:
        headers[settings.X_FEATURE_INCLUDE_SYNONYMS_TYPEAHEAD] = 'true'
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
        print(synonyms)


# This test case is for test complete endpoint with auto complete suggest
# This test case is not good, will fix in future
@pytest.mark.integration
def test_complete_endpoint_with_auto_complete_suggest():
    app.testing = True
    with app.test_client() as testclient:
        query = 'pyth'
        headers[settings.X_FEATURE_SPELLCHECK_TYPEAHEAD] = 'true'
        result = testclient.get('/complete', headers=headers, data={'q': query})
        json_response = check_response_return_json(result)

        assert 'typeahead' in json_response

        suggest_value = [suggest.get('value') for suggest in json_response.get('typeahead')]
        assert len(suggest_value) > 0, f"no suggested values as auto-complete for '{query}'"
        assert 'python' in suggest_value, f"'python' not suggested as auto-complete for '{query}'"


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
