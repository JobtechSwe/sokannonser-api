import json
import pytest
import requests

import tests.test_resources.settings
from sokannonser import settings
from tests.test_resources.settings import test_api_key_search
from tests.test_resources.helper import get_complete_with_headers, compare, compare_suggestions, compare_typeahead, \
    compare_synonyms, check_len_more_than


@pytest.mark.parametrize("query, synonyms, expect_success", [('servit', ['servitris', 'servitör'], True),
                                                             ('servit',
                                                              ['servitris', 'servitör', 'servitriser', 'servitörer'],
                                                              True),
                                                             ('systemutvecklare angu', ['angular', 'angularjs'], True),
                                                             ('angu', ['angular', 'angularjs'], True),
                                                             ('ang', ['angularjs', 'angular', 'angular.js', 'angered'],
                                                              True),
                                                             ('c#', ['c#'], True),
                                                             ('pyth', ['python'], True),
                                                             # check that synonyms are not suggested
                                                             ('c#', ['c++'], False),
                                                             ('c#', ['java'], False)])
def test_complete_endpoint_synonyms_typeahead(session, search_url, query, synonyms, expect_success):
    """
    Test that incomplete search queries will return synonyms
    when 'x-feature-include-synonyms-typeahead' is set in headers
    first arg is the query
    second arg is a list of expected synonyms, which all must be found in the response
    third arg True/False determines if synonyms are supposed to be found or not
    """
    headers = {'api-key': test_api_key_search, 'accept': 'application/json',
               settings.X_FEATURE_INCLUDE_SYNONYMS_TYPEAHEAD: 'true'}
    response = get_complete_with_headers(session, search_url, params={'q': query}, headers=headers)
    json_response = json.loads(response.content.decode('utf8'))

    assert 'typeahead' in json_response
    json_typeahead = json_response['typeahead']
    complete_values = [item['value'] for item in json_typeahead]
    assert len(complete_values) > 0, f"no synonyms found for '{query}'"
    compare_synonyms(synonyms, complete_values, expect_success)


@pytest.mark.integration
@pytest.mark.parametrize("query, expected_suggestions", [
    ('systemutvecklare angu', ['systemutvecklare angularjs']),
    ('angu', ['angularjs']),
    ('pyth', ['python']),
    ('#coro', ['corona']),
    ('#coron', ['corona']),
    ('c#', ['c#']),
    ('c+', ['c++']),
    ('ang', ['angularjs', 'angered']),
    ('c', ['civilingenjör', 'c#', 'c', 'can', 'c körkort', 'cnc- operatör', 'c++', 'cad', 'cloud', 'css', 'chaufför',
           'certifikat', 'ci/cd', 'citrix', 'civilingenjörsutbildning', 'continuous integration', 'cnc', 'coachning',
           'cykling', 'c-chaufför', 'c-kort', 'cellbiologi', 'cisco', 'confluence', 'controller', 'copy', 'ce-chaufför',
           'cheerleadingtränare', 'chefskock', 'civilekonom', 'cnc-svarvare', 'coach', 'consultant manager',
           'copywriter', 'customer success manager', 'cykelbud', 'cykelsäljare']),
    ('uppd', ['uppdragsutbildning', 'uppdukning', 'uppdragsledare']),
    ('underh',
     ['underhållsmekaniker', 'underhållsarbete', 'underhållstekniker', 'underhållssystem', 'underhållsrutiner',
      'underhållsarbetare', 'underhållsingenjör']),
    ('sjuks', ['sjuksköterska', 'sjuksköterskeuppgifter', 'sjuksköterskeutbildning', 'sjuksköterskelegitimation']),
    ('arbetsl', ['arbetslivserfarenhet', 'arbetsledning', 'arbetsledare', 'arbetsliv', 'arbetslivspsykologi',
                 'arbetsledarutbildning', 'arbetslivsfrågor']),
    ('servitr', ['server', 'service', 'servrar']),

    # Failing
    # ('servit', ['servicetekniker', 'servicearbete', 'service och underhåll', 'servicedesk', 'servicehandläggare',
    #               'servicemedarbetare', 'servicetjänster', 'serviceyrke', 'service manager', 'servicebiträde',
    #              'serviceelektriker', 'serviceinsatser', 'servicerådgivare']),
    # ('servitr', ['servitris', 'servitör', 'servitriser', 'servitörer']),

    # ('servi', ['servicetekniker', 'servicearbete', 'service och underhåll', 'servicedesk', 'servicehandläggare',
    #           'servicemedarbetare', 'serviceyrke', 'service manager', 'servicebiträde', 'serviceelektriker']),
    # ('angu', ['angular', 'angularjs']),  # actual ['angularjs']
    # ('ang', ['angular', 'angularjs', 'angered'])  # actual ['angularjs', 'angered']
])
def test_complete_endpoint_with_spellcheck_typeahead(session, search_url, query, expected_suggestions):
    """
    test of /complete endpoint with 'x-feature-spellcheck-typeahead' header
    parameters: query and list of expected result(s)
    """
    headers = {'api-key': test_api_key_search, 'accept': 'application/json',
               settings.X_FEATURE_SPELLCHECK_TYPEAHEAD: 'true'}
    response = get_complete_with_headers(session, search_url, params={'q': query, 'limit': 50}, headers=headers)
    json_response = json.loads(response.content.decode('utf8'))
    assert 'typeahead' in json_response
    actual_suggestions = [suggest.get('value') for suggest in json_response.get('typeahead')]
    compare(len(actual_suggestions), len(expected_suggestions), f"\nQuery: {query} ")
    compare_suggestions(actual_suggestions, expected_suggestions, query)


