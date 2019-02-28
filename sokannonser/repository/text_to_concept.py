from beaker.cache import CacheManager
from beaker import util

from sokannonser.repository.ontology import Ontology


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

    def __init__(self, ontologyhost='http://localhost:9200', ontologyindex='narvalontology', ontologyuser=None,
                 ontologypwd=None):
        self.ontologyhost = ontologyhost
        self.ontologyindex = ontologyindex
        self.ontologyuser = ontologyuser
        self.ontologypwd = ontologypwd

    @cache.cache('get_ontology')
    def get_ontology(self):
        return Ontology(url=self.ontologyhost,
                        index=self.ontologyindex,
                        user=self.ontologyuser,
                        pwd=self.ontologypwd,
                        concept_type=None,
                        include_misspelled=True)

    def text_to_concepts(self, text):
        ontology_concepts = self.get_ontology().get_concepts(text, concept_type=None, span_info=False)

        text_lower = text.lower()

        other_text = text_lower

        for concept in ontology_concepts:
            term = concept['term']
            other_text = other_text.replace(term, self.REMOVED_TAG)

        # print(other_text)

        others = [word for word in other_text.split(' ') if word != self.REMOVED_TAG]

        # print(other_words)

        competencies = [c['concept'].lower() for c in ontology_concepts if c['type'] == self.COMPETENCE_KEY]
        occupations = [c['concept'].lower() for c in ontology_concepts if c['type'] == self.OCCUPATION_KEY]
        traits = [c['concept'].lower() for c in ontology_concepts if c['type'] == self.TRAIT_KEY]

        result = {'competencies': competencies, 'occupations': occupations, 'traits': traits, 'others': others}

        return result
