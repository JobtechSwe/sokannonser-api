# -*- coding: utf-8 -*-
import logging
import pytest
import sys
import os

from sokannonser.repository import taxonomy as t
from sokannonser.repository import platsannonser
from sokannonser.repository.querybuilder import QueryBuilder
import re

log = logging.getLogger(__name__)
pbquery = QueryBuilder()

tax_stat = [[t.OCCUPATION], [t.GROUP], [t.FIELD], [t.SKILL]]
tax_other = [[t.MUNICIPALITY], [t.REGION]]
tax_noexist = [['  ', 'blabla', '']]


@pytest.mark.parametrize("taxonomy_type", tax_stat + tax_other + tax_noexist)
def test_get_stats_for_taxonomy_type(taxonomy_type):

    if taxonomy_type not in tax_stat:
        try:
            platsannonser.get_stats_for(taxonomy_type)
        except KeyError as e:
            print('KeyError exception. Reason: taxonomy type %s' % str(e))
            assert "'" + taxonomy_type + "'" == str(e)
        except Exception as ex:
            pytest.fail('ERROR: This is not a KeyError exception: %s (%s)' %
                        (str(ex), taxonomy_type), pytrace=False)
    else:  # taxonomy_type is in 5 mentioned in platsannonser.py::get_stats_for()
        for k, v in platsannonser.get_stats_for(taxonomy_type).items():
            assert (re.match(r'^[\w\d_-]*$', k) is not None)  # check k is string of int
            assert isinstance(v, int)  # check v is int


@pytest.mark.parametrize("taxonomy_type", tax_other + tax_noexist)
def test_get_stats_for_taxonomy_type_neg(taxonomy_type):
    assert platsannonser.get_stats_for(taxonomy_type) == {}



@pytest.mark.parametrize("v", ['a', 'abc', '-1'])
def test_is_char_as_str(v):
    with pytest.raises(AssertionError):
        is_int(v)


@pytest.mark.parametrize("v", ['1', '0', '10000'])
def test_is_int_as_str(v):
    is_int(v)


@pytest.mark.parametrize("v", [0, 1, 1000])
def test_is_int_as_int(v):
    with pytest.raises(TypeError):
        is_int(v)


def is_int(value):
    assert (re.match(r'[0-9]+$', value) is not None)
