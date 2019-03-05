import logging
from beaker.cache import CacheManager
from beaker import util

from sokannonser.repository.ontology import Ontology

log = logging.getLogger(__name__)


class TextToConcept(object):
    cache_opts = {
        'cache.expire': 60 * 60 * 1,  # Expire time in seconds
        'cache.type': 'memory'
    }

    COMPETENCE_KEY = 'KOMPETENS'
    OCCUPATION_KEY = 'YRKE'
    TRAIT_KEY = 'FORMAGA'
    REMOVED_TAG = '<removed>'

    cache = CacheManager(**util.parse_cache_config_options(cache_opts))

    def __init__(self, ontologyhost='http://localhost:9200',
                 ontologyindex='narvalontology', ontologyuser=None, ontologypwd=None):
        self.ontologyhost = ontologyhost
        self.ontologyindex = ontologyindex
        self.ontologyuser = ontologyuser
        self.ontologypwd = ontologypwd
        self.get_ontology()

    @cache.cache('get_ontology')
    def get_ontology(self):
        return Ontology(url=self.ontologyhost,
                        index=self.ontologyindex,
                        user=self.ontologyuser,
                        pwd=self.ontologypwd,
                        concept_type=None,
                        include_misspelled=True)

    def text_to_concepts(self, text):
        ontology_concepts = self.get_ontology().get_concepts(text, concept_type=None,
                                                             span_info=False)

        text_lower = text.lower()

        tmp_text = text_lower

        for concept in ontology_concepts:
            term = concept['term']
            term_index = tmp_text.index(term) - 1
            prev_char = tmp_text[term_index:term_index + 1]
            # print('term: %s, prev_char: %s' % (term, prev_char))
            tmp_text = tmp_text.replace(term, self.REMOVED_TAG)
            concept['operator'] = prev_char if prev_char == '-' else ''

        # print(tmp_text)

        skills = [c['concept'].lower() for c in ontology_concepts
                  if self.filter_concepts(c, self.COMPETENCE_KEY, '')]
        occupations = [c['concept'].lower() for c in ontology_concepts
                       if self.filter_concepts(c, self.OCCUPATION_KEY, '')]
        traits = [c['concept'].lower() for c in ontology_concepts
                  if self.filter_concepts(c, self.TRAIT_KEY, '')]

        skills_must_not = [c['concept'].lower() for c in ontology_concepts
                           if self.filter_concepts(c, self.COMPETENCE_KEY, '-')]
        occupations_must_not = [c['concept'].lower() for c in ontology_concepts
                                if self.filter_concepts(c, self.OCCUPATION_KEY, '-')]
        traits_must_not = [c['concept'].lower() for c in ontology_concepts
                           if self.filter_concepts(c, self.TRAIT_KEY, '-')]

        result = {'skills': skills,
                  'occupations': occupations,
                  'traits': traits,
                  'skills_must_not': skills_must_not,
                  'occupations_must_not': occupations_must_not,
                  'traits_must_not': traits_must_not}

        return result

    def filter_concepts(self, concept, concept_type, operator):
        if concept['type'] == concept_type and concept['operator'] == operator:
            return True
        else:
            return False
