import pytest

from tests.test_resources.helper import get_search
from tests.test_resources.concept_ids import concept_ids_geo as geo


@pytest.mark.integration
@pytest.mark.parametrize("city, region, country", [
    (geo.stockholm, geo.stockholms_lan, geo.sverige),
    (geo.malmo, geo.skane_lan, geo.sverige)
])
def test_search_municipality(session, search_url, city, region, country):
    """
    Check that parent concept ids (region, country) are correct when searching for a municipality
    """
    json_response = get_search(session, search_url, {'municipality': city})
    hits = json_response['hits']
    for hit in hits:
        assert hit['workplace_address']['municipality_concept_id'] == city
        assert hit['workplace_address']['region_concept_id'] == region
        assert hit['workplace_address']['country_concept_id'] == country


@pytest.mark.integration
@pytest.mark.parametrize("cities, region, country", [
    ([geo.kiruna, geo.lulea, geo.gallivare, geo.kalix, geo.alvsbyn, geo.jokkmokk], geo.norrbottens_lan, geo.sverige),
    ([geo.malmo, geo.bastad, geo.sjobo, geo.kavlinge, geo.helsingborg, geo.angelholm, geo.hoor], geo.skane_lan,
     geo.sverige),
])
def test_search_region(session, search_url, cities, region, country):
    """
    Check that parent (country) and child (municipality) concept ids are correct when searching for ads in a region
    """
    json_response = get_search(session, search_url, {'region': region})
    hits = json_response['hits']
    for hit in hits:
        print(hit['id'])
        assert hit['workplace_address']['municipality_concept_id'] in cities
        assert hit['workplace_address']['region_concept_id'] == region
        assert hit['workplace_address']['country_concept_id'] == country


@pytest.mark.integration
@pytest.mark.parametrize("country", [geo.norge, geo.aland_tillhor_finland, geo.malta, geo.schweiz])
def test_search_country_except_sweden(session, search_url, country):
    """
    Test that countries except Sweden do not have concept ids for municipality and region.
    """
    json_response = get_search(session, search_url, {'country': country})
    hits = json_response['hits']
    for hit in hits:
        assert hit['workplace_address']['municipality_concept_id'] is None
        assert hit['workplace_address']['region_concept_id'] is None
        assert hit['workplace_address']['country_concept_id'] == country


@pytest.mark.integration
def test_search_country_sweden(session, search_url):
    """
    Test that concept ids for municipality and region exists when searching for ads in Sweden
    """
    country = geo.sverige
    json_response = get_search(session, search_url, {'country': country})
    hits = json_response['hits']
    for hit in hits:
        assert hit['workplace_address']['municipality_concept_id'] is not None
        assert hit['workplace_address']['region_concept_id'] is not None
        assert hit['workplace_address']['country_concept_id'] == country
