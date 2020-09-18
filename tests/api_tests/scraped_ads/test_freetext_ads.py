import sys
import pytest
from tests.test_resources.scraped import get_scraped, check_ids, get_actual_ad_ids
from tests.test_resources.settings import NUMBER_OF_SCRAPED_ADS


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.parametrize("query, expected_ids", [
    ('barnmorska', ['19801']),
    ('tandsköterska', []),
    ('kock', ['20301', '42301', '20401']),
    ('Sjuksköterskor',
     ['16401', '17301', '18101', '17601', '44701', '17901', '18701', '19301', '18901', '17501', '17401', '17701',
      '18001', '18201', '18301', '18401', '18501', '18601', '18801', '19001', '19501', '19801', '32301', '32801',
      '34001', '34401', '47001', '49401', '15601', '16701', '17201', '19201', '41301', '45101', '46101', '17801']
     ),
    ('Sjuksköterska',
     ['18301', '18501', '34001', '17401', '18001', '18201', '32301', '34401', '47001', '49401', '32801', '18601',
      '19001', '18801', '18401', '41401', '16401', '17301', '17601', '17701', '17901', '18101', '18701', '18901',
      '19301', '19501', '19801', '44701', '15601', '16701', '17201', '17501', '19201', '19101', '17801']
     )])
