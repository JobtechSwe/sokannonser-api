import os
import pytest
from flask import Flask
from werkzeug.exceptions import Unauthorized
from werkzeug.datastructures import Headers
import sys

from sokannonser.rest.decorators import *


app = Flask('mytestapplication')

@pytest.mark.unit
def test_check_api_key_no_key():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    with app.test_request_context():
        @check_api_key
        def function_to_test():
            print('This line should never be printed since user has no valid API key')

        with pytest.raises(Unauthorized):
            function_to_test()



@pytest.mark.unit
def test_check_api_key_backdoor():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    d = Headers()
    d.add(settings.APIKEY, settings.APIKEY_BACKDOOR)
    with app.test_request_context(headers=d):
        @check_api_key
        def backdoor_function_to_test():
            print('This line should be printed since user has a backdoor key')
            return True

        assert backdoor_function_to_test() == True


@pytest.mark.unit
def test_check_api_key_valid():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    encoded_key = base64.b64encode('test.testsson@test.se'.encode("utf-8"))
    d = Headers()
    d.add(settings.APIKEY, encoded_key)
    with app.test_request_context(headers=d):
        @check_api_key
        def valid_key_function_to_test():
            print('This line should be printed since user has a valid API key')
            return True

        assert valid_key_function_to_test() == True

@pytest.mark.unit
def test_check_api_key_not_valid():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    encoded_key = base64.b64encode('not_a_valid_email_address'.encode("utf-8"))
    d = Headers()
    d.add(settings.APIKEY, encoded_key)
    with app.test_request_context(headers=d):
        @check_api_key
        def non_valid_key_function_to_test():
            print('This line should not be printed since user doesnt have a valid API key')
            return True

        with pytest.raises(Unauthorized):
            non_valid_key_function_to_test()

@pytest.mark.unit
def test_check_api_key_not_valid_and_base64():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    d = Headers()
    d.add(settings.APIKEY, 'test.testsson@test.se')
    with app.test_request_context(headers=d):
        @check_api_key
        def non_base64_key_function_to_test():
            print('This line should not be printed since user doesnt have a base64-encoded API key')
            return True

        with pytest.raises(Unauthorized):
            non_base64_key_function_to_test()





if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra','-m unit'])