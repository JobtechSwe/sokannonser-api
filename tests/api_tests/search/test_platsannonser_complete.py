import json
import pytest
import requests

from tests.test_resources.helper import get_complete, get_complete_expect_error, compare, compare_suggestions, \
    compare_typeahead, compare_synonyms


@pytest.mark.parametrize("query, synonyms, expect_syn", [('servit', ['servitris', 'servitör'], True),
                                                         ('servit',
                                                          ['servitris', 'servitör', 'servitriser'], True),
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
def test_complete_endpoint_synonyms_typeahead(session, query, synonyms, expect_syn):
    """
    Test that incomplete search queries will return synonyms
    first arg is the query
    second arg is a list of expected synonyms, which all must be found in the response
    third arg True/False determines if synonyms are supposed to be found or not
    """
    json_response = get_complete(session, params={'q': query})
    json_typeahead = json_response['typeahead']
    actual_complete_values = [item['value'] for item in json_typeahead]
    assert len(actual_complete_values) > 0, f"no synonyms found for '{query}'"
    print(actual_complete_values)
    compare_synonyms(synonyms, actual_complete_values, expect_syn)


@pytest.mark.integration
@pytest.mark.parametrize("query, expected_suggestions", [
    ('systemutvecklare angular',
     ['systemutvecklare angularjs', 'systemutvecklare angular', 'systemutvecklare angular js']),
    ('angu', ['angularjs', 'angular', 'angular js', 'angular.js']),
    ('pyth', ['python', 'python scripting']),
    ('#coro', ['coordinator', 'core network', 'colorist', 'dorotea']),
    ('#coron', []),
    ('c#', ['c#', 'c#.net']),
    ('c+', ['c++']),
    ('ang', ['angularjs', 'angular', 'angular js', 'angular.js', 'angered']),
    ('c',
     ['can', 'civilingenjör', 'cloud', 'c#', 'c++', 'cnc- operatör', 'cnc-operatör', 'certifieringar', 'ci/cd',
      'civilingenjörsexamen', 'client', 'certifikat', 'coachning', 'continuous integration', 'crm-system', 'css',
      'c-körkort', 'cms', 'cnc', 'crm', 'cad', 'chief information officer', 'cio', 'coordinator', 'c-kort',
      'cad-system', 'chaufför', 'controller', 'cfo', 'cirkelledare', 'cnc-operatörer', 'case manager',
      'category manager', 'ce-chaufför', 'ce-chaufförer', 'change manager', 'chaufförer', 'chefsbarnmorska', 'co',
      'colorist']),
    ('uppd', ['uppdragsutbildning', 'uppdragsforskning', 'uppdragsledning', 'uppdragsutbildningar', 'uppdragsledare']),
    ('underh',
     ['underhållsprojekt', 'underhållsarbete', 'underhållsmekaniker', 'underhållstekniker', 'underhållssystem',
      'underhållsarbeten', 'underhållsingenjör', 'underhåll och reparation', 'underhållsavdelning', 'underhållsfrågor',
      'underhållsplanering', 'underhållsteknik', 'underhållschef', 'underhållspersonal']),
    ('sjuks',
     ['sjuksköterska', 'sjuksköterskor', 'sjuksköterskeexamen', 'sjuksköterskelegitimation', 'sjuksköterskeuppgifter']),
    ('arbetsl', ['arbetslivserfarenhet', 'arbetsledning', 'arbetsledare', 'arbetsliv', 'arbetslivsfrågor',
                 'arbetsledarerfarenhet']),
    ('servitr', ['servitris', 'servitriser']),

])
def test_complete_endpoint_with_spellcheck_typeahead(session, query, expected_suggestions):
    """
    test of /complete endpoint
    parameters: query and list of expected result(s)
    """
    json_response = get_complete(session, params={'q': query, 'limit': 50})
    assert 'typeahead' in json_response
    actual_suggestions = [suggest.get('value') for suggest in json_response.get('typeahead')]
    compare(len(actual_suggestions), len(expected_suggestions), f"\nQuery: {query} ")
    compare_suggestions(actual_suggestions, expected_suggestions, query)


def test_check_400_bad_request_when_limit_is_greater_than_allowed(session):
    """
    Test that a limit of 51 will give a '400 BAD REQUEST' response with a meaningful error message
    """
    response = get_complete_expect_error(session, {'q': 'x', 'limit': 51},
                                         expected_http_code=requests.codes.bad_request)
    response_json = json.loads(response.content.decode('utf8'))
    assert response_json['errors']['limit'] == 'Invalid argument: 51. argument must be within the range 0 - 50'
    assert response_json['message'] == 'Input payload validation failed'


@pytest.mark.parametrize("query, query_2, expected_typeahead", [
    ("stor", "",
     ['storage', 'storkök', 'storhushållsutbildning', 'storköksutbildning', 'storstädning', 'storyboards', 'storvik']),
    ("stor", "s",
     ['stor sverige', 'stor svenska', 'stor stockholms län', 'stor stockholm', 'stor skåne', 'stor skåne län',
      'stor sjuksköterska', 'stor sjukvård', 'stor svenskt medborgarskap', 'stor samverkan']),
    ("storage", "",
     ['storage', 'storage göteborg', 'storage västra götaland', 'storage västra götalands län', 'storage stockholm',
      'storage stockholms län']),
    ("storage", "s",
     ['storage sverige', 'storage sensors', 'storage stockholm', 'storage stockholms län',
      'storage systemadministratör']),
])
def test_complete_multiple_words(session, query, query_2, expected_typeahead):
    """
    Test typeahead with two words
    """
    if query_2 == "":
        full_query = query
    else:
        full_query = query + ' ' + query_2
    response_json = get_complete(session, {'q': full_query})
    typeahead = response_json['typeahead']
    compare(len(typeahead), len(expected_typeahead))
    compare_typeahead(typeahead, expected_typeahead)


@pytest.mark.parametrize("contextual", [True, False])
def test_complete_for_locations_with_space_and_contextual_param(session, contextual):
    """
    Test typeahead for location with trailing space after city name,
    and using parameter 'contextual' True or False
    """

    query = 'Malmö '
    expected = ['malmö programmerare', 'malmö systemutvecklare', 'malmö försäljare', 'malmö kundtjänstmedarbetare',
                'malmö lagerarbetare', 'malmö personlig assistent']

    response_json = get_complete(session, {'q': query, 'limit': 10, 'contextual': contextual})
    typeahead = response_json['typeahead']
    suggestions = []
    for t in typeahead:
        suggestions.append(t['value'])
    assert suggestions == expected


@pytest.mark.parametrize("query, expected", [
    ("göteborg sjuksköterska", ['göteborg sjuksköterska']),
    ("götteborg sjuksköterska", ['göteborg sjuksköterska']),
    ("götteborg sjukssköterska", ['göteborg sjuksköterska', 'götteborg sjuksköterska', 'göteborg sjukssköterska']),
    ("göteborg sjukssköterska", ['göteborg sjuksköterska']),
    ("göteborg sjukssköterska läckare", ['göteborg sjuksköterska läkare', 'göteborg sjuksköterska lärare']),
    ("göteborg sjukssköterska läkkare", ['göteborg sjuksköterska läkare', 'göteborg sjuksköterska lärare']),
    ("göteborg sjukssköterska lääkare", ['göteborg sjuksköterska läkare', 'göteborg sjuksköterska lärare']),
    ("göteborg sjukssköterska läkare", ['göteborg sjuksköterska läkare']),
    ("läckare", ['läkare']),
    ("götteborg", ['göteborg']),
    ("stokholm", ['stockholms län', 'stockholm']),
    ("stokholm ", ['stockholms län', 'stockholm']),  # trailing space
    ("stockhlm", ['stockholms län', 'stockholm']),
    ("stockhlm ", ['stockholms län', 'stockholm']),  # trailing space
    ("stokholm lärarre", ['stockholms lärare', 'stockholm lärare', 'stockholm läkare']),
    ("göteborg sjukssköterska läckare", ['göteborg sjuksköterska lärare', 'göteborg sjuksköterska läkare']),
    ("göteborg läckare sjukssköterska ", ['göteborg lärare sjuksköterska', 'göteborg läkare sjuksköterska']),
    ("göteborg läckare sjukssköterska", ['göteborg lärare sjuksköterska', 'göteborg läkare sjuksköterska']),
    ("läckare götteborg", ['läkare göteborg']),
    ("läckare göteborg", ['läkare göteborg']),
    ("stockholm läckare göteborg", ['stockholm lärare göteborg', 'stockholm läkare göteborg']),
    ("stockhlm läckare göteborg", ['stockholm lärare göteborg', 'stockholm läkare göteborg']),
    ("stockhlm läckare göteborg ", ['stockholm lärare göteborg', 'stockholm läkare göteborg']),  # trailing space
])
def test_complete_spelling_correction_multiple_words(session, query, expected):
    """
    Test typeahead with multiple (misspelled) words
    """
    typeahead = get_complete(session, {'q': query})['typeahead']
    values = []
    for item in typeahead:
        values.append(item['value'])
    # check that expected typeahead is in one of the actual suggestions
    for exp in expected:
        assert any(v == exp for v in values), f"Error: expected: '{exp}' not found in '{values}'. Query: {query}"
