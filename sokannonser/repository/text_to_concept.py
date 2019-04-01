import logging
import certifi
from ssl import create_default_context
from elasticsearch import Elasticsearch
from copy import copy
from sokannonser import settings
from sokannonser.repository.ontology import Ontology

log = logging.getLogger(__name__)

OP_NONE = ''
OP_PLUS = '+'
OP_MINUS = '-'


class TextToConcept(object):
    COMPETENCE_KEY = 'KOMPETENS'
    OCCUPATION_KEY = 'YRKE'
    TRAIT_KEY = 'FORMAGA'
    REMOVED_TAG = '<removed>'

    def __init__(self, ontologyhost='localhost', ontologyport=9200,
                 ontologyindex='narvalontology', ontologyuser=None, ontologypwd=None):
        log.info('Creating TextToConcept')

        self.client = self.create_elastic_client(ontologyhost, ontologyport, ontologyuser, ontologypwd)
        self.ontologyindex = ontologyindex

        self.ontology = None

        if settings.ES_HOST != 'localhost':
            # Cache ontology directly unless it's a local call (tests or docker build)
            self.get_ontology()

    def get_ontology(self):
        if self.ontology is None:
            log.info('Creating Ontology, ontologyindex: %s' % self.ontologyindex)
            self.ontology = Ontology(client=self.client,
                                     index=self.ontologyindex,
                                     concept_type=None,
                                     include_misspelled=True)
            log.info('Done creating Ontology, ontologyindex: %s' % self.ontologyindex)

        return self.ontology

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
        ontology_concepts_orig = self.get_ontology().get_concepts(text, concept_type=None,
                                                                  span_info=True)

        ontology_concepts = []
        for concept_data in ontology_concepts_orig:
            concept = copy(concept_data[0])
            concept['span_begin'] = concept_data[1]
            concept['span_end'] = concept_data[2]
            ontology_concepts.append(concept)

        # print(ontology_concepts)
        text_lower = text.lower()

        for concept in ontology_concepts:
            term_index = concept['span_begin']
            prev_char = text_lower[term_index - 1:term_index]
            if prev_char == OP_MINUS:
                concept['operator'] = OP_MINUS
            elif prev_char == OP_PLUS:
                concept['operator'] = OP_PLUS
            else:
                concept['operator'] = OP_NONE

        skills = [c['concept'].lower() for c in ontology_concepts
                  if self.filter_concepts(c, self.COMPETENCE_KEY, OP_NONE)]
        occupations = [c['concept'].lower() for c in ontology_concepts
                       if self.filter_concepts(c, self.OCCUPATION_KEY, OP_NONE)]
        traits = [c['concept'].lower() for c in ontology_concepts
                  if self.filter_concepts(c, self.TRAIT_KEY, OP_NONE)]

        skills_must = [c['concept'].lower() for c in ontology_concepts
                       if self.filter_concepts(c, self.COMPETENCE_KEY, OP_PLUS)]
        occupations_must = [c['concept'].lower() for c in ontology_concepts
                            if self.filter_concepts(c, self.OCCUPATION_KEY, OP_PLUS)]
        traits_must = [c['concept'].lower() for c in ontology_concepts
                       if self.filter_concepts(c, self.TRAIT_KEY, OP_PLUS)]

        skills_must_not = [c['concept'].lower() for c in ontology_concepts
                           if self.filter_concepts(c, self.COMPETENCE_KEY, OP_MINUS)]
        occupations_must_not = [c['concept'].lower() for c in ontology_concepts
                                if self.filter_concepts(c, self.OCCUPATION_KEY, OP_MINUS)]
        traits_must_not = [c['concept'].lower() for c in ontology_concepts
                           if self.filter_concepts(c, self.TRAIT_KEY, OP_MINUS)]

        result = {'skills': skills,
                  'occupations': occupations,
                  'traits': traits,
                  'skills_must': skills_must,
                  'occupations_must': occupations_must,
                  'traits_must': traits_must,
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
