# -*- coding: utf-8 -*-
import logging
import pytest
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


@pytest.mark.parametrize("taxonomy_type", tax_stat)
def test_get_stats_for_taxonomy_type(taxonomy_type):
    for k, v in platsannonser.get_stats_for(taxonomy_type).items():
        assert (re.match(r'^[\w\d_-]*$', k) is not None)  # check k is string of int
        assert isinstance(v, int)  # check v is int


@pytest.mark.parametrize("taxonomy_type", tax_other + tax_noexist)
def test_get_stats_for_taxonomy_type_neg(taxonomy_type):
    assert platsannonser.get_stats_for(taxonomy_type) == {}


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m unit'])
