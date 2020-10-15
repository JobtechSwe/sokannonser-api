import sys
import pytest
import bulkloader.repository as bulkloader
from flask_restx import inputs


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


def test_format_removed_ad():
    ad = {'id': 24025897, 'external_id': None,
          'headline': 'Sjuksköterska sökes till bemanningsuppdrag med hög ersättning!',
          'application_deadline': '2020-05-03T23:59:59', 'number_of_vacancies': 1, 'description': {
            'text': 'Är du sjuksköterska och söker efter nya uppdrag? Eller kanske helt ny inom bemanning och vill veta mer?\nOavsett vad kan vi förhoppningsvis hjälpa dig att finna det du söker. Vi svarar på frågor och planerar ett upplägg tillsammans utefter dina önskemål för att du ska ha möjlighet att arbeta på dina villkor. \nVi är med från uppläggets start och ser fram emot att följa din resa, vi upplever nya platser tillsammans! Vi har i dagsläget uppdrag runtom i stort sett över hela Sverige, i alla dess former och med attraktiva ersättningar.\nFör oss är en viktig del att du ska känna dig trygg under hela din arbetsperiod varför du utöver din lön erhåller bland annat följande förmåner:\n·        Tjänstepension\n·        Övriga försäkringar\n·        Personlig kontaktperson som är tillgänglig & engagerad\n·        Ekonomisk ersättning för boende & resor\n·        Utbildningar\n\n\nKvalifikationer:\nVi söker dig som är legitimerad sjuksköterska med yrkeserfarenhet och referenser som kan intyga din kompetens. Du har goda kunskaper i det svenska språket, både i tal och skrift.\n\n\nPersonliga egenskaper:\nDu är självständig både ensam och i grupp. Du ska kunna samarbeta med sjuksköterskor och läkare samt vara intresserad och göra ditt yttersta för patienterna. Du är säker i din yrkesroll, hjälpsam, engagerad och tillmötesgående.\n\n\nOmfattning:\nDeltid/Heltid, Rotation: dag, kväll och natt. Även helg kan förekomma.\n\n\nAnsökan\nVälkommen med din ansökan via mail alternativ intresseanmälan på vår hemsida www.vivabemanning.se\nTelefon:  TELEPHONENO \nMail:  EMAIL  \nKänner du möjligtvis även en sjuksköterska som kan vara lämplig? Vi tar mer än gärna emot förslag.\n\n\n#jobbjustnu',
            'text_formatted': '<p>Är du sjuksköterska och söker efter nya uppdrag? Eller kanske helt ny inom bemanning och vill veta mer?</p><p>Oavsett vad kan vi förhoppningsvis hjälpa dig att finna det du söker. Vi svarar på frågor och planerar ett upplägg tillsammans utefter dina önskemål för att du ska ha möjlighet att arbeta på dina villkor. </p><p>Vi är med från uppläggets start och ser fram emot att följa din resa, vi upplever nya platser tillsammans! Vi har i dagsläget uppdrag runtom i stort sett över hela Sverige, i alla dess former och med attraktiva ersättningar.</p><p>För oss är en viktig del att du ska känna dig trygg under hela din arbetsperiod varför du utöver din lön erhåller bland annat följande förmåner:</p><p>·        Tjänstepension</p><p>·        Övriga försäkringar</p><p>·        Personlig kontaktperson som är tillgänglig &amp; engagerad</p><p>·        Ekonomisk ersättning för boende &amp; resor</p><p>·        Utbildningar</p><p><br></p><p><strong>Kvalifikationer:</strong></p><p>Vi söker dig som är legitimerad sjuksköterska med yrkeserfarenhet och referenser som kan intyga din kompetens. Du har goda kunskaper i det svenska språket, både i tal och skrift.</p><p><br></p><p><strong>Personliga egenskaper:</strong></p><p>Du är självständig både ensam och i grupp. Du ska kunna samarbeta med sjuksköterskor och läkare samt vara intresserad och göra ditt yttersta för patienterna. Du är säker i din yrkesroll, hjälpsam, engagerad och tillmötesgående.</p><p><br></p><p><strong>Omfattning:</strong></p><p>Deltid/Heltid, Rotation: dag, kväll och natt. Även helg kan förekomma.</p><p><br></p><p><strong>Ansökan</strong></p><p>Välkommen med din ansökan via mail alternativ intresseanmälan på vår hemsida www.vivabemanning.se</p><p>Telefon:  TELEPHONENO </p><p>Mail:  EMAIL  </p><p>Känner du möjligtvis även en sjuksköterska som kan vara lämplig? Vi tar mer än gärna emot förslag.</p><p><br></p><p>#jobbjustnu</p>',
            'company_information': None, 'needs': None, 'requirements': None, 'conditions': None},
          'employment_type': {'concept_id': '1paU_aCR_nGn', 'label': 'Behovsanställning',
                              'legacy_ams_taxonomy_id': '4'},
          'salary_type': {'concept_id': 'oG8G_9cW_nRf', 'label': 'Fast månads- vecko- eller timlön',
                          'legacy_ams_taxonomy_id': '1'}, 'salary_description': None, 'duration': None,
          'working_hours_type': None, 'scope_of_work': {'min': None, 'max': None}, 'access': None,
          'employer': {'phone_number': None, 'email': None, 'url': 'www.vivabemanning.se',
                       'organization_number': '5591982029', 'name': 'Viva Bemanning AB', 'workplace': 'Sundsvall',
                       'workplace_id': '87189900'},
          'application_details': {'information': None, 'reference': None, 'email': ' EMAIL ', 'via_af': False,
                                  'url': 'http://www.vivabemanning.se', 'other': None}, 'experience_required': True,
          'access_to_own_car': False, 'driving_license_required': False,
          'occupation': {'concept_id': 'bXNH_MNX_dUR', 'label': 'Sjuksköterska, grundutbildad',
                         'legacy_ams_taxonomy_id': '7296'},
          'occupation_group': {'concept_id': 'Z8ci_bBE_tmx', 'label': 'Grundutbildade sjuksköterskor',
                               'legacy_ams_taxonomy_id': '2221'},
          'occupation_field': {'concept_id': 'NYW6_mP6_vwf', 'label': 'Hälso- och sjukvård',
                               'legacy_ams_taxonomy_id': '8'},
          'workplace_address': {'municipality_code': '2281', 'municipality_concept_id': 'dJbx_FWY_tK6',
                                'municipality': 'Sundsvall', 'region_code': '22', 'region_concept_id': 'NvUF_SP1_1zo',
                                'region': 'Västernorrlands län', 'country_code': '199',
                                'country_concept_id': 'i46j_HmG_v64', 'country': 'Sverige', 'street_address': None,
                                'postcode': None, 'city': None, 'coordinates': [None, None]},
          'must_have': {'skills': [], 'languages': [], 'work_experiences': [], 'education': [], 'education_level': []},
          'nice_to_have': {'skills': [], 'languages': [], 'work_experiences': [
              {'concept_id': 'bXNH_MNX_dUR', 'label': 'Sjuksköterska, grundutbildad', 'weight': 5,
               'legacy_ams_taxonomy_id': '7296'}], 'education': [], 'education_level': []}, 'application_contact': [
            {'name': 'Testy Testsson', 'description': 'blabla', 'email': 'test@jobtechdev.se',
             'telephone': '+01011122233',
             'contactType': None}], 'publication_date': '2020-04-25T14:24:02',
          'last_publication_date': '2021-04-29T15:34:59', 'removed': False, 'removed_date': None,
          'source_type': 'VIA_ANNONSERA', 'timestamp': 1587817442503,
          'logo_url': 'https://www.arbetsformedlingen.se/rest/arbetsgivare/rest/af/v3/arbetsplatser/87189900/logotyper/logo.png',
          'keywords': {'extracted': {
              'occupation': ['grundutbildad', 'sjuksköterska', 'grundutbildade sjuksköterskor', 'hälso- och sjukvård'],
              'skill': [], 'location': ['västernorrlands län', 'sverige', 'sundsvall'],
              'employer': ['viva bemanning', 'sundsvall']},
              'enriched': {'occupation': ['sjuksköterska'], 'skill': ['svenska'],
                           'trait': ['tillmötesgående', 'självständig', 'engagerad', 'hjälpsam'],
                           'location': ['västernorrland', 'sverige', 'sundsvall'],
                           'compound': ['sjuksköterska', 'svenska', 'västernorrland', 'sverige', 'sundsvall']},
              'enriched_typeahead_terms': {'occupation': ['sjuksköterska'], 'skill': ['svenska'],
                                           'trait': ['tillmötesgående', 'självständig', 'engagerad', 'hjälpsam'],
                                           'location': ['västernorrlands län', 'västernorrland', 'sverige',
                                                        'sundsvall'],
                                           'compound': ['sjuksköterska', 'svenska', 'västernorrlands län',
                                                        'västernorrland', 'sverige', 'sundsvall']}}}

    result = bulkloader.format_removed_ad(ad)
    expected_id = '24025897'

    ad_id = result['id']
    assert isinstance(ad_id, str), f"id was of type: {type(ad_id)}"
    expected = {'id': expected_id, 'removed': False, 'removed_date': None, 'occupation': 'bXNH_MNX_dUR',
                'occupation_group': 'Z8ci_bBE_tmx', 'occupation_field': 'NYW6_mP6_vwf', 'municipality': 'dJbx_FWY_tK6',
                'region': 'NvUF_SP1_1zo', 'country': 'i46j_HmG_v64'}
    assert result == expected


@pytest.mark.unit
def test_regex_input_bulk_zip():
    print('============================', sys._getframe().f_code.co_name, '============================ ')

    bulk_regex = r'(\d{4}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])|all)$'
    input_regex = inputs.regex(bulk_regex)

    input_value = 'all'
    val = input_regex(input_value)

    assert val == input_value

    input_value = '2019-04-01'
    val = input_regex(input_value)

    assert val == input_value

    input_value = '2019-04-42'

    try:
        input_regex(input_value)
    except ValueError as ve:
        assert ve is not None
    else:
        pytest.fail("expected a ValueError, but no ValueError was raised")
