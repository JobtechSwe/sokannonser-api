from pytest_bdd import scenario, given, when, then
import pytest, os, sys
from sokannonser import app
from jobtech.common import *

@scenario('open-api/top_fields.feature', 'Get fields')
def test_scenario():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    '''test'''

test_api_key = os.getenv('TEST_API_KEY')
app.testing = True

@given("I am authorised user")
def given():
    pass

@when('I request search')
def when():

    pass


@then('I get all top level fields')
def then():
    assert True



