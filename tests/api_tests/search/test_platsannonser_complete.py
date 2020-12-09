import json
import pytest
import requests

from tests.test_resources.helper import get_complete, compare, compare_suggestions, compare_typeahead, \
    compare_synonyms


@pytest.mark.parametrize("query, synonyms, expect_syn", [('servit', ['servitris', 'servitör'], True),
                                                         ('servit',
                                                          ['servitris', 'servitör', 'servitriser', 'servitörer'], True),
                                                         ('systemutvecklare angu', ['systemutvecklare angular',
                                                                                    'systemutvecklare angularjs'],
                                                          True),
                                                         ('angu', ['angular', 'angularjs'], True),
                                                         ('ang', ['angularjs', 'angular', 'angular.js', 'angered'],
                                                          True),
                                                         ('c#', ['c#'], True),
                                                         ('pyth', ['python'], True),
                                                         # check that synonyms are not suggested
                                                         ('c#', ['c++'], False),
                                                         ('c#', ['java'], False)])
def test_complete_endpoint_synonyms_typeahead(session, search_url, query, synonyms, expect_syn):
    """
    Test that incomplete search queries will return synonyms
    first arg is the query
    second arg is a list of expected synonyms, which all must be found in the response
    third arg True/False determines if synonyms are supposed to be found or not
    """
    json_response = get_complete(session, search_url, params={'q': query})
    json_typeahead = json_response['typeahead']
    actual_complete_values = [item['value'] for item in json_typeahead]
    assert len(actual_complete_values) > 0, f"no synonyms found for '{query}'"
    print(actual_complete_values)
    compare_synonyms(synonyms, actual_complete_values, expect_syn)


@pytest.mark.integration
@pytest.mark.parametrize("query, expected_suggestions", [
    ('systemutvecklare angular', ['systemutvecklare angular', 'systemutvecklare angularjs']),
    ('angu', ['angular', 'angularjs', 'angular.js']),
    ('pyth', ['python', 'python stockholm', 'python stockholms län', 'python göteborg', 'python västra götaland',
              'python västra götalands län']),
    ('#coro', ['creo', 'foto', 'core', 'code', 'cura']),
    ('#coron', ['fordon', 'core']),
    ('c#', ['c#']),
    ('c+', ['c++']),
    ('ang', ['angular', 'angularjs', 'angular.js', 'angered']),
    ('c',
     ['can', 'civilingenjör', 'c#', 'c-körkort', 'c++', 'cnc- operatör', 'cnc-operatör', 'cloud',
      'continuous integration', 'chaufför', 'cad', 'cafeteria', 'ci/cd', 'citrix', 'civilingenjörsutbildning', 'css',
      'c-kort', 'café', 'certifieringar', 'certifikat', 'coachning', 'cyklar', 'cykling', 'c-chaufför', 'c körkort',
      'cafébiträde', 'chaufförer', 'cnc-operatörer', 'controller', 'c-chaufförer', 'ce-chaufför', 'cheerleadingtränare',
      'chefskock', 'civilekonom', 'cnc-svarvare', 'co', 'copywriter', 'customer success manager', 'cykelbud',
      'cykelsäljare']),
    ('uppd', ['uppdragsutbildning', 'uppdukning', 'uppdragsledare']),
    ('underh',
     ['underhållsmekaniker', 'underhållsarbete', 'underhållstekniker', 'underhållssystem', 'underhållsarbeten',
      'underhållsrutiner', 'underhållsarbetare', 'underhållsingenjör', 'underhållspersonal']),
    ('sjuks',
     ['sjuksköterska', 'sjuksköterskor', 'sjuksköterskeuppgifter', 'sjuksköterskearbete', 'sjuksköterskeexamen',
      'sjuksköterskelegitimation', 'sjuksköterskeutbildning', 'sjuksköterskan']),
    ('arbetsl', ['arbetslivserfarenhet', 'arbetsledning', 'arbetsledare', 'arbetsliv', 'arbetslivserfarenheter',
                 'arbetslivspsykologi', 'arbetsledarutbildning', 'arbetslivsfrågor']),
    ('servitr', ['servitris', 'servitriser']),

])
def test_complete_endpoint_with_spellcheck_typeahead(session, search_url, query, expected_suggestions):
    """
    test of /complete endpoint
    parameters: query and list of expected result(s)
    """
    json_response = get_complete(session, search_url, params={'q': query, 'limit': 50})
    assert 'typeahead' in json_response
    actual_suggestions = [suggest.get('value') for suggest in json_response.get('typeahead')]

    compare(len(actual_suggestions), len(expected_suggestions), f"\nQuery: {query} ")
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
     ['stor sverige', 'stor svenska', 'stor stockholms län', 'stor stockholm', 'stor skåne', 'stor skåne län',
      'stor sjuksköterska', 'stor sjukvård', 'stor sjuksköterskor', 'stor språkkunskaper']),
    ("storage", "", ['storage', 'storage solna', 'storage stockholms län']),
    ("storage", "s",
     ['storage servrar', 'storage säkerhet', 'storage solna', 'storage stockholms län', 'storage sverige']),
])
def test_complete_multiple_words(session, search_url, query, query_2, expected_typeahead):
    """
    Test typeahead with two words
    """
    if query_2 == "":
        full_query = query
    else:
        full_query = query + ' ' + query_2
    response_json = get_complete(session, search_url, {'q': full_query})
    typeahead = response_json['typeahead']
    compare(len(typeahead), len(expected_typeahead))
    compare_typeahead(typeahead, expected_typeahead)


@pytest.mark.parametrize("contextual", [True, False])
def test_complete_for_locations_with_space_and_contextual_param(session, search_url, contextual):
    """
    Test typeahead for location with trailing space after city name,
    and using parameter 'contextual' True or False
    """

    query = 'Malmö '
    expected = ['malmö butikssäljare', 'malmö sjuksköterska', 'malmö civilingenjör', 'malmö högskoleingenjör',
                'malmö lagerarbetare', 'malmö redovisningsekonom']
    response_json = get_complete(session, search_url, {'q': query, 'limit': 10, 'contextual': contextual})
    typeahead = response_json['typeahead']
    suggestions = []
    for t in typeahead:
        suggestions.append(t['value'])
    assert suggestions == expected
