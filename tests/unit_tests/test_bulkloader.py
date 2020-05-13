import pytest
import bulkloader.repository as bulkloader


def test_dsl():
    offset = bulkloader.offset
    actual_dsl = bulkloader._es_dsl()
    expected = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "publication_date": {
                                "lte": "now/m+%dH/m" % offset
                            }
                        }
                    },
                    {
                        "range": {
                            "last_publication_date": {
                                "gte": "now/m+%dH/m" % offset
                            }
                        }
                    }
                ]
            }
        },
    }
    assert actual_dsl == expected


@pytest.mark.parametrize("dsl, items, concept_ids, expected_result", [

    ([{'query': {'bool': {'filter': [{'range': {'publication_date': {'lte': 'now/m+2H/m'}}},
                                     {'range': {'last_publication_date': {'gte': 'now/m+2H/m'}}}],
                          'must': [{'range': {'timestamp': {'gte': -3599000, 'lte': 32503676401000}}}]}}}],
     ['workplace_address.region_concept_id', 'workplace_address.city_concept_id',
      'workplace_address.country_concept_id', 'workplace_address.municipality_concept_id'],
     ['N1wJ_Cuu_7Cs'],
     [{'query': {'bool': {'filter': [{'range': {'publication_date': {'lte': 'now/m+2H/m'}}},
                                     {'range': {'last_publication_date': {'gte': 'now/m+2H/m'}}}, {'bool': {
             'should': [{'term': {'workplace_address.region_concept_id': 'N1wJ_Cuu_7Cs'}},
                        {'term': {'workplace_address.city_concept_id': 'N1wJ_Cuu_7Cs'}},
                        {'term': {'workplace_address.country_concept_id': 'N1wJ_Cuu_7Cs'}},
                        {'term': {'workplace_address.municipality_concept_id': 'N1wJ_Cuu_7Cs'}}]}}],
                          'must': [{'range': {'timestamp': {'gte': -3599000, 'lte': 32503676401000}}}]}}}])
    ,
    ([{'query': {'bool': {'filter': [{'range': {'publication_date': {'lte': 'now/m+2H/m'}}},
                                     {'range': {'last_publication_date': {'gte': 'now/m+2H/m'}}}],
                          'must': [{'range': {'timestamp': {'gte': 1585692001000, 'lte': 32503676401000}}}]}}}],
     ['occupation.concept_id.keyword', 'occupation_field.concept_id.keyword', 'occupation_group.concept_id.keyword'],
     ['heGV_uHh_o8W'],
     [{'query': {'bool': {'filter': [{'range': {'publication_date': {'lte': 'now/m+2H/m'}}},
                                     {'range': {'last_publication_date': {'gte': 'now/m+2H/m'}}}, {'bool': {
             'should': [{'term': {'occupation.concept_id.keyword': 'heGV_uHh_o8W'}},
                        {'term': {'occupation_field.concept_id.keyword': 'heGV_uHh_o8W'}},
                        {'term': {'occupation_group.concept_id.keyword': 'heGV_uHh_o8W'}}]}}],
                          'must': [{'range': {'timestamp': {'gte': 1585692001000, 'lte': 32503676401000}}}]}}}])
    ,
    ([{'query': {'bool': {'filter': [{'range': {'publication_date': {'lte': 'now/m+2H/m'}}},
                                     {'range': {'last_publication_date': {'gte': 'now/m+2H/m'}}}],
                          'must': [{'range': {'timestamp': {'gte': 1587792581000, 'lte': 32503676401000}}}]}}}],
     ['occupation.concept_id.keyword', 'occupation_field.concept_id.keyword', 'occupation_group.concept_id.keyword'],
     ['rQds_YGd_quU'],
     [{'query': {'bool': {'filter': [{'range': {'publication_date': {'lte': 'now/m+2H/m'}}},
                                     {'range': {'last_publication_date': {'gte': 'now/m+2H/m'}}}, {'bool': {
             'should': [{'term': {'occupation.concept_id.keyword': 'rQds_YGd_quU'}},
                        {'term': {'occupation_field.concept_id.keyword': 'rQds_YGd_quU'}},
                        {'term': {'occupation_group.concept_id.keyword': 'rQds_YGd_quU'}}]}}],
                          'must': [{'range': {'timestamp': {'gte': 1587792581000, 'lte': 32503676401000}}}]}}}])
    ,
    ([{'query': {'bool': {'filter': [{'range': {'publication_date': {'lte': 'now/m+2H/m'}}},
                                     {'range': {'last_publication_date': {'gte': 'now/m+2H/m'}}}],
                          'must': [{'range': {'timestamp': {'gte': 1577833201000, 'lte': 32503676401000}}}]}}}],
     ['occupation.concept_id.keyword', 'occupation_field.concept_id.keyword', 'occupation_group.concept_id.keyword'],
     ['rQds_YGd_quU', 'rz2m_96d_vyF', 'fsnw_ZCu_v2U'],
     [{'query': {'bool': {'filter': [{'range': {'publication_date': {'lte': 'now/m+2H/m'}}},
                                     {'range': {'last_publication_date': {'gte': 'now/m+2H/m'}}}, {'bool': {
             'should': [{'term': {'occupation.concept_id.keyword': 'rQds_YGd_quU'}},
                        {'term': {'occupation_field.concept_id.keyword': 'rQds_YGd_quU'}},
                        {'term': {'occupation_group.concept_id.keyword': 'rQds_YGd_quU'}},
                        {'term': {'occupation.concept_id.keyword': 'rz2m_96d_vyF'}},
                        {'term': {'occupation_field.concept_id.keyword': 'rz2m_96d_vyF'}},
                        {'term': {'occupation_group.concept_id.keyword': 'rz2m_96d_vyF'}},
                        {'term': {'occupation.concept_id.keyword': 'fsnw_ZCu_v2U'}},
                        {'term': {'occupation_field.concept_id.keyword': 'fsnw_ZCu_v2U'}},
                        {'term': {'occupation_group.concept_id.keyword': 'fsnw_ZCu_v2U'}}]}}],
                          'must': [{'range': {'timestamp': {'gte': 1577833201000, 'lte': 32503676401000}}}]}}}])
    ,
    ([{'query': {'bool': {'filter': [{'range': {'publication_date': {'lte': 'now/m+2H/m'}}},
                                     {'range': {'last_publication_date': {'gte': 'now/m+2H/m'}}}, {'bool': {
            'should': [{'term': {'occupation.concept_id.keyword': 'ek9W_CmD_y2M'}},
                       {'term': {'occupation_field.concept_id.keyword': 'ek9W_CmD_y2M'}},
                       {'term': {'occupation_group.concept_id.keyword': 'ek9W_CmD_y2M'}},
                       {'term': {'occupation.concept_id.keyword': 'kJeN_wmw_9wX'}},
                       {'term': {'occupation_field.concept_id.keyword': 'kJeN_wmw_9wX'}},
                       {'term': {'occupation_group.concept_id.keyword': 'kJeN_wmw_9wX'}}]}}],
                          'must': [{'range': {'timestamp': {'gte': 1580511601000, 'lte': 32503676401000}}}]}}}],
     ['workplace_address.region_concept_id', 'workplace_address.city_concept_id',
      'workplace_address.country_concept_id', 'workplace_address.municipality_concept_id'],
     ['Q78b_oCw_Yq2', 'CifL_Rzy_Mku'],
     [{'query': {'bool': {'filter': [{'range': {'publication_date': {'lte': 'now/m+2H/m'}}},
                                     {'range': {'last_publication_date': {'gte': 'now/m+2H/m'}}}, {'bool': {
             'should': [{'term': {'occupation.concept_id.keyword': 'ek9W_CmD_y2M'}},
                        {'term': {'occupation_field.concept_id.keyword': 'ek9W_CmD_y2M'}},
                        {'term': {'occupation_group.concept_id.keyword': 'ek9W_CmD_y2M'}},
                        {'term': {'occupation.concept_id.keyword': 'kJeN_wmw_9wX'}},
                        {'term': {'occupation_field.concept_id.keyword': 'kJeN_wmw_9wX'}},
                        {'term': {'occupation_group.concept_id.keyword': 'kJeN_wmw_9wX'}}]}}, {'bool': {
             'should': [{'term': {'workplace_address.region_concept_id': 'Q78b_oCw_Yq2'}},
                        {'term': {'workplace_address.city_concept_id': 'Q78b_oCw_Yq2'}},
                        {'term': {'workplace_address.country_concept_id': 'Q78b_oCw_Yq2'}},
                        {'term': {'workplace_address.municipality_concept_id': 'Q78b_oCw_Yq2'}},
                        {'term': {'workplace_address.region_concept_id': 'CifL_Rzy_Mku'}},
                        {'term': {'workplace_address.city_concept_id': 'CifL_Rzy_Mku'}},
                        {'term': {'workplace_address.country_concept_id': 'CifL_Rzy_Mku'}},
                        {'term': {'workplace_address.municipality_concept_id': 'CifL_Rzy_Mku'}}]}}],
                          'must': [{'range': {'timestamp': {'gte': 1580511601000, 'lte': 32503676401000}}}]}}}])
    ,
    ([{'query': {'bool': {'filter': [{'range': {'publication_date': {'lte': 'now/m+2H/m'}}},
                                     {'range': {'last_publication_date': {'gte': 'now/m+2H/m'}}}, {'bool': {
            'should': [{'term': {'occupation.concept_id.keyword': 'NYW6_mP6_vwf'}},
                       {'term': {'occupation_field.concept_id.keyword': 'NYW6_mP6_vwf'}},
                       {'term': {'occupation_group.concept_id.keyword': 'NYW6_mP6_vwf'}},
                       {'term': {'occupation.concept_id.keyword': 'qSXj_aXc_EGp'}},
                       {'term': {'occupation_field.concept_id.keyword': 'qSXj_aXc_EGp'}},
                       {'term': {'occupation_group.concept_id.keyword': 'qSXj_aXc_EGp'}}]}}],
                          'must': [{'range': {'timestamp': {'gte': 1580511601000, 'lte': 32503676401000}}}]}}}],
     ['workplace_address.region_concept_id', 'workplace_address.city_concept_id',
      'workplace_address.country_concept_id', 'workplace_address.municipality_concept_id'],
     ['Q78b_oCw_Yq2', 'QJgN_Zge_BzJ'],
     [{'query': {'bool': {'filter': [{'range': {'publication_date': {'lte': 'now/m+2H/m'}}},
                                     {'range': {'last_publication_date': {'gte': 'now/m+2H/m'}}}, {'bool': {
             'should': [{'term': {'occupation.concept_id.keyword': 'NYW6_mP6_vwf'}},
                        {'term': {'occupation_field.concept_id.keyword': 'NYW6_mP6_vwf'}},
                        {'term': {'occupation_group.concept_id.keyword': 'NYW6_mP6_vwf'}},
                        {'term': {'occupation.concept_id.keyword': 'qSXj_aXc_EGp'}},
                        {'term': {'occupation_field.concept_id.keyword': 'qSXj_aXc_EGp'}},
                        {'term': {'occupation_group.concept_id.keyword': 'qSXj_aXc_EGp'}}]}}, {'bool': {
             'should': [{'term': {'workplace_address.region_concept_id': 'Q78b_oCw_Yq2'}},
                        {'term': {'workplace_address.city_concept_id': 'Q78b_oCw_Yq2'}},
                        {'term': {'workplace_address.country_concept_id': 'Q78b_oCw_Yq2'}},
                        {'term': {'workplace_address.municipality_concept_id': 'Q78b_oCw_Yq2'}},
                        {'term': {'workplace_address.region_concept_id': 'QJgN_Zge_BzJ'}},
                        {'term': {'workplace_address.city_concept_id': 'QJgN_Zge_BzJ'}},
                        {'term': {'workplace_address.country_concept_id': 'QJgN_Zge_BzJ'}},
                        {'term': {'workplace_address.municipality_concept_id': 'QJgN_Zge_BzJ'}}]}}],
                          'must': [{'range': {'timestamp': {'gte': 1580511601000, 'lte': 32503676401000}}}]}}}])

])
def test_add_filter_query(dsl, items, concept_ids, expected_result):
    result = bulkloader.add_filter_query(dsl[0], items, concept_ids)
    assert result == expected_result[0]
