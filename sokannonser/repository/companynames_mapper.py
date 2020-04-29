import logging
import os
import math
from flashtext.keyword import KeywordProcessor
from sokannonser.repository import elastic
from sokannonser import settings

log = logging.getLogger(__name__)

currentdir = os.path.dirname(os.path.realpath(__file__)) + '/'


class CompanynamesMapper(object):

    def __init__(self, companynames_from_file=False, companynames_filepath=None):
        self.companynames_from_file = companynames_from_file
        self.companynames_filepath = companynames_filepath

        self.concept_to_term = {}
        self.keyword_processor = KeywordProcessor()
        self._init_keyword_processor(self.keyword_processor)
        self._init_companynames(self.keyword_processor)

    def _get_partial_to_companynames_mappings(self):
        """
        # "ikea" --> "ikea ab"
        # "ikea ab" --> "ikea ab"
        # "Volvo Car" --> "volvo car mobility ab", "volvo car retail solutions ab"
        # "Banan-Kompaniet" --> "ab banan-kompaniet"
        :return: Mappings between partial companyname to original variants of the complete name.
        """
        companylist = self.load_all_companynames()

        companies_mappings = dict()

        for name in companylist:
            original_name = name.strip()
            original_name_lower = original_name.lower()
            name_parts = original_name_lower.split(' ')
            len_parts = len(name_parts)

            partial_company_name = ''

            if len(name_parts) == 1 or len(name_parts) == 2 and original_name_lower.endswith(' ab'):
                partial_company_name = name_parts[0].strip()
                self.map_partial_to_company(companies_mappings, original_name_lower, partial_company_name)
            elif len(name_parts) == 2 and original_name_lower.startswith('ab '):
                partial_company_name = name_parts[1].strip()
                self.map_partial_to_company(companies_mappings, original_name_lower, partial_company_name)
            else:
                for i in range(len_parts):
                    clean_part = name_parts[i].strip()

                    if clean_part != '':
                        partial_company_name = partial_company_name + ' ' + clean_part
                        partial_company_name = partial_company_name.strip()

                        if i > 0:
                            # Don't add single word if companyname consist of more words than 1.
                            self.map_partial_to_company(companies_mappings, original_name_lower, partial_company_name)

        return companies_mappings

    def map_partial_to_company(self, companies_mappings, original_name_lower, partial_company_name):
        if partial_company_name not in companies_mappings:
            companies_mappings[partial_company_name] = []
        if original_name_lower not in companies_mappings[partial_company_name]:
            log.debug('Mapping %s to %s' % (partial_company_name, original_name_lower))
            companies_mappings[partial_company_name].append(original_name_lower)

    def company_name_iterator(self, max_size=100 ** 100):

        # companyname_field = "arbetsgivarenamn.keyword"
        # es_index = 'platsannonser_gdpr_behandlade'
        companyname_field = "employer.name.keyword"
        es_index = settings.ES_INDEX

        query_unique_names = {
            "size": 0,
            "aggs": {
                "names_count": {
                    "cardinality": {
                        "field": companyname_field
                    }
                }
            }
        }

        unique_res = elastic.search(index=es_index, body=query_unique_names)

        unique_amount = int(unique_res['aggregations']['names_count']['value'])

        batch_size = 1000
        num_partitions = int(math.ceil(unique_amount / batch_size))

        aggs_query = {
            "size": 0,
            "aggs": {
                "names_agg": {
                    "terms": {
                        "field": companyname_field,
                        "include": {
                            "partition": 0,
                            "num_partitions": num_partitions
                        },
                        "size": batch_size
                    }
                }
            }
        }

        i = 0
        for partition_counter in range(num_partitions):
            aggs_query['aggs']['names_agg']['terms']['include']['partition'] = partition_counter
            res = elastic.search(index=es_index, body=aggs_query)

            for bucket in res['aggregations']['names_agg']['buckets']:
                if i == max_size:
                    break
                i = i + 1
                yield bucket['key']

    def load_companynames_from_elastic(self):
        elastic_companynames = set()
        for name in self.company_name_iterator():
            elastic_companynames.add(name)
        log.debug('Loaded %s companynames from Elastic' % len(elastic_companynames))
        return sorted(list(elastic_companynames))

    def _load_companynames_from_file(self, filepath):
        with open(filepath, encoding='utf-8') as f:
            company_list = f.read().splitlines()
        return company_list

    def load_companynames_from_file(self):
        companylist = self._load_companynames_from_file(self.companynames_filepath)
        log.debug('Loaded %s companynames from file' % len(companylist))
        return companylist

    def load_all_companynames(self):

        if self.companynames_from_file and self.companynames_filepath:
            companylist = self.load_companynames_from_file()
        else:
            companylist = self.load_companynames_from_elastic()

        return companylist

    def _init_companynames(self, keyword_processor):
        for key, term_obj_list in self._get_partial_to_companynames_mappings().items():
            keyword_processor.add_keyword(key, term_obj_list)

    @staticmethod
    def _init_keyword_processor(keyword_processor):
        [keyword_processor.add_non_word_boundary(token) for token in list('åäöÅÄÖüÜ()-')]

    def _get_keyword_processor(self):
        return self.keyword_processor

    def extract_companynames(self, text, span_info=False):
        concepts = self._get_keyword_processor().extract_keywords(text,
                                                                  span_info=span_info)
        companylist = []
        for sublist in concepts:
            for item in sublist:
                companylist.append(item)

        return companylist