def test_freetext_query(session_scraped, scraped_url, query, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')

    json_response = get_scraped(session_scraped, scraped_url, params={'q': query, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


@pytest.mark.smoke
@pytest.mark.integration
def test_no_freetext_query_total_value(session_scraped, scraped_url):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_scraped(session_scraped, scraped_url, params={'limit': '0'})
    expected_number = NUMBER_OF_SCRAPED_ADS
    assert json_response['total']['value'] == expected_number


@pytest.mark.parametrize("query, expected_ids", [
    ('lärare',
     ['10601', '43501', '5701', '7401', '9701', '10501', '43701', '6101', '36501', '31301', '7301', '42601', '47901',
      '10001', '33701', '42701', '7101', '42501', '9301', '7601', '9101', '9601', '10201', '10401', '13601', '43201',
      '43601', '43801', '8501', '43901', '6601', '7701', '7801', '8601', '9201', '9901', '10101', '47301', '10301',
      '10801', '47701', '9401', '42101', '46301', '48301', '7501', '40001', '45801', '10701', '9001', '38401']),
    ('kock', ['20301', '42301', '20401']),
    ('lärare kock',
     ['5701', '6101', '7301', '7401', '7601', '9101', '9601', '9701', '10001', '10201', '10401', '10501', '10601',
      '13601', '31301', '36501', '42601', '43201', '43501', '43601', '43701', '6601', '7701', '7801', '8601', '9201',
      '9901', '33701', '47901', '9301', '42701', '8501', '43801', '7101', '9001', '42501', '43901']),
    ('Sollentuna', ['7901']),
    ('Sollentuna Umeå', ['7901', '48601', '37601', '11301', '11501', '27201', '35601']),
    ('Sjuksköterska Göteborg', ['32301']),
    ('Helsingborg', ['49401', '19001', '24901', '9801', '46601']),
    ('sjuksköterskor',
     ['16401', '17301', '18101', '17601', '44701', '17901', '18701', '19301', '18901', '17501', '17401', '17701',
      '18001', '18201', '18301', '18401', '18501', '18601', '18801', '19001', '19501', '19801', '32301', '32801',
      '34001', '34401', '47001', '49401', '15601', '16701', '17201', '19201', '41301', '45101', '46101', '17801']),
    ('sjuksköterska',
     ['18301', '18501', '34001', '17401', '18001', '18201', '32301', '34401', '47001', '49401', '32801', '18601',
      '19001', '18801', '18401', '41401', '16401', '17301', '17601', '17701', '17901', '18101', '18701', '18901',
      '19301', '19501', '19801', '44701', '15601', '16701', '17201', '17501', '19201', '19101', '17801']),
    ('Uppsala',
     ['11601', '27401', '17901', '34701', '8901', '19601', '20701', '21101', '23601', '24701', '36801', '43401', '4701',
      '10601', '35901', '41301', '33501']),
    ('sjuksköterskor Uppsala', ['17901'])])
def test_freetext_query_multiple_search_terms(session_scraped, scraped_url, query, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_scraped(session_scraped, scraped_url, params={'q': query, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)

    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


@pytest.mark.parametrize("query, expected_ids", [
    ('barnmorska', ['19801']),  # free text
    ('tandsköterska', []),  # no hits expected in test data
    ('barnmorska tandsköterska', []),  # no tandsköterska in test data, no free text search
    ('tandsköterska barnmorska', []),  # no tandsköterska in test data, no free text search
    ('fysioterapeut ', ['33801', '16901']),
    ('fysioterapeut barnmorska', ['33801', '16901']),  # no free text search
    ('barnmorska fysioterapeut', ['33801', '16901']),  # no free text search
    ('chefsbarnmorska fysioterapeut', ['19401', '33801', '16901']),  # both are in enrichment - occupation
    ('chefsbarnmorska', ['19401']),  # occupation
    ('chefsbarnmorska barnmorska', ['19401']),  # only chefsbarnmorksa is used, no free text search for barnmorska
    ('engineer', ['30501', '2201', '2001', '38101']),
    ('developer', ['40701', '24501', '31201']),
    ('developer engineer', ['30501', '2201', '2001', '38101', '40701', '24501', '31201']),
    ('engineer developer', ['30501', '2201', '2001', '38101', '40701', '24501', '31201']),
    ('engineer developer kock', [])])
def test_freetext_query_multiple_search_terms_freetext_and_occupation(session_scraped, scraped_url, query,
                                                                      expected_ids):
    """
    One search term: freetext search is performed
    Multiple search terms:
    Only those where the occupation is found in enrichment are returned. No free text search is done
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_scraped(session_scraped, scraped_url, params={'q': query, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)
    assert json_response['total']['value'] == len(expected_ids)
    assert len(json_response['hits']) == len(expected_ids)


@pytest.mark.parametrize("query, expected_ids", ([
    ("python", ['24401', '30501', '31901']),
    ("java", ['2001', '24401', '24601', '24901']),
    ("java -javautvecklare", ['2001', '24401', '24901']),
    ("java python", ['24401', '2001', '24601', '30501', '24901', '31901']),
    ("java +python", ['24401', '30501', '31901']),
    ("java -python", ['2001', '24601', '24901']),
    ("kock -bagare", ['20301', '42301', '20401']),
    ("pizzabagare", ['20001', '20501']),
    ("bartender", ['20901']),
    ("målare", ['27701', '28401', '28001']),
    ("målare sundsvall", ['28401']),
    ("målare +sundsvall", ['28401']),
    ("målare -sundsvall", ['27701', '28001']),
    ("personlig assistent", ['3401', '3501', '4001', '4101', '3101', '3201', '3601', '3701', '2901']),
    ("personlig assistent +göteborg", ['3501', '3701']),
    ("personlig assistent -göteborg", ['3401', '4001', '4101', '3101', '3201', '3601', '2901']),
    ("utvecklare", ['25401', '24801', '35801', '24201', '24401', '41101', '42201']),
    ("förskollärare",
     ['8101', '8201', '8401', '48901', '8001', '43101', '8301', '48101', '7901', '46501', '34201', '9001', '42501']),
    ("sjuksköterska",
     ['18301', '18501', '34001', '17401', '18001', '18201', '32301', '34401', '47001', '49401', '32801', '18601',
      '19001', '18801', '18401', '41401', '16401', '17301', '17601', '17701', '17901', '18101', '18701', '18901',
      '19301', '19501', '19801', '44701', '15601', '16701', '17201', '17501', '19201', '19101', '17801']),
    ("sjuksköterska -stockholm",
     ['18301', '18501', '34001', '17401', '18001', '18201', '32301', '34401', '47001', '49401', '32801', '18601',
      '19001', '18801', '41401', '17301', '17601', '17701', '17901', '18101', '18701', '19301', '19801', '44701',
      '15601', '16701', '17201', '17501', '19201', '17801'])
]))
def test_plus_minus(session_scraped, scraped_url, query, expected_ids):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_scraped(session_scraped, scraped_url, params={'q': query, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)


@pytest.mark.skip("skip until we find out why they fail")
@pytest.mark.parametrize("query, expected_ids", ([
    ("C#", ['24301', '24401', '30501']),
    ("c-körkort", ['1201', '2701', '6201']),
    (".net", ['24301', '24401', '30501', '45401']),
    ("ci/cd", ['30501', '32201']),
    ("erp-system", ['31001']),
    ("tcp/ip", ['31901', '36701', '45001']),
    ("cad-verktyg", ['33001']),
    ("backend-utvecklare", ['24901']),
    ("it-tekniker", ['49301'])  # this works

]))
def test_special_chars_from_enrichment(session_scraped, scraped_url, query, expected_ids):
    """
    Search for special characters (#/-.) that are found in enrichment: keywords.enriched.skill
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_scraped(session_scraped, scraped_url, params={'q': query, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    check_ids(actual_ids, expected_ids)
