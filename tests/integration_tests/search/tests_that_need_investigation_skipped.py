import sys

import pytest

# from sokannonser import app
from tests.test_resources import headers
from tests.test_resources import check_response_return_json


# The tests in this file were skipped with the messages "to be removed".
# Needs more investigation. Do we have enough coverage of enrichement?

@pytest.mark.skip("lacking enrichment - does not find field 'keywords'")
@pytest.mark.integration
def test_freetext_query_one_param_deleted_enriched():
    print('==================', sys._getframe().f_code.co_name, '================== ')
    app.testing = True
    with app.test_client() as testclient:
        result = testclient.get('/search', headers=headers, data={'q': 'gymnasielärare', 'limit': '10'})
        json_response = check_response_return_json(result)
        assert int(json_response['total']['value']) > 0
        hits = json_response['hits']
        assert len(hits) <= 10
        try:
            keywords = hits[0]['keywords']
        except KeyError:
            print("KeyError - could not find field 'keywords'")
            raise
        assert 'extracted' in keywords
        assert 'enriched' not in keywords

@pytest.mark.skip("lacking enrichment - Field 'found_in_enriched' was not found")
@pytest.mark.integration
def test_freetext_query_one_param_found_in_enriched_pos():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        result = testclient.get('/search', headers=headers, data={'q': 'diskare', 'limit': '100'})
        json_response = check_response_return_json(result)
        hits = json_response['hits']
        assert len(hits) > 0
        assert 'found_in_enriched' in hits[0]

@pytest.mark.skip("lacking enrichment - Field 'found_in_enriched' was not found")
@pytest.mark.integration
def test_freetext_query_one_param_found_in_enriched_neg():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    app.testing = True
    with app.test_client() as testclient:
        result = testclient.get('/search', headers=headers, data={'q': 'sjuksköterska'})
        json_response = check_response_return_json(result)
        hits = json_response['hits']
        assert len(hits) > 0
        for hit in hits:
            assert 'found_in_enriched' in hit, "field 'found_in_enriched' was not found"
            assert hit['found_in_enriched'] is False, "field 'found_in_enriched' was not False as expected"


@pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_freetext_query_geo_param2():
    print('==================', sys._getframe().f_code.co_name, '================== ')

    # kista: 119 (46)
    # gärdet: 62 (8)
    # råsunda: 8 (8)
    # stockholm: 5826 (1196)
    # skåne: 2718 (260)
    # värmland: 103 (47)
    # örebro: 351 (178)
    # örebros län: 66 (66)

    app.testing = True
    with app.test_client() as testclient:
        # result = testclient.get('/search', headers=headers, data={'q': 'sjukssköterska noggran javasscript',
        #                                                           'limit': '1'})
        result_freetext = testclient.get('/search', headers=headers, data={'q': 'restaurangbiträde stockholm',
                                                                           'limit': '100'})
        json_response = result_freetext.json
        # pprint(json_response)

        hits_total = json_response['total']['value']
        # print(hits_total)

        ids_freetext = [hit['id'] for hit in json_response['hits']]
        result_freetext2 = testclient.get('/search', headers=headers, data={'q': 'restaurangbiträde stockholm',
                                                                            'limit': '100', 'offset': 80})
        json_response2 = result_freetext2.json
        ids_freetext.extend([hit['id'] for hit in json_response2['hits']])

        # pprint(sorted(ids_freetext))

        result_taxonomy = testclient.get('/search', headers=headers, data={'occupation-name': '5555', 'q': 'stockholm',
                                                                           'limit': '100'})
        json_response_tax = result_taxonomy.json
        # pprint(json_response)

        hits_total_tax = json_response_tax['total']['value']
        # print(hits_total_tax)

        ids_tax = [hit['id'] for hit in json_response_tax['hits']]

        result_taxonomy2 = testclient.get('/search', headers=headers, data={'occupation-name': '5555', 'q': 'stockholm',
                                                                            'limit': '100', 'offset': 80})
        json_response_tax2 = result_taxonomy2.json
        ids_tax.extend([hit['id'] for hit in json_response_tax2['hits']])

        # pprint(sorted(ids_tax))

        result_ids_tax_minus_freetext = sorted(list(set(ids_tax) - set(ids_freetext)))
        # print('tax - free', result_ids_tax_minus_freetext)
        # All hits in structured search should be covered when doing an equivalent freetext search.
        assert len(result_ids_tax_minus_freetext) == 0
        # print('free - tax', sorted(list(set(ids_freetext) - set(ids_tax))))
