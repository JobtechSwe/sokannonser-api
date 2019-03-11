import logging
import certifi
from ssl import create_default_context
from elasticsearch import Elasticsearch
from beaker.cache import CacheManager
from beaker import util

from sokannonser import settings
from sokannonser.repository.ontology import Ontology

log = logging.getLogger(__name__)


class TextToConcept(object):
    cache_opts = {
        'cache.expire': 60,#60 * 60 * 24 * 7,  # Expire time in seconds
        'cache.type': 'memory',
    }

    COMPETENCE_KEY = 'KOMPETENS'
    OCCUPATION_KEY = 'YRKE'
    TRAIT_KEY = 'FORMAGA'
    REMOVED_TAG = '<removed>'

    cache = CacheManager(**util.parse_cache_config_options(cache_opts))

    def __init__(self, ontologyhost='localhost', ontologyport=9200,
                 ontologyindex='narvalontology', ontologyuser=None, ontologypwd=None):
        log.info('Creating TextToConcept')

        self.cachekey = '%s-%s-%s-%s' % (ontologyhost, ontologyport, ontologyindex, ontologyuser)

        self.client = self.create_elastic_client(ontologyhost, ontologyport, ontologyuser, ontologypwd)

        if settings.ES_HOST != 'localhost':
            # Cache ontology directly unless it's a local call (tests or docker build)
            self.get_ontology()

    def get_ontology(self):
        return self._get_cached_ontology(self.cachekey)

    @cache.cache('_get_cached_ontology')
    def _get_cached_ontology(self, cachekey):
        log.info('Creating ontology, cachekey: %s' % cachekey)
        ontology = Ontology(client=self.client,
                            concept_type=None,
                            include_misspelled=True)
        log.info('Created ontology')
        return ontology

    @staticmethod
    def create_elastic_client(host, port, user, pwd):
        log.info('Creating ontology elasticclient, host: %s, port: %s, user: %s' % (
            host, port, user))
        if user and pwd:
            context = create_default_context(cafile=certifi.where())
            client = Elasticsearch([host], port=port,
                                   use_ssl=True, scheme='https',
                                   ssl_context=context,
                                   http_auth=(user, pwd))
        else:
            client = Elasticsearch([{'host': host, 'port': port}])

        return client

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

    @staticmethod
    def filter_concepts(concept, concept_type, operator):
        if concept['type'] == concept_type and concept['operator'] == operator:
            return True
        else:
            return False
