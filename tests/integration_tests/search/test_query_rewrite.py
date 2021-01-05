import sys
import os
import pytest
from sokannonser import settings
from sokannonser.repository.text_to_concept import TextToConcept
from sokannonser.settings import ONTOLOGY_INDEX

text_to_concept = TextToConcept(ontologyhost=settings.ES_HOST,
                                ontologyport=settings.ES_PORT,
                                ontologyindex=ONTOLOGY_INDEX,
                                ontologyuser=settings.ES_USER,
                                ontologypwd=settings.ES_PWD)


@pytest.mark.smoke
@pytest.mark.integration
def test_rewrite_unigram_competence():
    print('\n==================', sys._getframe().f_code.co_name, '==================')
    concepts = text_to_concept.text_to_concepts('noggrann systemutvecklare java')
    assert concepts is not None
    assert_not_empty(concepts, 'occupation')
    assert_not_empty(concepts, 'skill')
    assert_not_empty(concepts, 'trait')
    assert len(concepts) > 0
    assert 'systemutvecklare' in [c['concept'].lower() for c in concepts['occupation']]
    assert 'java' in [c['concept'].lower() for c in concepts['skill']]
    assert 'noggrann' in [c['concept'].lower() for c in concepts['trait']]


@pytest.mark.integration
def test_rewrite_unigram_multiple_skills():
    print('\n==================', sys._getframe().f_code.co_name, '==================')

    concepts = text_to_concept.text_to_concepts('noggrann systemutvecklare java python cobol')
    assert_not_empty(concepts, 'occupation')
    assert_not_empty(concepts, 'skill')
    assert_not_empty(concepts, 'trait')
    occupations = [c['concept'].lower() for c in concepts['occupation']]
    skills = [c['concept'].lower() for c in concepts['skill']]
    traits = [c['concept'].lower() for c in concepts['trait']]
    assert 'systemutvecklare' in occupations
    assert 'java' in skills
    assert 'python' in skills
    assert 'cobol' in skills
    assert 'noggrann' in traits


@pytest.mark.integration
def test_rewrite_jobtitle_with_hyphen():
    print('\n==================', sys._getframe().f_code.co_name, '==================')
    concepts = text_to_concept.text_to_concepts('HR-specialister')
    assert_not_empty(concepts, 'occupation')
    assert 'hr-specialist' in [c['concept'].lower() for c in concepts['occupation']]


@pytest.mark.integration
def test_rewrite_competence_special_characters():
    print('\n==================', sys._getframe().f_code.co_name, '==================')

    concepts = text_to_concept.text_to_concepts('java c++ .net microsoft visual c++ c-sharp c-level')
    assert_not_empty(concepts, 'skill')
    assert 'java' in [c['concept'].lower() for c in concepts['skill']]
    assert 'c++' in [c['concept'].lower() for c in concepts['skill']]
    assert '.net' in [c['concept'].lower() for c in concepts['skill']]
    assert 'visual c++' in [c['concept'].lower() for c in concepts['skill']]
    assert 'c' not in [c['concept'].lower() for c in concepts['skill']]


@pytest.mark.integration
def test_rewrite_unigram_misspelled_input():
    print('\n==================', sys._getframe().f_code.co_name, '==================')
    concepts = text_to_concept.text_to_concepts('noggran sjukssköterska java')
    assert_not_empty(concepts, 'occupation')
    assert_not_empty(concepts, 'trait')
    assert 'sjuksköterska' in [c['concept'].lower() for c in concepts['occupation']]
    assert 'noggrann' in [c['concept'].lower() for c in concepts['trait']]


@pytest.mark.integration
def test_rewrite_unigram_misspelled_single_word_input():
    print('\n==================', sys._getframe().f_code.co_name, '==================')
    concepts = text_to_concept.text_to_concepts('noggran')
    assert_not_empty(concepts, 'trait')
    assert 'noggrann' in [c['concept'].lower() for c in concepts['trait']]


@pytest.mark.integration
def test_rewrite_bigrams():
    concepts = text_to_concept.text_to_concepts('inhouse key account manager säljare')
    assert_not_empty(concepts, 'occupation')
    assert 'key account manager' in [c['concept'].lower() for c in concepts['occupation']]
    assert 'försäljare' in [c['concept'].lower() for c in concepts['occupation']]


@pytest.mark.integration
def test_rewrite_diverse_occupationterms_to_concepts():
    input_type = 'occupation'
    assert_concept_name = 'souschef'
    assert_term_to_concept('souschef', input_type, assert_concept_name)
    assert_term_to_concept('sous-chef', input_type, assert_concept_name)
    assert_term_to_concept('sous chef', input_type, assert_concept_name)


