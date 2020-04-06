import sys
import os
import pytest
from market import app
from tests.integration_tests.test_resources.check_response import check_response_return_json

test_api_key = os.getenv('TEST_API_KEY')


@pytest.mark.skip(reason=" http 401 error")
@pytest.mark.integration
def test_passed_deadline():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    from datetime import datetime
    # 03f1762c-1f19-4e4f-842f-214db5db25bc
    app.testing = True
    with app.test_client() as testclient:
        # https://jobtechjobs-api.dev.services.jtech.se/market/search?show-expired=false&q=ekonomi&place=jokkmokk&place=ume%C3%A5&offset=0&limit=5
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/search', headers=headers, data={'show-expired': 'false',
                                                                  'q': 'ekonomi',
                                                                  'place': 'stockholm',
                                                                  'offset': 0,
                                                                  'limit': '100'})
        json_response = check_response_return_json(result)
        deadlines = [hit['application']['deadline'] for hit in json_response['hits']]
        dt_now = datetime.now()

        for deadline in deadlines:
            dt_deadline = datetime.strptime(deadline, '%Y-%m-%dT%H:%M:%S+00:00')
            assert dt_deadline >= dt_now


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
