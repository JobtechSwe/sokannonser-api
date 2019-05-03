# -*- coding: utf-8 -*-
import logging
import pytest
import sys
import os

from sokannonser.repository import taxonomy as t
from sokannonser.repository.taxonomy import tax_type
from sokannonser.repository import platsannonser
from sokannonser.repository.querybuilder import QueryBuilder
import re

log = logging.getLogger(__name__)
pbquery = QueryBuilder()

tax_stat = [tax_type[t.OCCUPATION], tax_type[t.GROUP], tax_type[t.FIELD],
            tax_type[t.SKILL], tax_type[t.WORKTIME_EXTENT]]
tax_other = [tax_type[t.MUNICIPALITY], tax_type[t.REGION], tax_type[t.PLACE],
             tax_type[t.LANGUAGE]]
tax_noexist = ['', 'blabla', ' ']


@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
@pytest.mark.parametrize("taxonomy_type", tax_stat + tax_other + tax_noexist)
def test_get_stats_for(taxonomy_type):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    # print(platsannonser.get_stats_for(taxonomy_type) )
    if taxonomy_type not in tax_stat:
        try:
            platsannonser.get_stats_for(taxonomy_type)
        except KeyError as e:
            print('KeyError exception. Reason: taxonomy type %s' % str(e))
            assert "'" + taxonomy_type + "'" == str(e)
        except Exception as ex:
            pytest.fail('ERROR: This is not a KeyError exception: %s' % str(ex),
                        pytrace=False)
    else:  # taxonomy_type is in 5 mentioned in platsannonser.py::get_stats_for()
        for k, v in platsannonser.get_stats_for(taxonomy_type).items():
            assert (re.match(r'^[\w\d_-]*$', k) is not None)  # check k is string of int
            assert isinstance(v, int)  # check v is int


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