@pytest.mark.integration
def test_rewrite_uppercase_input():
    concepts = text_to_concept.text_to_concepts('Key Account Manager SÄLJARE')
    assert len(concepts) > 0
    assert_not_empty(concepts, 'occupation')
    assert 'key account manager' in [c['concept'].lower() for c in concepts['occupation']]
    assert 'försäljare' in [c['concept'].lower() for c in concepts['occupation']]


@pytest.mark.integration
def test_rewrite_plus_input():
    concepts = text_to_concept.text_to_concepts('psykolog+psykologer')
    assert len(concepts) > 0
    assert_not_empty(concepts, 'occupation')
    assert 'psykolog' in [c['concept'].lower() for c in concepts['occupation']]
    assert 'psykolog' in [c['concept'].lower() for c in concepts['occupation_must']]


@pytest.mark.integration
def test_rewrite_non_concept_words():
    concepts = text_to_concept.text_to_concepts(
        'jättebra och flexibel Key Account Manager som vill jobba med försäljning på Spotify i Hartford, Connecticut')
    assert_not_empty(concepts, 'occupation')
    assert_not_empty(concepts, 'skill')
    assert_not_empty(concepts, 'trait')
    assert 'key account manager' in [c['concept'].lower() for c in concepts['occupation']]
    assert 'försäljning' in [c['concept'].lower() for c in concepts['skill']]
    assert 'flexibel' in [c['concept'].lower() for c in concepts['trait']]


@pytest.mark.integration
def test_rewrite_must_words():
    concepts = text_to_concept.text_to_concepts(
        'mållare +målare säljare +key account manager c-sharp +java positiv +noggrann -flexibel stockholm +solna -sundbyberg')
    assert_not_empty(concepts, 'occupation')
    assert_not_empty(concepts, 'occupation_must')
    assert_not_empty(concepts, 'skill')
    assert_not_empty(concepts, 'skill_must')
    assert_not_empty(concepts, 'trait')
    assert_not_empty(concepts, 'trait_must')
    assert_not_empty(concepts, 'trait_must_not')
    assert_not_empty(concepts, 'location')
    assert_not_empty(concepts, 'location_must')
    assert_not_empty(concepts, 'location_must_not')

    assert 'försäljare' in [c['concept'].lower() for c in concepts['occupation']]
    assert 'målare' in [c['concept'].lower() for c in concepts['occupation_must']]
    assert 'key account manager' in [c['concept'].lower() for c in concepts['occupation_must']]
    assert 'c#' in [c['concept'].lower() for c in concepts['skill']]
    assert 'java' in [c['concept'].lower() for c in concepts['skill_must']]
    assert 'positiv' in [c['concept'].lower() for c in concepts['trait']]
    assert 'noggrann' in [c['concept'].lower() for c in concepts['trait_must']]
    assert 'flexibel' in [c['concept'].lower() for c in concepts['trait_must_not']]


@pytest.mark.integration
def test_rewrite_must_not_words():
    concepts = text_to_concept.text_to_concepts(
        'mållare -målare java-utvecklare -key account manager c-sharp -java -noggrann flexibel solna -sundbyberg')
    assert_not_empty(concepts, 'occupation')
    assert_not_empty(concepts, 'occupation_must_not')
    assert_not_empty(concepts, 'skill')
    assert_not_empty(concepts, 'skill_must_not')
    assert_not_empty(concepts, 'trait')
    assert_not_empty(concepts, 'trait_must_not')
    assert_not_empty(concepts, 'location')
    assert_not_empty(concepts, 'location_must_not')

    assert 'javautvecklare' in [c['concept'].lower() for c in concepts['occupation']]
    assert 'målare' in [c['concept'].lower() for c in concepts['occupation_must_not']]
    assert 'key account manager' in [c['concept'].lower() for c in concepts['occupation_must_not']]
    assert 'c#' in [c['concept'].lower() for c in concepts['skill']]
    assert 'java' in [c['concept'].lower() for c in concepts['skill_must_not']]
    assert 'flexibel' in [c['concept'].lower() for c in concepts['trait']]
    assert 'noggrann' in [c['concept'].lower() for c in concepts['trait_must_not']]


def assert_term_to_concept(input_term, input_type, assert_concept_name):
    concepts = text_to_concept.text_to_concepts(input_term)
    assert_not_empty(concepts, input_type)
    assert assert_concept_name in [c['concept'].lower() for c in concepts[input_type]]


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
