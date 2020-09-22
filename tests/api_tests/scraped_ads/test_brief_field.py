import sys
import pytest
from tests.test_resources.scraped import get_scraped, check_ids, get_actual_ad_ids


@pytest.mark.parametrize("query, expected", ([
    ("universitetslektor", [('6401',
                             'Mittuniversitetet är ett lärosäte där människor möts, inspireras och tänker nytt. Vi finns i Sundsvall och Östersund, och har ett brett utbud av utbildningar både på campus och på distans.'),
                            ('6901', 'vid Institutionen för språkdidaktik. Sista ansökningsdag: 2020-05-21.')]),
    ("skogsarbetare", [('11801',
                        'Kort beskrivning av företaget: Bolaget bedriver skogsröjning, kraftledningsröjning, plantering, stödplantering, hyggesrensning, avläggsrensning och annat arbete inom skogsvård, samt annan därmed förenlig verksamhet.Vi söker dig som är ansvarstagande och har en god samarbetsförmåga då man arbetar nära varandra i arbetslaget.')]),

]))
def test_brief(session_scraped, scraped_url, query, expected):
    """
    Check that the 'brief' section is as expected and that order of hits is as expected
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')
    json_response = get_scraped(session_scraped, scraped_url, params={'q': query, 'limit': '100'})
    actual_ids = get_actual_ad_ids(json_response)
    expected_ids = []
    for item in expected:
        expected_ids.append(item[0])

    for index, hit in enumerate(json_response['hits']):
        assert hit['id'] == expected[index][0]
        assert hit['brief'] == expected[index][1]

    check_ids(actual_ids, expected_ids)
