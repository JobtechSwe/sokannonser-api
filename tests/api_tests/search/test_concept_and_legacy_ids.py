from tests.test_resources.helper import get_with_path_return_json
from tests.test_resources.concept_ids.ad_ids_with_all_concept_and_legacy_ids import all_ids


def test_all_ads_for_concept_and_legacy_ids(session, search_url):
    for test_data in all_ids:
        json_response = get_with_path_return_json(session, search_url, path=f"/ad/{test_data['id']}", params={})
        assert json_response['occupation']['concept_id'] == test_data['occupation_concept_id']
        assert json_response['occupation']['legacy_ams_taxonomy_id'] == test_data['occupation_legacy_id']
        assert json_response['occupation']['label'] == test_data['occupation_label']

        assert json_response['occupation_group']['concept_id'] == test_data['occupation_group_concept_id']
        assert json_response['occupation_group']['legacy_ams_taxonomy_id'] == test_data['occupation_group_legacy_id']
        assert json_response['occupation_group']['label'] == test_data['occupation_group_label']

        assert json_response['occupation_field']['concept_id'] == test_data['occupation_field_concept_id']
        assert json_response['occupation_field']['label'] == test_data['occupation_field_label']
