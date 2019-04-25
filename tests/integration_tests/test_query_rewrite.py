import sys
import os
import pytest
from sokannonser import settings
from pprint import pprint

from sokannonser.repository.text_to_concept import TextToConcept

host = settings.ES_HOST
index = 'narvalontology'
user = settings.ES_USER
pwd = settings.ES_PWD
port = settings.ES_PORT

# protocol = 'http' if host == 'localhost' else 'https'
# url = protocol + '://' + host + ':' + str(port)

# print('Running unittests calling %s' % url)

text_to_concept = TextToConcept(ontologyhost=host,
                                ontologyport=port,
                                ontologyindex='narvalontology',
                                ontologyuser=user,
                                ontologypwd=pwd)


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_unigram_competence():
    print('\n============================', sys._getframe().f_code.co_name, '============================')
    concepts = text_to_concept.text_to_concepts('noggrann systemutvecklare java')
    assert concepts is not None
    assert_not_empty(concepts, 'occupation')
    assert_not_empty(concepts, 'skill')
    assert_not_empty(concepts, 'trait')
    assert len(concepts) > 0
    pprint(concepts)
    assert 'systemutvecklare' in concepts['occupation']
    assert 'java' in concepts['skill']
    assert 'noggrann' in concepts['trait']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_unigram_multiple_skills():
    print('\n============================', sys._getframe().f_code.co_name, '============================')

    concepts = text_to_concept.text_to_concepts('noggrann systemutvecklare java python cobol')
    assert_not_empty(concepts, 'occupation')
    assert_not_empty(concepts, 'skill')
    assert_not_empty(concepts, 'trait')
    # pprint(concepts)
    assert 'systemutvecklare' in concepts['occupation']
    assert 'java' in concepts['skill']
    assert 'python' in concepts['skill']
    assert 'cobol' in concepts['skill']
    assert 'noggrann' in concepts['trait']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_jobtitle_with_hyphen():
    print('\n============================', sys._getframe().f_code.co_name, '============================')

    concepts = text_to_concept.text_to_concepts('HR-specialister')
    # pprint(concepts)
    assert_not_empty(concepts, 'occupation')
    assert 'hr-specialist' in concepts['occupation']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_unigram_misspelled_input():
    print('\n============================', sys._getframe().f_code.co_name, '============================')

    concepts = text_to_concept.text_to_concepts('noggran sjukssköterska java')
    assert_not_empty(concepts, 'occupation')
    assert_not_empty(concepts, 'trait')
    pprint(concepts)
    assert 'sjuksköterska' in concepts['occupation']
    assert 'noggrann' in concepts['trait']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_bigrams():
    concepts = text_to_concept.text_to_concepts('inhouse key account manager säljare')
    assert_not_empty(concepts, 'occupation')
    pprint(concepts)

    assert 'key account manager' in concepts['occupation']
    assert 'säljare' in concepts['occupation']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_diverse_occupationterms_to_concepts():
    input_type = 'occupation'
    assert_concept_name = 'souschef'

    assert_term_to_concept('souschef', input_type, assert_concept_name)
    assert_term_to_concept('sous-chef', input_type, assert_concept_name)
    # TODO: Lägg till även 'sous chef' när denna term finns i narvalontology i prod
    # assert_term_to_concept('sous chef', input_type, assert_concept_name)


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_uppercase_input():
    concepts = text_to_concept.text_to_concepts('Key Account Manager SÄLJARE')
    assert len(concepts) > 0
    assert_not_empty(concepts, 'occupation')
    # pprint(concepts)
    assert 'key account manager' in concepts['occupation']
    assert 'säljare' in concepts['occupation']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_plus_input():
    # concepts = text_to_concept.text_to_concepts('chef+chef')
    concepts = text_to_concept.text_to_concepts('psykolog+psykologer')
    # concepts = text_to_concept.text_to_concepts('tyska+tyska')
    pprint(concepts)
    assert len(concepts) > 0
    assert_not_empty(concepts, 'occupation')
    assert 'psykolog' in concepts['occupation']
    assert 'psykolog' in concepts['occupation_must']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_non_concept_words():
    concepts = text_to_concept.text_to_concepts(
        'jättebra och flexibel Key Account Manager som vill jobba med försäljning på Spotify i Hartford, Connecticut')
    assert_not_empty(concepts, 'occupation')
    assert_not_empty(concepts, 'skill')
    assert_not_empty(concepts, 'trait')
    print(concepts)
    assert 'key account manager' in concepts['occupation']
    assert 'försäljning' in concepts['skill']
    assert 'flexibel' in concepts['trait']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_must_words():
    concepts = text_to_concept.text_to_concepts(
        'mållare +målare säljare +key account manager python +java positiv +noggrann -flexibel')
    assert_not_empty(concepts, 'occupation')
    assert_not_empty(concepts, 'occupation_must')
    assert_not_empty(concepts, 'skill')
    assert_not_empty(concepts, 'skill_must')
    assert_not_empty(concepts, 'trait')
    assert_not_empty(concepts, 'trait_must')
    assert_not_empty(concepts, 'trait_must_not')

    print(concepts)

    assert 'säljare' in concepts['occupation']
    assert 'målare' in concepts['occupation_must']
    assert 'key account manager' in concepts['occupation_must']
    assert 'python' in concepts['skill']
    assert 'java' in concepts['skill_must']
    assert 'positiv' in concepts['trait']
    assert 'noggrann' in concepts['trait_must']
    assert 'flexibel' in concepts['trait_must_not']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_must_not_words():
    concepts = text_to_concept.text_to_concepts(
        'mållare -målare säljare -key account manager python -java -noggrann flexibel')
    assert_not_empty(concepts, 'occupation')
    assert_not_empty(concepts, 'occupation_must_not')
    assert_not_empty(concepts, 'skill')
    assert_not_empty(concepts, 'skill_must_not')
    assert_not_empty(concepts, 'trait')
    assert_not_empty(concepts, 'trait_must_not')

    print(concepts)

    assert 'säljare' in concepts['occupation']
    assert 'målare' in concepts['occupation_must_not']
    assert 'key account manager' in concepts['occupation_must_not']
    assert 'python' in concepts['skill']
    assert 'java' in concepts['skill_must_not']
    assert 'flexibel' in concepts['trait']
    assert 'noggrann' in concepts['trait_must_not']


def assert_term_to_concept(input_term, input_type, assert_concept_name):
    concepts = text_to_concept.text_to_concepts(input_term)
    assert_not_empty(concepts, input_type)
    assert assert_concept_name in concepts[input_type]


def assert_result_has_keys(concepts):
    for name in ['skill', 'occupation', 'trait',
                 'skill_must', 'occupation_must', 'trait_must',
                 'skill_must_not', 'occupation_must_not', 'trait_must_not']:
        assert name in concepts


def assert_not_empty(concepts, resulttype):
    assert type(concepts) == dict
    assert_result_has_keys(concepts)

    assert len(concepts[resulttype]) > 0


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
