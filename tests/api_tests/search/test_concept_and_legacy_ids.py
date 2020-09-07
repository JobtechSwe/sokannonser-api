import pytest
from tests.test_resources.helper import get_with_path_return_json
from tests.test_resources.concept_ids.ad_ids_with_all_concept_and_legacy_ids import all_ids
from tests.test_resources.settings import TEST_USE_STATIC_DATA

@pytest.mark.skip("slow")
@pytest.mark.slow
@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="the ids in the test data are no longer available")
@pytest.mark.parametrize("id_concept_legacy", all_ids)
def test_all_ads_for_concept_and_legacy_ids(session, search_url, id_concept_legacy):
    json_response = get_with_path_return_json(session, search_url, path=f"/ad/{id_concept_legacy['id']}", params={})

    assert json_response['occupation']['concept_id'] == id_concept_legacy['occupation_concept_id']
    assert json_response['occupation']['label'] == id_concept_legacy['occupation_label']

    assert json_response['occupation']['legacy_ams_taxonomy_id'] == id_concept_legacy['occupation_legacy_id']
    assert json_response['occupation_group']['concept_id'] == id_concept_legacy['occupation_group_concept_id']
    assert json_response['occupation_group']['legacy_ams_taxonomy_id'] == id_concept_legacy[
        'occupation_group_legacy_id']
    assert json_response['occupation_group']['label'] == id_concept_legacy['occupation_group_label']

    assert json_response['occupation_field']['concept_id'] == id_concept_legacy['occupation_field_concept_id']
    assert json_response['occupation_field']['label'] == id_concept_legacy['occupation_field_label']

