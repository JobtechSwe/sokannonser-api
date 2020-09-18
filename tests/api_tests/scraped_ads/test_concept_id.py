import sys
import pytest

from tests.test_resources.scraped import get_scraped, check_ids, get_actual_ad_ids
from tests.test_resources.concept_ids import occupation
from tests.test_resources.concept_ids import occupation_field as field
from tests.test_resources.concept_ids import occupation_group as group
from tests.test_resources.concept_ids import concept_ids_geo as geo


@pytest.mark.parametrize("occupation, expected_ids", [
    (group.barnmorskor, ['19401']),
    (group.tandskoterskor, []),
    (group.kockar_och_kallskankor, ['15101', '20301', '20401', '40601', '42301', '46401', '47101']),
    (group.grundutbildade_sjukskoterskor,
     ['15601', '16401', '16601', '16701', '17201', '17301', '17401', '17501', '17601', '17701', '17801', '17901',
      '18001', '18101', '18201', '18301', '18401', '18501', '18601', '18701', '18801', '18901', '19001', '19101',
      '19301', '19501', '19701', '19801', '19901', '32301', '32801', '34001', '34401', '41301', '41401', '44701',
      '45101', '46101', '46601', '46701', '47001', '49401']),
])
def test_occupation_group(session_scraped, scraped_url, occupation, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'occupation-group': occupation, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


@pytest.mark.parametrize("occupation, expected_ids", [
    (field.naturbruk, ['11801', '11901', '26701']),
    (field.hotell__restaurang__storhushall,
     ['6001', '15101', '20001', '20101', '20201', '20301', '20401', '20501', '20601', '20701', '20801', '20901',
      '37701', '38901', '40601', '42301', '46401', '47101']),
    (field.transport,
     ['601', '701', '801', '901', '1001', '1101', '1201', '1301', '1401', '1501', '13901', '32501', '33301', '34101',
      '36001', '36401', '37601', '38601', '41901', '44401']),
    (field.kultur__media__design, ['12201', '12401']),
    (field.militart_arbete, []),  # OK
])
def test_occupation_field_2(session_scraped, scraped_url, occupation, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'occupation-field': occupation, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)
    assert json_response['total']['value'] == len(expected_ids)


@pytest.mark.parametrize("city, region, country, expected_ids", [
    (geo.stockholm, geo.stockholms_lan, geo.sverige,
     ['801', '2001', '2101', '2601', '8301', '8501', '10001', '11101', '11401', '12201', '12401', '13001', '13501',
      '16401', '18401', '18901', '19101', '19501', '20201', '21001', '21701', '22101', '24501', '25101', '25301',
      '25901', '26401', '27901', '28301', '29101', '29301', '29701', '29901', '30201', '30301', '30401', '30501',
      '30701', '31001', '31201', '33401', '33501', '35401', '36901', '37101', '41501', '42601', '43001', '43801',
      '45601']
     ),
    (geo.malmo, geo.skane_lan, geo.sverige,
     ['1701', '3401', '13401', '23701', '26901', '29801', '31601', '31901', '33101', '35201', '36501', '36601', '45401',
      '46101', '49701']),
    (geo.goteborg, geo.vastra_gotalands_lan, geo.sverige,
     ['3501', '3701', '11001', '11701', '16601', '23301', '25201', '26101', '28101', '32301', '40901']),
    (geo.umea, geo.vasterbottens_lan, geo.sverige, ['11301', '11501', '27201', '37601', '48601'])
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
    (geo.vasterbottens_lan, [geo.skelleftea, geo.sorsele, geo.umea, geo.storuman, geo.dorotea, ], geo.sverige,
     ['2901', '9001', '11301', '11501', '13101', '23901', '27201', '29201', '37601', '42001', '46401', '48601',
      '48901']),
    (geo.skane_lan,
     [geo.lund, geo.helsingborg, geo.sjobo, geo.malmo, geo.trelleborg, geo.hassleholm, geo.perstorp, geo.kristianstad,
      geo.ystad, geo.bromolla, geo.angelholm, geo.bastad, geo.landskrona, geo.tomelilla], geo.sverige,
     ['601', '701', '1701', '2301', '3401', '6001', '9801', '10201', '12701', '13201', '13401', '13901', '15201',
      '16301', '17501', '17801', '19001', '21301', '22901', '23701', '24901', '26901', '29801', '31601', '31701',
      '31801', '31901', '32501', '33101', '35201', '36501', '36601', '42101', '42301', '44601', '45401', '45501',
      '46101', '46201', '46601', '46701', '47201', '47301', '47501', '47601', '48201', '48701', '49401', '49701']

     ),
    (geo.stockholms_lan,
     [geo.sollentuna, geo.sodertalje, geo.varmdo, geo.haninge, geo.sigtuna, geo.nacka, geo.solna, geo.tyreso,
      geo.huddinge, geo.vallentuna, geo.danderyd, geo.stockholm, geo.norrtalje, geo.jarfalla, geo.sundbyberg,
      geo.upplands_bro, geo.upplands_vasby], geo.sverige,
     ['801', '1501', '2001', '2101', '2601', '3801', '3901', '5301', '5501', '6601', '7201', '7401', '7601', '7901',
      '8301', '8501', '9201', '9901', '10001', '10501', '10701', '11101', '11401', '12201', '12401', '13001', '13501',
      '16401', '18401', '18901', '19101', '19401', '19501', '20201', '21001', '21701', '22101', '24501', '25101',
      '25301', '25701', '25901', '26401', '27701', '27901', '28301', '29101', '29301', '29701', '29901', '30201',
      '30301', '30401', '30501', '30701', '30801', '30901', '31001', '31101', '31201', '32601', '32801', '33401',
      '33501', '35401', '35501', '36701', '36901', '37101', '41501', '42501', '42601', '43001', '43201', '43801',
      '44701', '44801', '45101', '45301', '45601', '49201']
     ),
])
def test_search_region(session_scraped, scraped_url, region, expected_cities, country, expected_ids):
    """
    Check that parent (country) and child (municipality) concept ids are correct when searching for ads in a region
    """
    json_response = get_scraped(session_scraped, scraped_url, {'region': region, 'limit': 100})
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
                         [(geo.sverige, 495), (geo.norge, 4), (geo.grekland, 1), (geo.schweiz, 0), (geo.estland, 0),
                          (geo.stockholm, 0)])
def test_search_country(session_scraped, scraped_url, country, expected_number):
    """
    Check that correct number of hits is returned when searching with the 'country' parameter and concept_id
    """
    json_response = get_scraped(session_scraped, scraped_url, params={'country': country, 'limit': 0})
    assert json_response['total']['value'] == expected_number
