import pytest
import bulkloader.repository as bulkloader

ad = {'id': 24025897, 'external_id': None, 'headline': 'Sjuksköterska sökes till bemanningsuppdrag med hög ersättning!',
      'application_deadline': '2020-05-03T23:59:59', 'number_of_vacancies': 1, 'description': {
        'text': 'Är du sjuksköterska och söker efter nya uppdrag? Eller kanske helt ny inom bemanning och vill veta mer?\nOavsett vad kan vi förhoppningsvis hjälpa dig att finna det du söker. Vi svarar på frågor och planerar ett upplägg tillsammans utefter dina önskemål för att du ska ha möjlighet att arbeta på dina villkor. \nVi är med från uppläggets start och ser fram emot att följa din resa, vi upplever nya platser tillsammans! Vi har i dagsläget uppdrag runtom i stort sett över hela Sverige, i alla dess former och med attraktiva ersättningar.\nFör oss är en viktig del att du ska känna dig trygg under hela din arbetsperiod varför du utöver din lön erhåller bland annat följande förmåner:\n·        Tjänstepension\n·        Övriga försäkringar\n·        Personlig kontaktperson som är tillgänglig & engagerad\n·        Ekonomisk ersättning för boende & resor\n·        Utbildningar\n\n\nKvalifikationer:\nVi söker dig som är legitimerad sjuksköterska med yrkeserfarenhet och referenser som kan intyga din kompetens. Du har goda kunskaper i det svenska språket, både i tal och skrift.\n\n\nPersonliga egenskaper:\nDu är självständig både ensam och i grupp. Du ska kunna samarbeta med sjuksköterskor och läkare samt vara intresserad och göra ditt yttersta för patienterna. Du är säker i din yrkesroll, hjälpsam, engagerad och tillmötesgående.\n\n\nOmfattning:\nDeltid/Heltid, Rotation: dag, kväll och natt. Även helg kan förekomma.\n\n\nAnsökan\nVälkommen med din ansökan via mail alternativ intresseanmälan på vår hemsida www.vivabemanning.se\nTelefon:  TELEPHONENO \nMail:  EMAIL  \nKänner du möjligtvis även en sjuksköterska som kan vara lämplig? Vi tar mer än gärna emot förslag.\n\n\n#jobbjustnu',
        'text_formatted': '<p>Är du sjuksköterska och söker efter nya uppdrag? Eller kanske helt ny inom bemanning och vill veta mer?</p><p>Oavsett vad kan vi förhoppningsvis hjälpa dig att finna det du söker. Vi svarar på frågor och planerar ett upplägg tillsammans utefter dina önskemål för att du ska ha möjlighet att arbeta på dina villkor. </p><p>Vi är med från uppläggets start och ser fram emot att följa din resa, vi upplever nya platser tillsammans! Vi har i dagsläget uppdrag runtom i stort sett över hela Sverige, i alla dess former och med attraktiva ersättningar.</p><p>För oss är en viktig del att du ska känna dig trygg under hela din arbetsperiod varför du utöver din lön erhåller bland annat följande förmåner:</p><p>·        Tjänstepension</p><p>·        Övriga försäkringar</p><p>·        Personlig kontaktperson som är tillgänglig &amp; engagerad</p><p>·        Ekonomisk ersättning för boende &amp; resor</p><p>·        Utbildningar</p><p><br></p><p><strong>Kvalifikationer:</strong></p><p>Vi söker dig som är legitimerad sjuksköterska med yrkeserfarenhet och referenser som kan intyga din kompetens. Du har goda kunskaper i det svenska språket, både i tal och skrift.</p><p><br></p><p><strong>Personliga egenskaper:</strong></p><p>Du är självständig både ensam och i grupp. Du ska kunna samarbeta med sjuksköterskor och läkare samt vara intresserad och göra ditt yttersta för patienterna. Du är säker i din yrkesroll, hjälpsam, engagerad och tillmötesgående.</p><p><br></p><p><strong>Omfattning:</strong></p><p>Deltid/Heltid, Rotation: dag, kväll och natt. Även helg kan förekomma.</p><p><br></p><p><strong>Ansökan</strong></p><p>Välkommen med din ansökan via mail alternativ intresseanmälan på vår hemsida www.vivabemanning.se</p><p>Telefon:  TELEPHONENO </p><p>Mail:  EMAIL  </p><p>Känner du möjligtvis även en sjuksköterska som kan vara lämplig? Vi tar mer än gärna emot förslag.</p><p><br></p><p>#jobbjustnu</p>',
        'company_information': None, 'needs': None, 'requirements': None, 'conditions': None},
      'employment_type': {'concept_id': '1paU_aCR_nGn', 'label': 'Behovsanställning', 'legacy_ams_taxonomy_id': '4'},
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
      'occupation_field': {'concept_id': 'NYW6_mP6_vwf', 'label': 'Hälso- och sjukvård', 'legacy_ams_taxonomy_id': '8'},
      'workplace_address': {'municipality_code': '2281', 'municipality_concept_id': 'dJbx_FWY_tK6',
                            'municipality': 'Sundsvall', 'region_code': '22', 'region_concept_id': 'NvUF_SP1_1zo',
                            'region': 'Västernorrlands län', 'country_code': '199',
                            'country_concept_id': 'i46j_HmG_v64', 'country': 'Sverige', 'street_address': None,
                            'postcode': None, 'city': None, 'coordinates': [None, None]},
      'must_have': {'skills': [], 'languages': [], 'work_experiences': [], 'education': [], 'education_level': []},
      'nice_to_have': {'skills': [], 'languages': [], 'work_experiences': [
          {'concept_id': 'bXNH_MNX_dUR', 'label': 'Sjuksköterska, grundutbildad', 'weight': 5,
           'legacy_ams_taxonomy_id': '7296'}], 'education': [], 'education_level': []}, 'application_contact': [
        {'name': 'Testy Testsson', 'description': 'blabla', 'email': 'test@jobtechdev.se', 'telephone': '+01011122233',
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


def test_format_removed_ad():
    result = bulkloader.format_removed_ad(ad)
    expected_id = '24025897'

    ad_id = result['id']
    assert isinstance(ad_id, str), f"id was of type: {type(ad_id)}"
    expected = {'id': expected_id, 'removed': False, 'removed_date': None, 'occupation': 'bXNH_MNX_dUR',
                'occupation_group': 'Z8ci_bBE_tmx', 'occupation_field': 'NYW6_mP6_vwf', 'municipality': 'dJbx_FWY_tK6',
                'region': 'NvUF_SP1_1zo', 'country': 'i46j_HmG_v64'}
    assert result == expected
