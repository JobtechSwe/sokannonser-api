import json
import pytest


@pytest.mark.integration
def test_unspecified_sweden_workplace(session, search_url):
    url = search_url + "/search?unspecified-sweden-workplace=true&offset=0&limit=100&stats=region"

    response = session.get(url)
    response.raise_for_status()
    hits = json.loads(response.content.decode('utf8'))['hits']

    assert len(hits) == 27
    for hit in hits:
        assert hit['workplace_address']['region'] == 'Ospecificerad arbetsort'
        assert hit['workplace_address']['municipality'] is None
        assert hit['workplace_address']['municipality_code'] is None
        assert hit['workplace_address']['municipality_concept_id'] is None
        assert hit['workplace_address']['region'] == 'Ospecificerad arbetsort'
        assert hit['workplace_address']['region_code'] == '90'
        assert hit['workplace_address']['region_concept_id'] is None
        assert hit['workplace_address']['street_address'] is None
        assert hit['workplace_address']['postcode'] is None
        assert hit['workplace_address']['city'] is None
        assert hit['workplace_address']['coordinates'] == [None, None]
        assert hit['relevance'] == 0.0
