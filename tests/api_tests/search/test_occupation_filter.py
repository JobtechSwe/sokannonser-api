import pytest
from tests.test_resources.helper import get_search
from tests.test_resources.concept_ids import occupation_collections


@pytest.mark.parametrize("collection_info", occupation_collections.collections_info)
def test_occupation_filter(session, search_url, collection_info):
    """
    Takes info about how many hits are expected when searching with 'occupation-name'
    using the concept ids in each collection.
    Does a query with 'occupation-filter' for each of the collection and checks that
    actual hits are as many as expected
    """
    params = {'occupation-filter': collection_info['id'], 'offset': 0, 'limit': 100}
    result_json = get_search(session, search_url, params)
    assert result_json['total']['value'] == collection_info[
        'expected'], f"collection id: {collection_info['id']}, label: {collection_info['label']}"


@pytest.mark.parametrize("collection", occupation_collections.all_collections['data']['concepts'])
def test_occupation_names_from_collection(session, search_url, collection):
    list_of_concept_ids = list_of_concept_ids_from_concept(collection)
    params = {'occupation-name': list_of_concept_ids, 'offset': 0, 'limit': 0}
    result_json = get_search(session, search_url, params)
    info = find_collection_info(collection['id'])
    assert result_json['total']['value'] == info['expected']


def list_of_concept_ids_from_concept(concept):
    list_of_ids = []
    for item in concept['related']:
        list_of_ids.append(item['id'])
    return list_of_ids


def find_collection_info(concept_id):
    return [x for x in occupation_collections.collections_info if x['id'] == concept_id][0]
