import sys
import pytest

from tests.test_resources.scraped import get_scraped, check_ids, get_actual_ad_ids
from tests.test_resources.concept_ids import occupation
from tests.test_resources.concept_ids import occupation_field as field
from tests.test_resources.concept_ids import occupation_group as group
from tests.test_resources.concept_ids import concept_ids_geo as geo


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.parametrize("occupation, expected_ids", [
    (occupation.barnmorska, [19769, 43643, 19764, 43645, 19765, 43655]),
    (occupation.tandskoterska, [45671, 14662, 14171]),
    # 'tandsköterska' also shows 49580 but that ad has no enrichment for occupation
    (occupation.kock_fartyg, [20208, 20352]),
    (occupation.sjukskoterska__grundutbildad, []),
    (occupation.tandskoterska, [45671, 14662, 14171]),
])
def test_occupation_name(session_scraped, scraped_url, occupation, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'occupation-name': occupation, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


@pytest.mark.parametrize("occupation, expected_ids", [
    (group.barnmorskor, [19769, 43643, 19764, 43645, 19765, 43655]),
    (group.tandskoterskor, [45671, 14662, 14171]),
    # 'tandsköterska' also shows 49580 but that ad has no enrichment for occupation
    (group.kockar_och_kallskankor, [20208, 20352]),
    (group.grundutbildade_sjukskoterskor, []),
])
def test_occupation_group(session_scraped, scraped_url, occupation, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'occupation-group': occupation, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


@pytest.mark.parametrize("occupation, expected_ids", [
    (field.halso__och_sjukvard, [19769, 43643, 19764, 43645, 19765, 43655]),
    (field.hotell__restaurang__storhushall, [20208, 20352]),
    (field.transport, [12242]),
])
def test_occupation_field(session_scraped, scraped_url, occupation, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'occupation-field': occupation, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


@pytest.mark.parametrize("occupation, expected_ids", [
    (field.halso__och_sjukvard, [19769, 43643, 19764, 43645, 19765, 43655]),
    (field.hotell__restaurang__storhushall, [20208, 20352]),
    (field.transport, [12242]),
])
def test_municipality(session_scraped, scraped_url, occupation, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'municipality': occupation, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


@pytest.mark.parametrize("city, region, country, expected_ids", [
    (geo.stockholm, geo.stockholms_lan, geo.sverige, [12242, 49738, 24067, 24968, 49736]),
    (geo.malmo, geo.skane_lan, geo.sverige, []),
    (geo.goteborg, geo.vastra_gotalands_lan, geo.sverige, [12196]),
    (geo.umea, geo.vasterbottens_lan, geo.sverige, [22148, 2261, 45671, 46272])
])
def test_search_municipality(session_scraped, scraped_url, city, region, country, expected_ids):
    """
    Check that parent concept ids (region, country) are correct when searching for a municipality
    """
    json_response = get_scraped(session_scraped, scraped_url, params={'municipality': city, 'limit': '100'})
    hits = json_response['hits']
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)
    for hit in hits:
        assert hit['workplace_address']['municipality_concept_id'] == city
        assert hit['workplace_address']['region_concept_id'] == region
        assert hit['workplace_address']['country_concept_id'] == country


@pytest.mark.parametrize("region, expected_cities, country, expected_ids", [
    (geo.vasterbottens_lan, [geo.umea], geo.sverige, [22148, 2261, 45671, 46272]),
    (geo.skane_lan, [geo.hassleholm, geo.tomelilla, geo.klippan], geo.sverige, [15596, 15799, 22273, 20208]),
    (geo.stockholms_lan, [geo.stockholm, geo.jarfalla, geo.huddinge], geo.sverige,
     [49791, 12242, 49738, 24067, 24968, 49736, 13926, 13508, 3887]),
])
def test_search_region(session_scraped, scraped_url, region, expected_cities, country, expected_ids):
    """
    Check that parent (country) and child (municipality) concept ids are correct when searching for ads in a region
    """
    json_response = get_scraped(session_scraped, scraped_url, {'region': region})
    hits = json_response['hits']
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)
    for hit in hits:
        city = hit['workplace_address']['municipality_concept_id']
        if city is not None:
            assert hit['workplace_address']['municipality_concept_id'] in expected_cities
        assert hit['workplace_address']['region_concept_id'] == region
        assert hit['workplace_address']['country_concept_id'] == country


@pytest.mark.parametrize("country, expected_number",
                         [(geo.sverige, 98), (geo.norge, 1), (geo.schweiz, 0), (geo.estland, 1), (geo.stockholm, 0)])
def test_search_country(session_scraped, scraped_url, country, expected_number):
    """
    Check that correct number of hits is returned when searching with the 'country' parameter and concept_id
    """
    json_response = get_scraped(session_scraped, scraped_url, params={'country': country, 'limit': '100'})
    hits = json_response['hits']
    for hit in hits:
        assert hit['workplace_address']['country_concept_id'] == country
    assert len(hits) == expected_number
