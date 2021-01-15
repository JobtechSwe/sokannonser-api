import json

from tests.test_resources.helper import get_snapshot_check_number_of_results
from tests.test_resources.settings import NUMBER_OF_ADS
from tests.test_resources.concept_ids.occupation_concept_ids_and_legacy_ids import occupation_pairs, \
    occupation_group_pairs, occupation_field_pairs


def test_occupation_concept_ids_legacy_ids_pair(session_stream):
    """
    Test that concept ids and legacy taxonomy ids are as expected
    """
    response = get_snapshot_check_number_of_results(session_stream, expected_number=NUMBER_OF_ADS)
    list_of_ads = json.loads(response.content.decode('utf8'))
    for ad in list_of_ads:
        for tpl in occupation_pairs:
            if tpl[0] == ad['occupation']['concept_id']:
                assert tpl[1] == ad['occupation']['legacy_ams_taxonomy_id']
        for tpl in occupation_group_pairs:
            if tpl[0] == ad['occupation_group']['concept_id']:
                assert tpl[1] == ad['occupation_group']['legacy_ams_taxonomy_id']
        for tpl in occupation_field_pairs:
            if tpl[0] == ad['occupation_field']['concept_id']:
                assert tpl[1] == ad['occupation_field']['legacy_ams_taxonomy_id']
