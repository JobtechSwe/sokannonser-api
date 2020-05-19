import sys

import pytest

from sokannonser import app
from sokannonser.settings import headers
from tests.integration_tests.test_resources.check_response import check_response_return_json
from tests.integration_tests.test_resources.concept_ids import concept_ids_geo as geo


@pytest.mark.integration
@pytest.mark.parametrize("query, municipality, code, municipality_concept_id, expected_number_of_hits", [
    ('bagare stockholm', 'Stockholm', '0180', geo.stockholm, 3),
    ('lärare stockholm', 'Stockholm', '0180', geo.stockholm, 4),
    ('lärare göteborg', 'Göteborg', '1480', geo.goteborg, 4),
])
def test_freetext_work_and_location_details(query, municipality, code, municipality_concept_id,
                                            expected_number_of_hits):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    app.testing = True
    with app.test_client() as testclient:
        result = testclient.get('/search', headers=headers, data={'q': query, 'limit': '100'})
        json_response = check_response_return_json(result)
        hits_total = json_response['total']['value']
        assert int(hits_total) == expected_number_of_hits, f"wrong number of hits for query '{query}'"
        hits = json_response['hits']

        for hit in hits:
            assert hit['workplace_address']['municipality'] == municipality
            assert hit['workplace_address']['municipality_code'] == code
            assert hit['workplace_address']['municipality_concept_id'] == municipality_concept_id


@pytest.mark.skip("work in progress")
@pytest.mark.parametrize("query, id_1, id_2, expected_number_of_hits", [
    ('bagare kock Stockholm Göteborg', '000', '123', 15),
])
def test_freetext_two_work_and_two_locations_details(query, id_1, id_2, expected_number_of_hits):
    print('==================', sys._getframe().f_code.co_name, '================== ')
    app.testing = True
    with app.test_client() as testclient:
        result = testclient.get('/search', headers=headers, data={'q': query, 'limit': '100'})
        json_response = check_response_return_json(result)
        hits_total = json_response['total']['value']
        assert int(hits_total) == expected_number_of_hits, f"wrong number of hits for query '{query}'"
        hits = json_response['hits']

        # assert hits[0]['id'] == '23783846'  #h as both bagare and kock in ad but is 6th hit
        for hit in hits:
            result = f"{hit['headline']}"
            print((result))
