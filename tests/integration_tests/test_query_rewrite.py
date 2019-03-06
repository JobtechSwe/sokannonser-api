import sys
import os
import pytest
from sokannonser import settings
# from pprint import pprint

from sokannonser.repository.text_to_concept import TextToConcept

host = settings.ES_HOST
index = 'narvalontology'
user = settings.ES_USER
pwd = settings.ES_PWD
port = settings.ES_PORT

protocol = 'http' if host == 'localhost' else 'https'
url = protocol + '://' + host + ':' + str(port)

print('Running unittests calling %s' % url)

text_to_concept = TextToConcept(ontologyhost=url,
                                ontologyindex='narvalontology',
                                ontologyuser=user,
                                ontologypwd=pwd)


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_unigram_competence():
    print('\n============================', sys._getframe().f_code.co_name, '============================')

    concepts = text_to_concept.text_to_concepts('noggrann systemutvecklare java')
    assert concepts is not None
    assert len(concepts) > 0
    # pprint(concepts)
    assert 'java' in concepts['skills']
    assert 'systemutvecklare' in concepts['occupations']
    assert 'noggrann' in concepts['traits']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_unigram_multiple_skills():
    print('\n============================', sys._getframe().f_code.co_name, '============================')

    concepts = text_to_concept.text_to_concepts('noggrann systemutvecklare java python cobol')
    assert len(concepts) > 0
    # pprint(concepts)
    assert 'java' in concepts['skills']
    assert 'python' in concepts['skills']
    assert 'cobol' in concepts['skills']
    assert 'systemutvecklare' in concepts['occupations']
    assert 'noggrann' in concepts['traits']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_unigram_misspelled_input():
    print('\n============================', sys._getframe().f_code.co_name, '============================')

    concepts = text_to_concept.text_to_concepts('noggran sjukssköterska java')
    assert len(concepts) > 0
    # pprint(concepts)
    assert 'noggrann' in concepts['traits']
    assert 'sjuksköterska' in concepts['occupations']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_bigrams():
    concepts = text_to_concept.text_to_concepts('inhouse key account manager säljare')
    assert len(concepts) > 0
    # pprint(concepts)

    assert 'key account manager' in concepts['occupations']
    assert 'säljare' in concepts['occupations']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_uppercase_input():
    concepts = text_to_concept.text_to_concepts('Key Account Manager SÄLJARE')
    assert len(concepts) > 0
    # pprint(concepts)
    assert 'key account manager' in concepts['occupations']
    assert 'säljare' in concepts['occupations']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_non_concept_words():
    concepts = text_to_concept.text_to_concepts(
        'jättebra och flexibel Key Account Manager som vill jobba med försäljning på Spotify i Hartford, Connecticut')
    assert len(concepts) > 0
    # print(concepts)
    assert 'försäljning' in concepts['skills']
    assert 'key account manager' in concepts['occupations']
    assert 'flexibel' in concepts['traits']


# @pytest.mark.skip(reason="Temporarily disabled")
@pytest.mark.integration
def test_rewrite_must_not_words():
    concepts = text_to_concept.text_to_concepts('mållare -målare säljare -key account manager python -java -noggrann flexibel')
    assert len(concepts) > 0
    # print(concepts)
    assert 'python' in concepts['skills']
    assert 'java' in concepts['skills_must_not']
    assert 'säljare' in concepts['occupations']
    assert 'målare' in concepts['occupations_must_not']
    assert 'key account manager' in concepts['occupations_must_not']
    assert 'flexibel' in concepts['traits']
    assert 'noggrann' in concepts['traits_must_not']


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__), '-svv', '-ra', '-m integration'])
