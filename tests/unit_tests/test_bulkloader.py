import sys
import pytest
import bulkloader.repository as bulkloader
from flask_restx import inputs
from tests.unit_tests.test_resources import test_data


def test_dsl():
    offset = bulkloader.offset
    actual_dsl = bulkloader._es_dsl()
    expected = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "publication_date": {
                                "lte": "now/m+%dH/m" % offset
                            }
                        }
                    },
                    {
                        "range": {
                            "last_publication_date": {
                                "gte": "now/m+%dH/m" % offset
                            }
                        }
                    }
                ]
            }
        },
    }
    assert actual_dsl == expected


@pytest.mark.parametrize("dsl, items, concept_ids, expected_result", test_data.data_for_test_add_filter_query)
def test_add_filter_query(dsl, items, concept_ids, expected_result):
    result = bulkloader.add_filter_query(dsl[0], items, concept_ids)
    assert result == expected_result[0]


def test_format_removed_ad():
    ad = test_data.ad_for_test_format_removed_ads
    result = bulkloader.format_removed_ad(ad)
    expected_id = '24025897'

    ad_id = result['id']
    assert isinstance(ad_id, str), f"id was of type: {type(ad_id)}"
    expected = {'id': expected_id, 'removed': False, 'removed_date': None, 'occupation': 'bXNH_MNX_dUR',
                'occupation_group': 'Z8ci_bBE_tmx', 'occupation_field': 'NYW6_mP6_vwf', 'municipality': 'dJbx_FWY_tK6',
                'region': 'NvUF_SP1_1zo', 'country': 'i46j_HmG_v64'}
    assert result == expected


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

    input_value = '2019-04-42'

    try:
        input_regex(input_value)
    except ValueError as ve:
        assert ve is not None
    else:
        pytest.fail("expected a ValueError, but no ValueError was raised")
