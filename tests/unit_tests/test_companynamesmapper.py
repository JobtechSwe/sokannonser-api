import pytest
import sys
import os
from pprint import pprint

from sokannonser.repository.companynames_mapper import CompanynamesMapper

print_result = True
from_file = True

currentdir = os.path.dirname(os.path.realpath(__file__)) + '/'
filepath = currentdir + 'test_resources/test_companynames.txt'
companynames = CompanynamesMapper(companynames_from_file=from_file, companynames_filepath=filepath)


def print_result_output(input_value, output_value):
    if print_result:
        print('Input: %s' % input_value)
        print('Output:')
        pprint(output_value)


@pytest.mark.unit
def test_get_diverse_companyname_in_text():
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    input = 'ikea stockholm java 3'
    companynames2 = CompanynamesMapper(companynames_from_file=from_file, companynames_filepath=filepath)

    concepts = companynames2.extract_companynames(input)
    print_result_output(input, concepts)
    assert 'ikea ab' in concepts


@pytest.mark.unit
def test_get_companyname_ab_in_text():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    input = 'ikea ab'
    concepts = companynames.extract_companynames(input)
    print_result_output(input, concepts)
    assert 'ikea ab' in concepts


@pytest.mark.unit
def test_get_companyname_ab_in_text2():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    input = 'ikea'
    concepts = companynames.extract_companynames(input)
    print_result_output(input, concepts)
    assert 'ikea ab' in concepts


@pytest.mark.unit
def test_get_companyname_multiple_in_text():
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    input = 'Volvo Car'
    concepts = companynames.extract_companynames(input)
    print_result_output(input, concepts)
    assert 'volvo car mobility ab' in concepts
    assert 'volvo car retail solutions ab' in concepts


@pytest.mark.unit
def test_get_companyname_multiple_words_in_text():
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    input = 'Active Clean'
    concepts = companynames.extract_companynames(input)
    print_result_output(input, concepts)
    assert 'active clean i stockholm ab' in concepts


@pytest.mark.unit
def test_get_ab_companyname_in_text():
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    input = 'Banan-Kompaniet'
    concepts = companynames.extract_companynames(input)
    print_result_output(input, concepts)
    assert 'ab banan-kompaniet' in concepts


@pytest.mark.unit
def test_get_one_companyname_in_text3():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    input = 'taxi'
    concepts = companynames.extract_companynames(input)
    print_result_output(input, concepts)
    assert len(concepts) == 0


@pytest.mark.unit
def test_get_one_companyname_in_text4():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    input = 'taxi stockholm'
    concepts = companynames.extract_companynames(input)
    print_result_output(input, concepts)
    assert len(concepts) > 0


@pytest.mark.unit
def test_get_one_companyname_unicode():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    input = 'Über nordic'
    concepts = companynames.extract_companynames(input)
    print_result_output(input, concepts)
    assert len(concepts) > 0


@pytest.mark.unit
def test_get_companyname_collides_with_skill():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    input = 'java'
    concepts = companynames.extract_companynames(input)
    print_result_output(input, concepts)
    assert len(concepts) == 0


@pytest.mark.unit
def test_get_companyname_one_part_companyname():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    input = 'Ako byggmästare'
    concepts = companynames.extract_companynames(input)
    print_result_output(input, concepts)
    assert len(concepts) > 0


@pytest.mark.unit
def test_get_companyname_city_and_companyname():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    input = 'stockholm'
    concepts = companynames.extract_companynames(input)
    print_result_output(input, concepts)
    assert len(concepts) == 0


@pytest.mark.unit
def test_get_companyname_city_and_not_companyname():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    input = 'löderup'
    concepts = companynames.extract_companynames(input)
    print_result_output(input, concepts)
    assert len(concepts) == 0


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m unit'])