@pytest.mark.parametrize("query, expected_suggestions", [
    ('lärare', ['lärare', 'lärare i grundskolan', 'lärare i förskola', 'lärare i fritidshem', 'lärarexamen',
                'lärare i förskoleklass', 'lärare i praktiska och estetiska ämnen']),
    ('lärare ',
     ['sverige', 'i grundskolan', 'undervisning', 'lärarlegitimation', 'svenska', 'skola', 'stockholms län', 'verktyg',
      'västra götaland', 'gymnasielärare']),
    ('lärare i', ['i grundskolan', 'idrott', 'i fritidshem', 'idrott och hälsa', 'it-kunskaper', 'i förskoleklass',
                  'informationsteknik', 'insatser', 'integration', 'intellektuell funktionsnedsättning',
                  'introduktionsprogram', 'i praktiska och estetiska ämnen', 'industrilärare', 'instrumentalpedagog']),
    ('lärare i ',
     ['sverige', 'grundskolan', 'undervisning', 'lärarlegitimation', 'svenska', 'skola', 'stockholms län', 'verktyg',
      'västra götaland', 'gymnasielärare']),
    ('lärare fr', ['fritidshem', 'fritidspedagog', 'franska', 'friluftsaktiviteter', 'fritidspedagogutbildning']),
    ('lärare i fr', ['fritidshem', 'fritidspedagog', 'franska', 'friluftsaktiviteter', 'fritidspedagogutbildning']),
    ('lärare i fö', ['förskola', 'förskoleklass', 'förskollärarexamen', 'förskollärare']),
    ('gymnas', ['gymnasieutbildning', 'gymnasielärare', 'gymnasiekompetens', 'gymnasium', 'gymnasieexamen', 'gymnastik',
                'gymnasieprogram', 'gymnasieskola', 'gymnasieskolekompetens']),
    ('gymnasie',
     ['gymnasieutbildning', 'gymnasielärare', 'gymnasiekompetens', 'gymnasieexamen', 'gymnasieprogram', 'gymnasieskola',
      'gymnasieskolekompetens']),
    ('bygg', ['byggbranschen', 'byggteknik', 'byggproduktion', 'byggnadsingenjör', 'byggprojektledare', 'byggprojekt',
              'byggarbetsplats', 'bygghandlingar', 'byggledning', 'bygglov', 'bygglovshandläggning', 'byggmaterial',
              'byggnadsställningar', 'byggnadsverksamhet', 'byggnationer', 'byggplatsuppföljning', 'byggprocesser',
              'byggtjänster', 'byggförare', 'byggingenjör', 'byggledare', 'byggmästare', 'byggnadsarbetare',
              'byggnadskonstruktör', 'byggnadsplåtslagare']),
    ('bygg ', ['will get too many hits, only number of hits is checked']),
    ('kock', ['kock', 'kockerfarenheter', 'kockutbildning', 'kockutbildare']),
    ('kock ', ['will get too many hits, only number of hits is checked']),
    ('stockholm  ',
     ['will get too many hits, only number of hits is checked']),
    ('malmö ',
     ['malmö butikssäljare', 'malmö sjuksköterska', 'malmö civilingenjör', 'malmö högskoleingenjör',
      'malmö lagerarbetare', 'malmö redovisningsekonom']),
    ('upplands ',
     ['upplands väsby', 'upplands väsby bemanningssjuksköterska', 'upplands väsby handledare',
      'upplands väsby javautvecklare', 'upplands väsby mjukvaruutvecklare', 'upplands väsby personlig assistent',
      'upplands väsby servicetekniker']),
    ('upplands väsby ',
     ['väsby', 'väsby bemanningssjuksköterska', 'väsby sjuksköterska']),
    ('sverige ',
     ['sverige sjuksköterska', 'sverige lärare', 'sverige personlig assistent', 'sverige lärare i grundskolan',
      'sverige säljare', 'sverige butikssäljare']),
    ('sverige',
     ['sverige', 'sverige sjuksköterska', 'sverige lärare', 'sverige personlig assistent',
      'sverige lärare i grundskolan', 'sverige säljare', 'sverige butikssäljare']),
])
def test_suggest_extra_word_and_allow_empty(session, search_url, query, expected_suggestions):
    """
    Test suggestions for extra words
    test difference between 'query' and 'query ' (with trailing space)

    X_FEATURE_SUGGEST_EXTRA_WORD
    X_FEATURE_ALLOW_EMPTY_TYPEAHEAD
    """
    headers = {'api-key': test_api_key_search, 'accept': 'application/json',
               settings.X_FEATURE_SUGGEST_EXTRA_WORD: 'true', settings.X_FEATURE_ALLOW_EMPTY_TYPEAHEAD: 'true'}

    response = get_complete_with_headers(session, search_url, params={'q': query, 'limit': 50}, headers=headers)
    json_response = json.loads(response.content.decode('utf8'))
    assert 'typeahead' in json_response
    actual_suggestions = [suggest.get('value') for suggest in json_response.get('typeahead')]
    # compare(len(actual_suggestions), len(expected_suggestions))
    if len(actual_suggestions) < 50:
        compare_suggestions(actual_suggestions, expected_suggestions, query)


