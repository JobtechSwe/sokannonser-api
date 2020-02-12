import logging
import re
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
    LOCATION_KEY = 'GEO'
    REMOVED_TAG = '<removed>'

    def __init__(self, ontologyhost='localhost', ontologyport=9200,
                 ontologyindex='narvalontology', ontologyuser=None, ontologypwd=None):
        log.info('Creating TextToConcept')

        self.client = self.create_elastic_client(ontologyhost, ontologyport, ontologyuser,
                                                 ontologypwd)
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
                                     annons_index=settings.ES_INDEX,
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

    RE_PLUS_MINUS = re.compile(r"((^| )[+-])", re.UNICODE)

    def clean_plus_minus(self, text):
        return self.RE_PLUS_MINUS.sub(" ", text).strip()

    def text_to_concepts(self, text):
        # Note: Remove eventual '+' and '-' in every freetext query word since flashText is configured
        # so it can't find words starting with minus/hyphen.
        searchtext = self.clean_plus_minus(text)
        text_lower = text.lower()
        ontology_concepts_orig = self.get_ontology().get_concepts(searchtext, concept_type=None,
                                                                  span_info=True)
        ontology_concepts = [c[0] for c in ontology_concepts_orig]

        # print(ontology_concepts)
        text_lower_plus_blank_end = text_lower + ' '

        for concept in ontology_concepts:
            # print(concept)
            concept_term = concept['term']
            if '-' + concept_term + ' ' in text_lower_plus_blank_end:
                concept['operator'] = OP_MINUS
            elif '+' + concept_term + ' ' in text_lower_plus_blank_end:
                concept['operator'] = OP_PLUS
            else:
                concept['operator'] = OP_NONE

        skills = [c for c in ontology_concepts
                  if self.filter_concepts(c, self.COMPETENCE_KEY, OP_NONE)]
        occupations = [c for c in ontology_concepts
                       if self.filter_concepts(c, self.OCCUPATION_KEY, OP_NONE)]
        traits = [c for c in ontology_concepts
                  if self.filter_concepts(c, self.TRAIT_KEY, OP_NONE)]
        locations = [c for c in ontology_concepts
                     if self.filter_concepts(c, self.LOCATION_KEY, OP_NONE)]

        skills_must = [c for c in ontology_concepts
                       if self.filter_concepts(c, self.COMPETENCE_KEY, OP_PLUS)]
        occupations_must = [c for c in ontology_concepts
                            if self.filter_concepts(c, self.OCCUPATION_KEY, OP_PLUS)]
        traits_must = [c for c in ontology_concepts
                       if self.filter_concepts(c, self.TRAIT_KEY, OP_PLUS)]
        locations_must = [c for c in ontology_concepts
                          if self.filter_concepts(c, self.LOCATION_KEY, OP_PLUS)]

        skills_must_not = [c for c in ontology_concepts
                           if self.filter_concepts(c, self.COMPETENCE_KEY, OP_MINUS)]
        occupations_must_not = [c for c in ontology_concepts
                                if self.filter_concepts(c, self.OCCUPATION_KEY, OP_MINUS)]
        traits_must_not = [c for c in ontology_concepts
                           if self.filter_concepts(c, self.TRAIT_KEY, OP_MINUS)]
        locations_must_not = [c for c in ontology_concepts
                              if self.filter_concepts(c, self.LOCATION_KEY, OP_MINUS)]

        result = {'skill': skills,
                  'occupation': occupations,
                  'trait': traits,
                  'location': locations,
                  'skill_must': skills_must,
                  'occupation_must': occupations_must,
                  'trait_must': traits_must,
                  'location_must': locations_must,
                  'skill_must_not': skills_must_not,
                  'occupation_must_not': occupations_must_not,
                  'trait_must_not': traits_must_not,
                  'location_must_not': locations_must_not}

        return result

    @staticmethod
    def filter_concepts(concept, concept_type, operator):
        if concept['type'] == concept_type and concept['operator'] == operator:
            return True
        else:
            return False
