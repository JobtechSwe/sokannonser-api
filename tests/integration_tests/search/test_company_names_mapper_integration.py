import sys
import pathlib
import pytest

from sokannonser.repository.companynames_mapper import CompanynamesMapper

print_result = True
from_file = True

filepath = pathlib.Path(__file__).parent.parent / 'test_resources' / 'companynames_test_data.txt'
companynames = CompanynamesMapper(companynames_from_file=from_file, companynames_filepath=filepath)


def test_get_diverse_companyname_in_text():
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    input_value = 'ikea stockholm java 3'
    companynames = CompanynamesMapper(companynames_from_file=from_file, companynames_filepath=filepath)
    concepts = companynames.extract_companynames(input_value)
    assert 'ikea ab' in concepts


@pytest.mark.parametrize("input_value, expected", [
    ('ikea ab', 'ikea ab'),
    ('ikea', 'ikea ab'),
    ('Active Clean', 'active clean i stockholm ab'),
    ('Banan-Kompaniet', 'ab banan-kompaniet')
])
def test_get_companyname_ab_in_text(input_value, expected):
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    assert expected in companynames.extract_companynames(input_value)


def test_get_companyname_multiple_in_text():
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    input = 'Volvo Car'
    concepts = companynames.extract_companynames(input)
    assert 'volvo car mobility ab' in concepts
    assert 'volvo car retail solutions ab' in concepts


@pytest.mark.parametrize("input_value", ['java', 'taxi', 'stockholm', 'löderup'])
def test_no_result(input_value):
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    concepts = companynames.extract_companynames(input_value)
    assert len(concepts) == 0


@pytest.mark.parametrize("input_value", ['taxi stockholm', 'Über nordic', 'Ako byggmästare'])
def test_get_at_least_one_companyname(input_value):
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    concepts = companynames.extract_companynames(input_value)
    assert len(concepts) > 0
