import sys
import pytest
from flask_restx import inputs


@pytest.mark.unit
def test_regex_input_bulk_zip():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    bulk_regex = r'(\d{4}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])|all)$'
    input_regex = inputs.regex(bulk_regex)

    input_value = 'all'
    val = input_regex(input_value)
    assert val == input_value

    input_value = '2019-04-01'
    val = input_regex(input_value)
    assert val == input_value

    wrong_input_value = '2019-04-42'

    with pytest.raises(ValueError):
        input_regex(wrong_input_value)
