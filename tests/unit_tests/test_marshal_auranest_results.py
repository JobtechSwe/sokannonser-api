import json
import os
import re
import sys
# from pprint import pprint

import pytest

from sokannonser.rest.endpoint.auranest import AuranestSearch

currentdir = os.path.dirname(os.path.realpath(__file__)) + '/'

def get_static_ads_from_file():
    with open(currentdir + 'test_resources/auranest_results.json') as f:
        result = json.load(f)
        # pprint(result)
        return result

@pytest.mark.unit
def test_properties_and_types_marshal_mocked_elastic_result():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    asearch = AuranestSearch()
    esresult = get_static_ads_from_file()
    # pprint(esresult)

    # args = {settings.FREETEXT_QUERY: False, settings.STATISTICS: False}
    marshalled_result = asearch.marshal_default(esresult)
    # pprint(marshalled_result)

    for hit in marshalled_result['hits']:
        content = hit['content']
        words = re.split(r'\s+', content)
        # print(len(words))
        # print(words[-1:])
        assert len(words) <= 101


