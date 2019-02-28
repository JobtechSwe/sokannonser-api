import sys
import os
import pytest
# from pprint import pprint

from sokannonser.repository.text_to_concept import TextToConcept

text_to_concept = TextToConcept(ontologyhost='http://localhost:9200',
                                ontologyindex='narvalontology',
                                ontologyuser=None,
                                ontologypwd=None)


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.unit
def test_rewrite_unigram_competence():
    print('\n============================', sys._getframe().f_code.co_name, '============================')

    concepts = text_to_concept.text_to_concepts('noggrann systemutvecklare java')
    assert concepts is not None
    assert len(concepts) > 0
    # pprint(concepts)
    assert 'java' in concepts['competencies']
    assert 'systemutvecklare' in concepts['occupations']
    assert 'noggrann' in concepts['traits']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.unit
def test_rewrite_unigram_multiple_competencies():
    print('\n============================', sys._getframe().f_code.co_name, '============================')

    concepts = text_to_concept.text_to_concepts('noggrann systemutvecklare java python cobol')
    assert len(concepts) > 0
    # pprint(concepts)
    assert 'java' in concepts['competencies']
    assert 'python' in concepts['competencies']
    assert 'cobol' in concepts['competencies']
    assert 'systemutvecklare' in concepts['occupations']
    assert 'noggrann' in concepts['traits']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.unit
def test_rewrite_unigram_misspelled_input():
    print('\n============================', sys._getframe().f_code.co_name, '============================')

    concepts = text_to_concept.text_to_concepts('noggran sjukssköterska java')
    assert len(concepts) > 0
    # pprint(concepts)
    assert 'noggrann' in concepts['traits']
    assert 'sjuksköterska' in concepts['occupations']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.unit
def test_rewrite_bigrams():
    concepts = text_to_concept.text_to_concepts('inhouse key account manager säljare')
    assert len(concepts) > 0
    # pprint(concepts)

    assert 'key account manager' in concepts['occupations']
    assert 'säljare' in concepts['occupations']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.unit
def test_rewrite_uppercase_input():
    concepts = text_to_concept.text_to_concepts('Key Account Manager SÄLJARE')
    assert len(concepts) > 0
    # pprint(concepts)
    assert 'key account manager' in concepts['occupations']
    assert 'säljare' in concepts['occupations']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.unit
def test_rewrite_non_concept_words():
    concepts = text_to_concept.text_to_concepts(
        'jättebra och flexibel Key Account Manager som vill jobba med försäljning på Spotify i Boston, Connecticut')
    assert len(concepts) > 0
    # pprint(concepts)
    assert 'försäljning' in concepts['competencies']
    assert 'key account manager' in concepts['occupations']
    assert 'flexibel' in concepts['traits']

    assert 'jättebra' in concepts['others']
    assert 'boston,' in concepts['others']
    assert 'connecticut' in concepts['others']
    assert 'spotify' in concepts['others']


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m unit'])
