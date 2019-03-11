import logging
from flashtext.keyword import KeywordProcessor
from elasticsearch import ElasticsearchException
from elasticsearch.helpers import scan

log = logging.getLogger(__name__)


class Ontology(object):

    # def __init__(self, host='localhost', port=9200, index='narvalontology', user=None, pwd=None, stoplist=None,
    #              concept_type=None, include_misspelled=False):
    def __init__(self, client=None, index='narvalontology', stoplist=None,
                 concept_type=None, include_misspelled=False):
        self.keyword_processor = KeywordProcessor()
        self.init_keyword_processor()

        self.client = client

        self.index = index
        if stoplist is None:
            stoplist = []
        self.stoplist = stoplist
        self.concept_type = concept_type
        self.include_misspelled = include_misspelled

        self.concept_to_term = {}

        self.init_ontology()

    def __len__(self):
        return len(self.keyword_processor)

    def misspelled_predicate(self, value):
        if not self.include_misspelled and value['term_misspelled']:
            return False
        return True

    def get_ontologi_iterator(self):
        if self.concept_type is not None:
            return (ontologi_concept for ontologi_concept in self.elastic_iterator()
                    if ontologi_concept['term'] not in self.stoplist
                    and ontologi_concept['type'] == self.concept_type
                    and self.misspelled_predicate(ontologi_concept))
        return (ontologi_concept for ontologi_concept in self.elastic_iterator()
                if ontologi_concept['term'] not in self.stoplist
                and self.misspelled_predicate(ontologi_concept))

    def init_keyword_processor(self):
        [self.keyword_processor.add_non_word_boundary(token) for token in list('åäöÅÄÖ()')]

    def init_ontology(self):
        for term_obj in self.get_ontologi_iterator():
            self.keyword_processor.add_keyword(term_obj['term'], term_obj)
            concept_preferred_label = term_obj['concept'].lower()
            if concept_preferred_label not in self.concept_to_term:
                self.concept_to_term[concept_preferred_label] = []
            self.concept_to_term[concept_preferred_label].append(term_obj)

    def get_keyword_processor(self):
        return self.keyword_processor

    def get_concepts(self, text, concept_type=None, span_info=False):
        concepts = self.keyword_processor.extract_keywords(text, span_info=span_info)
        if concept_type is not None:
            if span_info:
                concepts = list(filter(lambda concept: concept[0]['type'] == concept_type, concepts))
            else:
                concepts = list(filter(lambda concept: concept['type'] == concept_type, concepts))
        # print('Returning concepts', concepts)
        return concepts

    def elastic_iterator(self, maximum=None, query=None, _source=None, size=1000):
        if maximum:
            maximum = int(maximum)
        if query is None:
            elastic_query = {
                "query": {
                    "match_all": {}
                }
            }
        else:
            elastic_query = query

        # print(elastic_query)

        scan_result = scan(self.client, elastic_query, index=self.index, size=size, _source=_source)

        i = 0
        try:
            for row in scan_result:
                if i == maximum:
                    break
                i = i + 1
                yield row['_source']
        except ElasticsearchException as e:
            log.error("Failed to load ontology (%s)" % str(e))
