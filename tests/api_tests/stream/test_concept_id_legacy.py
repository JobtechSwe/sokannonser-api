import json
import pytest

from tests.test_resources.helper import get_snapshot_check_number_of_results
from tests.test_resources.settings import NUMBER_OF_ADS


@pytest.mark.smoke
def test_snapshot(session_stream, stream_url):
    """
    Test snapshot, should return everything
    """
    response = get_snapshot_check_number_of_results(session_stream, stream_url, expected_number=NUMBER_OF_ADS)

    list_of_ads = json.loads(response.content.decode('utf8'))
    print()
    concept_ids = set()
    for ad in list_of_ads:
        c_id = ad['occupation_field']['concept_id']
        l_id = ad['occupation_field']['legacy_ams_taxonomy_id']
        tpl = (c_id, l_id)
        concept_ids.add(tpl)
        # print(f"{ad['occupation']['concept_id']}  {ad['occupation']['legacy_ams_taxonomy_id']}")

    for pair in concept_ids:
        print(f"{pair},")


def test_occupation_concept_ids_legacy_ids_pair(session_stream, stream_url):
    from tests.test_resources.concept_ids.occupation_concept_ids_and_legacy_ids import occupation_pairs, \
        occupation_group_pairs, occupation_field_pairs
    """
    Test 
    """
    response = get_snapshot_check_number_of_results(session_stream, stream_url, expected_number=NUMBER_OF_ADS)
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


def test_print(session_stream, stream_url):
    """
    Test snapshot, should return everything
    """
    list_of_concept_id = []
    response = get_snapshot_check_number_of_results(session_stream, stream_url, expected_number=NUMBER_OF_ADS)
    list_of_ads = json.loads(response.content.decode('utf8'))

    for ad in list_of_ads:
        tmp = {'id': ad['id'],
               'occupation_concept_id': ad['occupation']['concept_id'],
               'occupation_legacy_id': ad['occupation']['legacy_ams_taxonomy_id'],
               'occupation_group_concept_id': ad['occupation_group']['concept_id'],
               'occupation_group_legacy_id': ad['occupation_group']['legacy_ams_taxonomy_id'],
               'occupation_field_concept_id': ad['occupation_field']['concept_id'],
               'occupation_field_legacy_id': ad['occupation_field']['legacy_ams_taxonomy_id']
               }
        list_of_concept_id.append(tmp)
    print()
    for item in list_of_concept_id:
        print(f"{item},")
