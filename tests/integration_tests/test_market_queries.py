import sys
import os
import pytest
from pprint import pprint
from market import app

test_api_key = os.getenv('TEST_API_KEY_MARKET')




# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_passed_deadline():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    from datetime import datetime
    # 03f1762c-1f19-4e4f-842f-214db5db25bc
    app.testing = True
    with app.test_client() as testclient:
        # https://jobtechjobs-api.dev.services.jtech.se/market/search?show-expired=false&q=ekonomi&place=jokkmokk&place=ume%C3%A5&offset=0&limit=5
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        result = testclient.get('/market/search', headers=headers, data={ 'show-expired': 'false',
                                                                        'q': 'ekonomi',
                                                                        'place': 'stockholm',
                                                                        # 'place': 'umeå',
                                                                        'offset': 0,
                                                                        'limit': '100'})
        json_response = result.json
        pprint(json_response)
        # ids = [hit['id'] for hit in json_response['hits']]
        deadlines = [hit['application']['deadline'] for hit in json_response['hits']]

        # print(len(json_response['hits']))

        dt_now = datetime.now()

        for deadline in deadlines:
            dt_deadline = datetime.strptime(deadline, '%Y-%m-%dT%H:%M:%S+00:00')
            # print(dt_now, dt_deadline)
            assert dt_deadline >= dt_now



if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
