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
    collection_id = collection_info['id']
    expected = collection_info['expected']
    label = collection_info['label']
    print(label)
    params = {'occupation-filter': collection_id, 'offset': 0, 'limit': 100}
    result_json = get_search(session, search_url, params)
    assert result_json['total']['value'] == expected
