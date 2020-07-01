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
    ('#coro', ['coordinator']),
    ('#coron', ['fordon', 'core']),
    ('c#', ['c#']),
    ('c+', ['c++']),
    ('ang', ['angularjs', 'angered']),
    ('c', ['can', 'civilingenjör', 'c#', 'c', 'c körkort', 'c++', 'cloud', 'cnc- operatör', 'chaufför', 'cad',
           'continuous integration', 'cafeteria', 'ci/cd', 'citrix', 'civilingenjörsutbildning', 'css', 'c-kort',
           'certifikat', 'coachning', 'cykling', 'c-chaufför', 'cancer', 'cisco', 'civilingenjörsexamen', 'cafébiträde',
           'controller', 'cheerleadingtränare', 'chefskock', 'civilekonom', 'cm', 'co', 'coach', 'consultant manager',
           'coordinator', 'copywriter', 'customer success manager', 'cykelbud', 'cykelsäljare']),
    ('uppd', ['uppdragsutbildning', 'uppdukning', 'uppdragsledare']),
    ('underh',
     ['underhållsmekaniker', 'underhållsarbete', 'underhållstekniker', 'underhållssystem', 'underhållsrutiner',
      'underhållsingenjör', 'underhållspersonal']),
    ('sjuks', ['sjuksköterska', 'sjuksköterskeuppgifter', 'sjuksköterskeexamen', 'sjuksköterskelegitimation',
               'sjuksköterskeutbildning']),
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
    ('lärare ', ['will get too many hits, only number of hits is checked']),
    ('lärare i',
     ['i grundskolan', 'idrott', 'i fritidshem', 'ikt', 'it-kunskaper', 'its', 'i förskoleklass', 'idrott och hälsa',
      'informationsteknik', 'insatser', 'internationalisering', 'introduktionsprogram',
      'i praktiska och estetiska ämnen', 'idrottslärare', 'instrumentalpedagog']),
    ('lärare i ', ['will get too many hits, only number of hits is checked']),
    ('lärare fr', ['fritidspedagog', 'fritids', 'fritidshem', 'franska', 'friluftsaktiviteter', 'fritidsanläggningar',
                   'fritidspedagogutbildning']),
    ('lärare i fr', ['fritidshem', 'fritidspedagog', 'fritids', 'franska', 'friluftsaktiviteter', 'fritidsanläggningar',
                     'fritidspedagogutbildning']),
    ('lärare i fö', ['förskoleklass', 'företrädesrätt', 'förskola', 'förskollärarexamen', 'förskollärare']),
    ('gymnas',
     ['gymnasieutbildning', 'gymnasielärare', 'gymnasiekompetens', 'gymnasieexamen', 'gymnasium', 'gymnasieskola',
      'gymnastik', 'gymnasiesärskola', 'gymnasiebehörighet', 'gymnasieprogram', 'gymnasieskolekompetens']),
    ('gymnasie', ['gymnasieutbildning', 'gymnasielärare', 'gymnasiekompetens', 'gymnasieexamen', 'gymnasieskola',
                  'gymnasiesärskola', 'gymnasiebehörighet', 'gymnasieprogram', 'gymnasieskolekompetens']),
    ('bygg', ['byggbranschen', 'byggproduktion', 'byggnadsingenjör', 'byggprojekt', 'byggteknik', 'byggnadsarbetare',
              'byggprojektledare', 'bygghandlingar', 'bygglov', 'bygglovshandläggning', 'byggmaterial',
              'byggnadsställningar', 'byggnadsverksamhet', 'byggnationer', 'byggplatsuppföljning', 'byggprocesser',
              'byggtjänster', 'byggförare', 'byggingenjör', 'byggledare', 'byggmästare', 'byggnadskonstruktör',
              'byggnadsplåtslagare']),
    ('bygg ', ['will get too many hits, only number of hits is checked']),
    ('kock', ['kock', 'kockutbildning', 'kockutbildare']),
    ('kock ',
     ['sverige', 'stockholms län', 'mat', 'stockholm', 'kök', 'matlagning', 'svenska', 'à la carte', 'tillagning',
      'specialkock', 'engelska', 'specialkost', 'storkök', 'städning', 'västra götaland', 'beställningar',
      'egenkontroll', 'servering', 'barn', 'datorvana', 'dietmatlagning', 'diskning', 'dokumentation', 'frukost',
      'haccp', 'hotell', 'bandhagen', 'dalarna', 'göteborg', 'jönköping', 'jönköpings län', 'skåne', 'kallskänka',
      'blekinge', 'borlänge', 'falköping', 'gotland', 'heby', 'hällefors', 'idre', 'järfälla', 'karlshamn',
      'karlskrona', 'chefskock', 'kokerska', 'köksbiträde', 'matlagare', 'pizzabagare']),
    ('stockholm  ',
     ['will get too many hits, only number of hits is checked']),
    ('malmö ',
     ['malmö butikssäljare', 'malmö sjuksköterska', 'malmö lagerarbetare', 'malmö redovisningsekonom',
      'malmö användbarhetsdesigner', 'malmö arbetschef']),
    ('upplands ',
     ['upplands väsby', 'upplands väsby bemanningssjuksköterska', 'upplands väsby handledare',
      'upplands väsby javautvecklare', 'upplands väsby mjukvaruutvecklare', 'upplands väsby personlig assistent',
      'upplands väsby servicetekniker']),
    ('upplands väsby ',
     ['väsby', 'väsby bemanningssjuksköterska', 'väsby sjuksköterska']),
    ('sverige ',
     ['sverige sjuksköterska', 'sverige lärare', 'sverige personlig assistent', 'sverige lärare i grundskolan',
      'sverige försäljare', 'sverige butikssäljare']),
    ('sverige',
     ['sverige', 'sverige sjuksköterska', 'sverige lärare', 'sverige personlig assistent',
      'sverige lärare i grundskolan', 'sverige försäljare', 'sverige butikssäljare']),
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
    ("stor", "", ['storkök', 'storstädning', 'storage', 'stored procedures', 'storhushåll', 'storuman']),
    ("stor", "s",
     ['sverige', 'svenska', 'stockholms län', 'stockholm', 'skåne', 'sjuksköterska', 'sjukvård', 'språkkunskaper',
      'städning', 'södermanland']),
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
