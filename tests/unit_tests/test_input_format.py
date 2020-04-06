import pytest
import sys

from flask_restx import inputs


@pytest.mark.unit
def test_regex_input_bulk_zip():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    bulk_regex = r'(\d{4}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])|all)$'
    input_regex = inputs.regex(bulk_regex)

    input = 'all'
    val = input_regex(input)

    assert val == input

    input = '2019-04-01'
    val = input_regex(input)

    assert val == input

    input = '2019-04-42'

    try:
        input_regex(input)
    except ValueError as ve:
        assert ve is not None
    else:
        pytest.fail("expected a ValueError, but no ValueError was raised")
