import pytest
from tests.test_resources.helper import get_search
from sokannonser.repository.taxonomy import fetch_occupation_collections


@pytest.mark.smoke
@pytest.mark.parametrize("collection", fetch_occupation_collections())
def test_name_and_collection_param(session, search_url, collection):
    """
    Fetch collections from Taxonomy and test them one by one
    Do a search with 'occupation-name' (using concept ids from collection) and save number of ads in result
    Do a search with 'occupation-collection' and save number of ads in result
    Verify that the number of ads are identical regardless of which param is used
    """

    # Search with 'occupation-name'
    list_of_concept_ids = list_of_concept_ids_from_concept(collection)
    params = {'occupation-name': list_of_concept_ids}
    result_json_name = get_search(session, search_url, params)
    number_of_ads_name = result_json_name['total']['value']

    # search with 'occupation-collection'
    params = {'occupation-collection': collection['id']}
    result_json_collection = get_search(session, search_url, params)
    number_of_ads_collection = result_json_collection['total']['value']

    assert number_of_ads_collection == number_of_ads_name, collection['preferred_label']


def list_of_concept_ids_from_concept(concept):
    list_of_ids = []
    for item in concept['related']:
        list_of_ids.append(item['id'])
    return list_of_ids
