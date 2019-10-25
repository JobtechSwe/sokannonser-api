import os
import sys
from pprint import pprint

import pytest

from sokannonser import app
from sokannonser import settings

test_api_key = os.getenv('TEST_API_KEY')


# @pytest.mark.skip(reason="Temporarily disabled, needs values in field keywords.enriched_synonyms")
@pytest.mark.integration
@pytest.mark.parametrize("synonym, expected",
                         [('servit', ['servitris', 'servitör']),
                          ('systemutvecklare angu', ['angular', 'angularjs']),
                          ('angu', ['angular', 'angularjs'])])
def test_complete_one_param_occupation(synonym, expected):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json',
                   settings.X_FEATURE_INCLUDE_SYNONYMS_TYPEAHEAD: 'true'}
        result = testclient.get('/complete', headers=headers, data={'q': synonym})
        json_response = result.json
        # pprint(json_response)
        assert 'typeahead' in json_response
        json_typeahead = json_response['typeahead']

        complete_values = [item['value'] for item in json_typeahead]

        assert len(complete_values) > 0
        # pprint(complete_values)
        for exp in expected:
            assert exp in complete_values


@pytest.mark.skip(reason="Temporarily disabled, needs values in field keywords.enriched_synonyms")
@pytest.mark.integration
def test_complete_one_param_competence():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json',
                   settings.X_FEATURE_INCLUDE_SYNONYMS_TYPEAHEAD: 'true'}
        result = testclient.get('/complete', headers=headers, data={'q': 'angu'})
        json_response = result.json
        # pprint(json_response)
        assert 'typeahead' in json_response
        json_typeahead = json_response['typeahead']

        complete_values = [item['value'] for item in json_typeahead]

        assert len(complete_values) > 0
        # pprint(complete_values)
        assert 'angular' in complete_values
        assert 'angularjs' in complete_values


@pytest.mark.skip(reason="Temporarily disabled, needs values in field keywords.enriched_synonyms")
@pytest.mark.integration
def test_complete_two_params():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json',
                   settings.X_FEATURE_INCLUDE_SYNONYMS_TYPEAHEAD: 'true'}
        result = testclient.get('/complete', headers=headers, data={'q': 'systemutvecklare angu'})
        json_response = result.json
        # pprint(json_response)
        assert 'typeahead' in json_response
        json_typeahead = json_response['typeahead']

        complete_values = [item['value'] for item in json_typeahead]

        assert len(complete_values) > 0
        # pprint(complete_values)
        assert 'angular' in complete_values
        assert 'angularjs' in complete_values


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
