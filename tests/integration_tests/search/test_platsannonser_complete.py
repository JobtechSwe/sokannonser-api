import os
import sys
import pytest

from sokannonser import app
from sokannonser import settings
from tests.integration_tests.test_resources.check_response import check_response_return_json
from sokannonser.settings import headers

@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.parametrize("synonym, expected",
                         [('servit', ['servitris', 'servitör']),
                          ('systemutvecklare angu', ['angular', 'angularjs']),
                          ('angu', ['angular', 'angularjs'])])
def test_complete_one_param_occupation(synonym, expected):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers[settings.X_FEATURE_INCLUDE_SYNONYMS_TYPEAHEAD] = 'true'
        result = testclient.get('/complete', headers=headers, data={'q': synonym})
        json_response = check_response_return_json(result)
        assert 'typeahead' in json_response
        json_typeahead = json_response['typeahead']

        complete_values = [item['value'] for item in json_typeahead]

        assert len(complete_values) > 0, f"no hits for synonym '{synonym}'"
        for exp in expected:
            assert exp in complete_values


@pytest.mark.integration
def test_complete_one_param_competence():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        query = 'angu'
        headers[settings.X_FEATURE_INCLUDE_SYNONYMS_TYPEAHEAD] = 'true'
        result = testclient.get('/complete', headers=headers, data={'q': query})
        json_response = check_response_return_json(result)
        assert 'typeahead' in json_response
        json_typeahead = json_response['typeahead']
        complete_values = [item['value'] for item in json_typeahead]
        assert len(complete_values) > 0, f"no hits for '{query}'"
        assert 'angular' in complete_values
        assert 'angularjs' in complete_values


@pytest.mark.integration
def test_complete_two_params():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    app.testing = True
    with app.test_client() as testclient:
        query = 'systemutvecklare angu'
        headers[settings.X_FEATURE_INCLUDE_SYNONYMS_TYPEAHEAD] = 'true'
        result = testclient.get('/complete', headers=headers, data={'q': query})
        json_response = check_response_return_json(result)
        assert 'typeahead' in json_response
        json_typeahead = json_response['typeahead']
        complete_values = [item['value'] for item in json_typeahead]
        assert len(complete_values) > 0, f"no hits for '{query}'"
        assert 'angular' in complete_values
        assert 'angularjs' in complete_values


@pytest.mark.integration
def test_complete_one_param_competence_special_char():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        query = 'c#'
        headers[settings.X_FEATURE_INCLUDE_SYNONYMS_TYPEAHEAD] = 'true'
        result = testclient.get('/complete', headers=headers, data={'q': query})
        json_response = check_response_return_json(result)
        assert 'typeahead' in json_response
        json_typeahead = json_response['typeahead']

        complete_values = [item['value'] for item in json_typeahead]

        assert len(complete_values) > 0, f"no hits for '{query}'"
        assert 'c#' in complete_values


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
