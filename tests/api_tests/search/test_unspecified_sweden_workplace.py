import pytest
from tests.test_resources.helper import get_search


@pytest.mark.integration
def test_unspecified_sweden_workplace(session):
    params = {'unspecified-sweden-workplace': 'true', 'offset': 0, 'limit': 100, 'stats': 'region'}
    result_json = get_search(session, params)
    hits = result_json['hits']
    assert len(hits) >= 46  # for use on static test data or prod
    for hit in hits:
        assert hit['workplace_address']['region'] is None
        assert hit['workplace_address']['municipality'] is None
        assert hit['workplace_address']['municipality_code'] is None
        assert hit['workplace_address']['municipality_concept_id'] is None
        assert hit['workplace_address']['region'] is None
        assert hit['workplace_address']['region_code'] is None
        assert hit['workplace_address']['region_concept_id'] is None
        assert hit['workplace_address']['street_address'] is None
        assert hit['workplace_address']['postcode'] is None
        assert hit['workplace_address']['city'] is None
        assert hit['workplace_address']['coordinates'] == [None, None]
        assert hit['relevance'] == 0.0