def test_check_400_bad_request_when_limit_is_greater_than_allowed(session, search_url):
    """
    Test that a limit of 51 will give a '400 BAD REQUEST' response with a meaningful error message
    """
    url = f"{search_url}/complete"
    response = session.get(url, params={'q': 'x', 'limit': 51})

    assert response.status_code == requests.codes.bad_request
    response_json = json.loads(response.content.decode('utf8'))
    assert response_json['errors']['limit'] == 'Invalid argument: 51. argument must be within the range 0 - 50'
    assert response_json['message'] == 'Input payload validation failed'


@pytest.mark.parametrize("query, query_2, expected_typeahead", [
    ("stor", "", ['storkök', 'storhushåll', 'storstädning', 'storage', 'stored procedures', 'storuman']),
    ("stor", "s",
     ['sverige', 'svenska', 'stockholms län', 'stockholm', 'skåne', 'sjuksköterska', 'sjukvård', 'språkkunskaper',
      'städning', 'skola']),
    ("storage", "", ['storage', 'storage solna', 'storage stockholms län']),
    ("storage", "s", ['servrar', 'säkerhet', 'solna', 'stockholms län', 'sverige']),

])
def test_complete_from_readme(session, search_url, query, query_2, expected_typeahead):
    headers = {'api-key': tests.test_resources.settings.test_api_key_search, 'accept': 'application/json',
               settings.X_FEATURE_SUGGEST_EXTRA_WORD: 'true', settings.X_FEATURE_ALLOW_EMPTY_TYPEAHEAD: 'true'}
    if query_2 == "":
        full_query = query
    else:
        full_query = query + ' ' + query_2
    response = get_complete_with_headers(session, search_url, {'q': full_query}, headers)
    response_json = json.loads(response.content.decode('utf8'))
    typeahead = response_json['typeahead']
    compare(len(typeahead), len(expected_typeahead))
    compare_typeahead(typeahead, expected_typeahead)
