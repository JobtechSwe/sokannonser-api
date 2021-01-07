#  -*- coding: utf-8 -*-
import logging
import pytest
import sys

from dateutil import parser

from sokannonser import settings
from sokannonser.repository.querybuilder import QueryBuilder
from sokannonser.repository import taxonomy

log = logging.getLogger(__name__)


class MockOntology:
    def __init__(self):
        self.extracted_locations = set()


class MockTextToConcept:
    def __init__(self):
        self.ontology = MockOntology()

    def text_to_concepts(self, text):
        skills = {
            "python": {
                "term": "python",
                "uuid": "0b6d3a08-3cc3-546d-b8ed-f2de299bafdb",
                "concept": "Python",
                "type": "KOMPETENS",
                "term_uuid": "f60fa7fd-00f7-5803-acd7-1a3eda170397",
                "term_misspelled": False,
                "plural_occupation": False,
                "definite_occupation": False,
                "version": "SYNONYM-DIC-2.0.1.25",
                "operator": ""
            },
            "java": {
                "term": "java",
                "uuid": "c965e8aa-751a-5923-97bd-b8bd6d5e813a",
                "concept": "Java",
                "type": "KOMPETENS",
                "term_uuid": "e3d2a75a-5717-56d2-ad8a-ee4b5baf8530",
                "term_misspelled": False,
                "plural_occupation": False,
                "definite_occupation": False,
                "version": "SYNONYM-DIC-2.0.1.25",
                "operator": "+"
            },
            "php": {
                "term": "php",
                "uuid": "3e3629d1-95f6-5b0e-8f5c-d6a709fd94e2",
                "concept": "Php",
                "type": "KOMPETENS",
                "term_uuid": "216af07e-d210-572f-8885-b13d79b80acc",
                "term_misspelled": False,
                "plural_occupation": False,
                "definite_occupation": False,
                "version": "SYNONYM-DIC-2.0.1.25",
                "operator": "-"
            }
        }
        occupations = {
            "systemutvecklare": {
                "term": "systemutvecklare",
                "uuid": "df9e7a73-2cc3-5b32-a84e-7e68a527e80e",
                "concept": "Systemutvecklare",
                "type": "YRKE",
                "term_uuid": "7296755c-acf2-5eed-9d4b-e4cd845cd05a",
                "term_misspelled": False,
                "plural_occupation": False,
                "definite_occupation": False,
                "version": "SYNONYM-DIC-2.0.1.25",
                "operator": ""
            }
        }
        response = {
            "skill": [],
            "occupation": [],
            "trait": [],
            "location": [],
            "skill_must": [],
            "occupation_must": [],
            "trait_must": [],
            "location_must": [],
            "skill_must_not": [],
            "occupation_must_not": [],
            "trait_must_not": [],
            "location_must_not": []
        }
        for word in text.split():
            if word.startswith("+"):
                word = word[1:]
                if word in skills:
                    response['skill_must'].append(skills[word])
                if word in occupations:
                    response['occupation_must'].append(occupations[word])
            elif word.startswith("-"):
                word = word[1:]
                if word in skills:
                    response['skill_must_not'].append(skills[word])
                if word in occupations:
                    response['occupation_must_not'].append(occupations[word])
            else:
                if word in skills:
                    response['skill'].append(skills[word])
                if word in occupations:
                    response['occupation'].append(occupations[word])

        return response
