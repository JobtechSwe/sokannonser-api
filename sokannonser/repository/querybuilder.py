import json
import logging
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta
import elasticsearch_dsl
from dateutil import parser
from sokannonser import settings
from sokannonser.repository import taxonomy, TextToConcept
from sokannonser.rest.model import queries
from sokannonser.rest.model import fields as f

log = logging.getLogger(__name__)


class QueryBuilder(object):
    def __init__(self, text_to_concept=TextToConcept(ontologyhost=settings.ES_HOST,
                                                     ontologyport=settings.ES_PORT,
                                                     ontologyuser=settings.ES_USER,
                                                     ontologypwd=settings.ES_PWD)):
        self.ttc = text_to_concept
        self.occupation_collections = taxonomy.fetch_occupation_collections()

    def parse_args(self, args, x_fields=None):
        """
        Parse arguments for query and return an elastic query dsl

        Keyword arguments:
        args -- dictionary containing parameters from query
        """
        query_dsl = self._bootstrap_query(args, x_fields)

        # Check for empty query
        if not any(v is not None for v in args.values()) \
                or not args.get(settings.CONTEXTUAL_TYPEAHEAD, True):
            log.debug("Constructing match-all query")
            query_dsl['query']['bool']['must'].append({'match_all': {}})
            if 'sort' not in query_dsl:
                query_dsl['sort'] = [f.sort_options.get('pubdate-desc')]
            return query_dsl

        must_queries = list()

        must_queries.append(
            self._build_freetext_query(args.get(settings.FREETEXT_QUERY),
                                       args.get(settings.FREETEXT_FIELDS),
                                       args.get(settings.X_FEATURE_FREETEXT_BOOL_METHOD),
                                       args.get(settings.X_FEATURE_DISABLE_SMART_FREETEXT),
                                       args.get(settings.X_FEATURE_ENABLE_FALSE_NEGATIVE, False))
        )
        must_queries.append(self._build_employer_query(args.get(settings.EMPLOYER)))
        must_queries.append(self._build_yrkes_query(args.get(taxonomy.OCCUPATION),
                                                    args.get(taxonomy.GROUP),
                                                    args.get(taxonomy.FIELD)))
        must_queries.append(self.build_yrkessamlingar_query(args.get(taxonomy.COLLECTION)))
        must_queries.append(self._filter_timeframe(args.get(settings.PUBLISHED_AFTER),
                                                   args.get(settings.PUBLISHED_BEFORE)))
        must_queries.append(self._build_parttime_query(args.get(settings.PARTTIME_MIN),
                                                       args.get(settings.PARTTIME_MAX)))
        must_queries.append(self._build_plats_query(args.get(taxonomy.MUNICIPALITY),
                                                    args.get(taxonomy.REGION),
                                                    args.get(taxonomy.COUNTRY),
                                                    args.get(settings.UNSPECIFIED_SWEDEN_WORKPLACE),
                                                    args.get(settings.ABROAD)))
        must_queries.append(self._build_generic_query([f.MUST_HAVE_SKILLS + "." +
                                                       f.CONCEPT_ID + ".keyword",
                                                       f.MUST_HAVE_SKILLS + "." +
                                                       f.LEGACY_AMS_TAXONOMY_ID,
                                                       f.NICE_TO_HAVE_SKILLS + "." +
                                                       f.CONCEPT_ID + ".keyword",
                                                       f.NICE_TO_HAVE_SKILLS + "." +
                                                       f.LEGACY_AMS_TAXONOMY_ID],
                                                      args.get(taxonomy.SKILL)))
        must_queries.append(self._build_generic_query([f.MUST_HAVE_LANGUAGES + "." +
                                                       f.CONCEPT_ID + ".keyword",
                                                       f.MUST_HAVE_LANGUAGES + "." +
                                                       f.LEGACY_AMS_TAXONOMY_ID,
                                                       f.NICE_TO_HAVE_LANGUAGES + "." +
                                                       f.CONCEPT_ID + ".keyword",
                                                       f.NICE_TO_HAVE_LANGUAGES + "." +
                                                       f.LEGACY_AMS_TAXONOMY_ID],
                                                      args.get(taxonomy.LANGUAGE)))
        must_queries.append(self._build_generic_query([f.WORKING_HOURS_TYPE + "." +
                                                       f.CONCEPT_ID + ".keyword",
                                                       f.WORKING_HOURS_TYPE + "." +
                                                       f.LEGACY_AMS_TAXONOMY_ID],
                                                      args.get(taxonomy.WORKTIME_EXTENT)))
        must_queries.append(self._build_generic_query([f.DRIVING_LICENCE + "." +
                                                       f.CONCEPT_ID + ".keyword",
                                                       f.DRIVING_LICENCE + "." +
                                                       f.LEGACY_AMS_TAXONOMY_ID],
                                                      args.get(taxonomy.DRIVING_LICENCE)))
        must_queries.append(self._build_generic_query([f.EMPLOYMENT_TYPE + "." +
                                                       f.CONCEPT_ID + ".keyword",
                                                       f.EMPLOYMENT_TYPE + "." +
                                                       f.LEGACY_AMS_TAXONOMY_ID],
                                                      args.get(taxonomy.EMPLOYMENT_TYPE)))
        if args.get(taxonomy.DRIVING_LICENCE_REQUIRED) is not None:
            must_queries.append(
                {"term": {
                    f.DRIVING_LICENCE_REQUIRED:
                        args.get(taxonomy.DRIVING_LICENCE_REQUIRED)
                }}
            )

        # TODO: Maybe check if NO skills are listed in ad instead?
        if args.get(settings.EXPERIENCE_REQUIRED) == 'false':
            must_queries.append({"term": {f.EXPERIENCE_REQUIRED: False}})
        if args.get(settings.EXPERIENCE_REQUIRED) == 'true':
            must_queries.append({"term": {f.EXPERIENCE_REQUIRED: True}})

        filter_queries = list()
        geo_filter = self._build_geo_dist_filter(args.get(settings.POSITION),
                                                 args.get(settings.POSITION_RADIUS))
        filter_queries.append(geo_filter)

        query_dsl = self._assemble_queries(query_dsl, must_queries, filter_queries)

        for stat in args.get(settings.STATISTICS) or []:
            query_dsl['aggs'][stat] = {
                "terms": {
                    "field": f.stats_options[stat],
                    "size": args.get(settings.STAT_LMT) or 5
                }
            }
        return query_dsl

    @staticmethod
    def filter_aggs(aggs, freetext):
        # will not use in future
        fwords = freetext.split(' ') if freetext else []
        value_dicts = []
        for agg in aggs:
            if agg.startswith('complete_'):
                value_dicts += [{"type": agg[12:], **bucket}
                                for bucket in aggs[agg]['buckets']]
        filtered_aggs = []
        value_list = []
        for kv in sorted(value_dicts, key=lambda k: k['doc_count'], reverse=True):
            found_words = kv['key'].split(' ')
            value = ' '.join([w for w in found_words if w not in fwords])
            if kv['key'] not in fwords and value not in value_list:
                ac_hit = {
                    "value": value,
                    "found_phrase": kv['key'],
                    "type": kv['type'],
                    "occurrences": kv['doc_count']
                }
                value_list.append(value)
                filtered_aggs.append(ac_hit)

        if len(filtered_aggs) > 50:
            return filtered_aggs[0:50]
        return filtered_aggs

    def _parse_x_fields(self, x_fields):
        # Remove all spaces from field
        x_fields = re.sub(r'\s', '', x_fields).lower()
        if 'hits{' in x_fields:
            # Find out which fields are wanted
            hitsfields = self._find_hits_subelement(x_fields)
            # Remove lower nestings
            hitsfields = re.sub("[{].*?[}]", "", hitsfields)
            fieldslist = hitsfields.split(',')
            if f.AD_URL in fieldslist:
                fieldslist.append('id')

            return fieldslist
        return []

    @staticmethod
    def _find_hits_subelement(text):
        istart = []  # stack of indices of opening parentheses
        bracket_positions = {}
        for i, c in enumerate(text):
            if c == '{':
                istart.append(i)

            if c == '}':
                try:
                    bracket_positions[istart.pop()] = i
                except IndexError:
                    pass
        idx = text.find('hits{') + 4
        r = text[idx + 1:bracket_positions[idx]]
        return r

    def _bootstrap_query(self, args, x_fields):
        query_dsl = dict()
        query_dsl['from'] = args.pop(settings.OFFSET, 0)
        query_dsl['size'] = args.pop(settings.LIMIT, 10)
        # No need to track all results if used for typeahead
        if not args.get(settings.TYPEAHEAD_QUERY):
            query_dsl['track_total_hits'] = True
            query_dsl['track_scores'] = True

        if args.pop(settings.DETAILS, '') == queries.OPTIONS_BRIEF:
            query_dsl['_source'] = [f.ID, f.HEADLINE, f.APPLICATION_DEADLINE,
                                    f.EMPLOYMENT_TYPE + "." + f.LABEL,
                                    f.WORKING_HOURS_TYPE + "." + f.LABEL,
                                    f.EMPLOYER_NAME,
                                    f.PUBLICATION_DATE]

        if x_fields:
            query_dsl['_source'] = self._parse_x_fields(x_fields)

        # Remove api-key from args to make sure an empty query can occur
        if settings.APIKEY in args:
            args.pop(settings.APIKEY)

        # Make sure to only serve published ads
        offset = calculate_utc_offset()
        query_dsl['query'] = {
            'bool': {
                'must': [],
                'filter': [
                    {
                        'range': {
                            f.PUBLICATION_DATE: {
                                'lte': 'now+%dH/m' % offset
                            }
                        }
                    },
                    {
                        'range': {
                            f.LAST_PUBLICATION_DATE: {
                                'gte': 'now+%dH/m' % offset
                            }
                        }
                    },
                    {
                        'term': {
                            f.REMOVED: False
                        }
                    },
                ]
            },
        }
        query_dsl['aggs'] = {
            "positions": {
                "sum": {"field": f.NUMBER_OF_VACANCIES}
            }
        }
        complete_string = args.get(settings.TYPEAHEAD_QUERY)
        complete_fields = args.get(settings.FREETEXT_FIELDS)

        if not complete_fields:
            complete_fields = queries.QF_CHOICES.copy()
            complete_fields.remove('employer')

        complete_string = self._rewrite_word_for_regex(complete_string)
        word_list = complete_string.split(' ')
        complete = word_list[-1]

        ngrams_complete = []
        for n in list(range(len(word_list) - 1)):
            ngrams_complete.append(' '.join(word_list[n:]))

        size = 60 / len(complete_fields)

        enriched_typeahead_field = f.KEYWORDS_ENRICHED_SYNONYMS

        for field in complete_fields:
            base_field = f.KEYWORDS_EXTRACTED \
                if field in ['employer'] else enriched_typeahead_field

            query_dsl['aggs']["complete_00_%s" % field] = {
                "terms": {
                    "field": "%s.%s.raw" % (base_field, field),
                    "size": size,
                    "include": "%s.*" % self._escape_special_chars_for_complete(complete)
                }
            }
            x = 1
            for ngram in ngrams_complete:
                if ngram != complete:
                    query_dsl['aggs']["complete_%s_%s_remainder" % (str(x).zfill(2), field)] = {
                        "terms": {
                            "field": "%s.%s.raw" % (base_field, field),
                            "size": size,
                            "include": "%s.*" % self._escape_special_chars_for_complete(ngram)
                        }
                    }
                    x += 1
        if args.get(settings.SORT) and args.get(settings.SORT) in f.sort_options.keys():
            query_dsl['sort'] = f.sort_options.get(args.pop(settings.SORT))
        else:
            query_dsl['sort'] = f.sort_options.get('relevance')
        return query_dsl

    @staticmethod
    def _escape_special_chars_for_complete(inputstr):
        escaped_str = inputstr
        chars_to_escape = ['#']

        for char in chars_to_escape:
            if char in inputstr:
                escaped_str = inputstr.replace(char, '[%s]' % char)
        return escaped_str

    @staticmethod
    def _assemble_queries(query_dsl, additional_queries, additional_filters):
        for query in additional_queries:
            if query:
                query_dsl['query']['bool']['must'].append(query)
        for af in additional_filters:
            if af:
                query_dsl['query']['bool']['filter'].append(af)
        return query_dsl

    @staticmethod
    def _rewrite_word_for_regex(word):
        if word is None:
            word = ''
        bad_chars = ['+', '.', '[', ']', '{', '}', '(', ')', '^', '$',
                     '*', '\\', '|', '?', '"', '\'', '&', '<', '>']
        if any(c in bad_chars for c in word):
            modded_term = ''
            for c in word:
                if c in bad_chars:
                    modded_term += '\\'
                modded_term += c
            return modded_term
        return word

    @staticmethod
    def extract_quoted_phrases(text):
        # Append quote to end of string if unbalanced
        if text.count('"') % 2 != 0:
            text += '"'
        must_matches = re.findall(r'\+\"(.+?)\"', text)
        neg_matches = re.findall(r'\-\"(.+?)\"', text)
        for neg_match in neg_matches:
            text = re.sub('-"%s"' % neg_match, '', text)
        for must_match in must_matches:
            text = re.sub(r'\+"%s"' % must_match, '', text)
        matches = re.findall(r'\"(.+?)\"', text)
        for match in matches:
            text = re.sub('"%s"' % match, '', text)
        return {"phrases": matches, "phrases_must": must_matches,
                "phrases_must_not": neg_matches}, text.strip()

    @staticmethod
    def _remove_unwanted_chars_from_querystring(querystring):
        return ' '.join([w.strip(',.!?:; ') for w in re.split('\\s|\\,', querystring)])

    # Parses FREETEXT_QUERY and FREETEXT_FIELDS
    def _build_freetext_query(self, querystring, queryfields, freetext_bool_method,
                              disable_smart_freetext, enable_false_negative=False):
        if not querystring:
            return None
        if not queryfields:
            queryfields = queries.QF_CHOICES.copy()
        querystring = self._remove_unwanted_chars_from_querystring(querystring)
        original_querystring = querystring
        (phrases, querystring) = self.extract_quoted_phrases(querystring)
        concepts = {} if disable_smart_freetext else self.ttc.text_to_concepts(querystring)
        querystring = self._rewrite_querystring(querystring, concepts)
        ft_query = self._create_base_ft_query(querystring, freetext_bool_method)

        # Make all "musts" concepts "shoulds" as well
        for qf in queryfields:
            if qf in concepts:
                must_key = "%s_must" % qf
                concepts[qf] += [c for c in concepts.get(must_key, [])]
        # Add concepts to query
        for concept_type in queryfields:
            sub_should = self._freetext_concepts({"bool": {}}, concepts,
                                                 [concept_type], "should", enable_false_negative)
            if 'should' in sub_should['bool']:
                if 'must' not in ft_query['bool']:
                    ft_query['bool']['must'] = []
                ft_query['bool']['must'].append(sub_should)
        # Remove unwanted concepts from query
        self._freetext_concepts(ft_query, concepts, queryfields, 'must_not', enable_false_negative)
        # Require musts
        self._freetext_concepts(ft_query, concepts, queryfields, 'must', enable_false_negative)
        self._add_phrases_query(ft_query, phrases)
        ft_query = self._freetext_headline(ft_query, original_querystring)
        return ft_query

    # Add phrase queries
    @staticmethod
    def _add_phrases_query(ft_query, phrases):
        for bool_type in ['should', 'must', 'must_not']:
            key = 'phrases' if bool_type == 'should' else "phrases_%s" % bool_type

            for phrase in phrases[key]:
                if bool_type not in ft_query['bool']:
                    ft_query['bool'][bool_type] = []
                ft_query['bool'][bool_type].append({"multi_match":
                                                        {"query": phrase,
                                                         "fields": ["headline", "description.text"],
                                                         "type": "phrase"}})

        return ft_query

    # Removes identified concepts from querystring
    def _rewrite_querystring(self, querystring, concepts):
        # Sort all concepts by string length
        all_concepts = sorted(concepts.get('occupation', []) +
                              concepts.get('occupation_must', []) +
                              concepts.get('occupation_must_not', []) +
                              concepts.get('skill', []) +
                              concepts.get('skill_must', []) +
                              concepts.get('skill_must_not', []) +
                              concepts.get('location', []) +
                              concepts.get('location_must', []) +
                              concepts.get('location_must_not', []),
                              key=lambda c: len(c),
                              reverse=True)
        # Remove found concepts from querystring
        for term in [concept['term'] for concept in all_concepts]:
            term = self._rewrite_word_for_regex(term)
            p = re.compile(f'(^|\\s+)(\\+{term}|\\-{term}|{term})(\\s+|$)')
            querystring = p.sub('\\1\\3', querystring).strip()
        # Remove duplicate spaces
        querystring = re.sub('\\s+', ' ', querystring).strip()
        return querystring

    def _create_base_ft_query(self, querystring, method):
        method = 'and' if method == 'and' else settings.DEFAULT_FREETEXT_BOOL_METHOD
        # Creates a base query dict for "independent" freetext words
        # (e.g. words not found in text_to_concepts)
        suffix_words = ' '.join([w[1:] for w in querystring.split(' ')
                                 if w.startswith('*')])
        prefix_words = ' '.join([w[:-1] for w in querystring.split(' ')
                                 if w and w.endswith('*')])
        inc_words = ' '.join([w for w in querystring.split(' ')
                              if w and not w.startswith('+')
                              and not w.startswith('-') and not w.startswith('*')
                              and not w.endswith('*')])
        req_words = ' '.join([w[1:] for w in querystring.split(' ')
                              if w.startswith('+')
                              and w[1:].strip()])
        exc_words = ' '.join([w[1:] for w in querystring.split(' ')
                              if w.startswith('-')
                              and w[1:].strip()])
        shoulds = self._freetext_fields(inc_words, method) if inc_words else []
        musts = self._freetext_fields(req_words, method) if req_words else []
        mustnts = self._freetext_fields(exc_words, method) if exc_words else []

        ft_query = {"bool": {}}
        # Add "common" words to query
        if shoulds or musts or prefix_words or suffix_words:
            ft_query['bool']['must'] = []
        if shoulds:
            # Include all "must" words in should, to make sure any single "should"-word
            # not becomes exclusive
            if 'must' not in ft_query['bool']:
                ft_query['bool']['must'] = []
            ft_query['bool']['must'].append({"bool": {"should": shoulds + musts}})
        # Wildcards after shoulds so they dont end up there
        if prefix_words:
            musts += self._freetext_wildcard(prefix_words, "prefix", method)
        if suffix_words:
            musts += self._freetext_wildcard(suffix_words, "suffix", method)
        if musts:
            ft_query['bool']['must'].append({"bool": {"must": musts}})
        if mustnts:
            ft_query['bool']['must_not'] = mustnts
        return ft_query

    @staticmethod
    def _freetext_fields(searchword, method=settings.DEFAULT_FREETEXT_BOOL_METHOD):
        return [{
            "multi_match": {
                "query": searchword,
                "type": "cross_fields",
                "operator": method,
                "fields": [f.HEADLINE + "^3", f.KEYWORDS_EXTRACTED + ".employer^2",
                           f.DESCRIPTION_TEXT, f.ID, f.EXTERNAL_ID, f.SOURCE_TYPE,
                           f.KEYWORDS_EXTRACTED + ".location^5"]
            }
        }]

    @staticmethod
    def _freetext_wildcard(searchword, wildcard_side, method=settings.DEFAULT_FREETEXT_BOOL_METHOD):
        return [{
            "multi_match": {
                "query": searchword,
                "type": "cross_fields",
                "operator": method,
                "fields": [f.HEADLINE + "." + wildcard_side, f.DESCRIPTION_TEXT + "." + wildcard_side]
            }
        }]

    @staticmethod
    def _freetext_headline(query_dict, querystring):
        # Remove plus and minus from querystring for headline search
        querystring = re.sub(r'(^| )[\\+]{1}', ' ', querystring)
        querystring = ' '.join([word for word in querystring.split(' ')
                                if not word.startswith('-') and not word.startswith('*') and not word.endswith('*')])
        if 'must' not in query_dict['bool']:
            query_dict['bool']['must'] = []

        for should in query_dict['bool']['must']:
            try:
                should['bool']['should'].append(
                    {
                        "match": {
                            f.HEADLINE + ".words": {
                                "query": querystring.strip(),
                                "operator": "and",
                                "boost": 5
                            }
                        }
                    })
            except KeyError:
                log.error("No bool clause for headline query")

        return query_dict

    def _freetext_concepts(self, query_dict, concepts,
                           concept_keys, bool_type, enable_false_negative=False):
        for key in concept_keys:
            dict_key = "%s_%s" % (key, bool_type) if bool_type != 'should' else key
            current_concepts = [c for c in concepts.get(dict_key, []) if c]
            for concept in current_concepts:
                if bool_type not in query_dict['bool']:
                    query_dict['bool'][bool_type] = []

                base_fields = []
                if key == 'location' and bool_type != 'must':
                    base_fields.append(f.KEYWORDS_EXTRACTED)
                    base_fields.append(f.KEYWORDS_ENRICHED)
                    # Add freetext search for location that does not exist
                    # in extracted locations, for example 'kallhäll'.
                    value = concept['term'].lower()
                    if value not in self.ttc.ontology.extracted_locations:
                        geo_ft_query = self._freetext_fields(value)
                        query_dict['bool'][bool_type].append(geo_ft_query[0])
                elif key == 'occupation' and bool_type != 'must':
                    base_fields.append(f.KEYWORDS_EXTRACTED)
                    base_fields.append(f.KEYWORDS_ENRICHED)
                else:
                    curr_base_field = f.KEYWORDS_EXTRACTED \
                        if key in ['employer'] else f.KEYWORDS_ENRICHED
                    base_fields.append(curr_base_field)

                for base_field in base_fields:
                    if base_field == f.KEYWORDS_EXTRACTED:
                        value = concept['term'].lower()
                        boost_value = 10
                    else:
                        value = concept['concept'].lower()
                        boost_value = 9

                    field = "%s.%s.raw" % (base_field, key)
                    query_dict['bool'][bool_type].append(
                        {
                            "term": {
                                field: {
                                    "value": value,
                                    "boost": boost_value
                                }
                            }
                        }
                    )
                    if enable_false_negative and base_field == f.KEYWORDS_ENRICHED and (key == 'skill'):
                        # Add extra search for the current known term in headline, employer and description to be sure
                        # not to miss search hits where the term wasn't identified during enrichment. Only search
                        # skills to avoid irrelevant hits on occupations and locations...
                        query_dict['bool'][bool_type].append(
                            {'multi_match': {
                                'query': concept['term'].lower(),
                                'type': 'cross_fields',
                                'operator': 'and',
                                'fields': [
                                    'headline^0.1',
                                    'keywords.extracted.employer^0.1',
                                    'description.text^0.1'
                                ]
                            }}
                        )
        return query_dict

    # Parses EMPLOYER
    @staticmethod
    def _build_employer_query(employers):
        if employers:
            bool_segment = {"bool": {"should": [], "must_not": [], "must": []}}
            for employer in employers:
                negative_search = employer.startswith('-')
                positive_search = employer.startswith('+')
                bool_type = 'should'
                if negative_search or positive_search:
                    employer = employer[1:]
                    bool_type = 'must_not' if negative_search else 'must'
                if employer.isdigit():
                    bool_segment['bool'][bool_type].append(
                        {"prefix": {f.EMPLOYER_ORGANIZATION_NUMBER: employer}}
                    )
                else:
                    bool_segment['bool'][bool_type].append(
                        {
                            "multi_match": {
                                "query": " ".join(employers),
                                "operator": "or",
                                "fields": [f.EMPLOYER_NAME,
                                           f.EMPLOYER_WORKPLACE]
                            }
                        }
                    )
            return bool_segment
        return None

    # Parses OCCUPATION, FIELD, GROUP and COLLECTIONS
    @staticmethod
    def _build_yrkes_query(yrkesroller, yrkesgrupper, yrkesomraden):
        yrken = yrkesroller or []
        yrkesgrupper = yrkesgrupper or []
        yrkesomraden = yrkesomraden or []

        yrke_term_query = [{
            "term": {
                f.OCCUPATION + "." + f.CONCEPT_ID + ".keyword": {
                    "value": y,
                    "boost": 2.0}}} for y in yrken if y and not y.startswith('-')]
        yrke_term_query += [{
            "term": {
                f.OCCUPATION + "." + f.LEGACY_AMS_TAXONOMY_ID: {
                    "value": y,
                    "boost": 2.0}}} for y in yrken if y and not y.startswith('-')]
        yrke_term_query += [{
            "term": {
                f.OCCUPATION_GROUP + "." + f.CONCEPT_ID + ".keyword": {
                    "value": y,
                    "boost": 1.0}}} for y in yrkesgrupper if y and not y.startswith('-')]
        yrke_term_query += [{
            "term": {
                f.OCCUPATION_GROUP + "." + f.LEGACY_AMS_TAXONOMY_ID: {
                    "value": y,
                    "boost": 1.0}}} for y in yrkesgrupper if y and not y.startswith('-')]
        yrke_term_query += [{
            "term": {
                f.OCCUPATION_FIELD + "." + f.CONCEPT_ID + ".keyword": {
                    "value": y,
                    "boost": 1.0}}} for y in yrkesomraden if y and not y.startswith('-')]
        yrke_term_query += [{
            "term": {
                f.OCCUPATION_FIELD + "." + f.LEGACY_AMS_TAXONOMY_ID: {
                    "value": y,
                    "boost": 1.0}}} for y in yrkesomraden if y and not y.startswith('-')]
        neg_yrke_term_query = [{
            "term": {
                f.OCCUPATION + "." + f.CONCEPT_ID + ".keyword": {
                    "value": y[1:]}}} for y in yrken if y and y.startswith('-')]
        neg_yrke_term_query += [{
            "term": {
                f.OCCUPATION + "." + f.LEGACY_AMS_TAXONOMY_ID: {
                    "value": y[1:]}}} for y in yrken if y and y.startswith('-')]
        neg_yrke_term_query += [{
            "term": {
                f.OCCUPATION_GROUP + "." + f.CONCEPT_ID + ".keyword": {
                    "value": y[1:]}}} for y in yrkesgrupper if y and y.startswith('-')]
        neg_yrke_term_query += [{
            "term": {
                f.OCCUPATION_GROUP + "." + f.LEGACY_AMS_TAXONOMY_ID: {
                    "value": y[1:]}}} for y in yrkesgrupper if y and y.startswith('-')]
        neg_yrke_term_query += [{
            "term": {
                f.OCCUPATION_FIELD + "." + f.CONCEPT_ID + ".keyword": {
                    "value": y[1:]}}} for y in yrkesomraden if y and y.startswith('-')]
        neg_yrke_term_query += [{
            "term": {
                f.OCCUPATION_FIELD + "." + f.LEGACY_AMS_TAXONOMY_ID: {
                    "value": y[1:]}}} for y in yrkesomraden if y and y.startswith('-')]

        if yrke_term_query or neg_yrke_term_query:
            query = {'bool': {}}
            if yrke_term_query:
                query['bool']['should'] = yrke_term_query
            if neg_yrke_term_query:
                query['bool']['must_not'] = neg_yrke_term_query
            return query

        else:
            return None

    # Parses OCCUPATION, FIELD, GROUP and COLLECTIONS
    def build_yrkessamlingar_query(self, yrkessamlingar):
        start_time = int(time.time() * 1000)
        if not yrkessamlingar:
            return None

        yrken_in_yrkessamlingar_id = []
        neg_yrken_in_yrkessamlingar_id = []
        # Parse yrkessamlingar from search input and add the occupations that is included to yrken_in_yrkessamlingar_id...
        for yrkessamling in yrkessamlingar:
            if yrkessamling:
                # If negative filter on yrkessamling:
                if str(yrkessamling).startswith('-'):
                    neg_yrkessamling = yrkessamling[1:]
                    if neg_yrkessamling in self.occupation_collections:
                        neg_yrken_in_yrkessamlingar_id += self.occupation_collections.get(neg_yrkessamling)
                # If positive filter on yrkessamling:
                else:
                    if yrkessamling in self.occupation_collections:
                        yrken_in_yrkessamlingar_id += self.occupation_collections.get(yrkessamling)
        if yrken_in_yrkessamlingar_id or neg_yrken_in_yrkessamlingar_id:
            query = {'bool': {}}
            if yrken_in_yrkessamlingar_id:
                query['bool']['should'] = {
                    "terms": {
                        f.OCCUPATION + "." + f.CONCEPT_ID + ".keyword":
                            yrken_in_yrkessamlingar_id}
                }
            if neg_yrken_in_yrkessamlingar_id:
                query['bool']['must_not'] = {
                    "terms": {
                        f.OCCUPATION + "." + f.CONCEPT_ID + ".keyword":
                            neg_yrken_in_yrkessamlingar_id}
                }
            log.debug("Occupation-collections Query results after %d milliseconds."
                      % (int(time.time() * 1000) - start_time))
            return query
        else:
            return None

    # Parses MUNICIPALITY and REGION
    @staticmethod
    def _build_plats_query(kommunkoder, lanskoder, landskoder, unspecify, abroad):
        kommuner = []
        neg_komm = []
        lan = []
        neg_lan = []
        land = []
        neg_land = []
        for kkod in kommunkoder if kommunkoder else []:
            if kkod.startswith('-'):
                neg_komm.append(kkod[1:])
            else:
                kommuner.append(kkod)
        for lkod in lanskoder if lanskoder else []:
            if lkod.startswith('-'):
                neg_lan.append(lkod[1:])
            else:
                lan.append(lkod)
        for ckod in landskoder if landskoder else []:
            if ckod.startswith('-'):
                neg_land.append(ckod[1:])
            else:
                land.append(ckod)

        plats_term_query = [{"term": {
            f.WORKPLACE_ADDRESS_MUNICIPALITY_CODE: {
                "value": kkod, "boost": 2.0}}} for kkod in kommuner]
        plats_term_query += [{"term": {
            f.WORKPLACE_ADDRESS_MUNICIPALITY_CONCEPT_ID: {
                "value": kkod, "boost": 2.0}}} for kkod in kommuner]

        # Add unspecified field, when it is true, system will return all adds with unspecified in sweden.
        if unspecify:
            plats_term_query += [
                {
                    "bool": {
                        "filter": {"term": {f.WORKPLACE_ADDRESS_COUNTRY_CONCEPT_ID: {
                            "value": settings.SWEDEN_CONCEPT_ID}}},
                        "must_not": {"exists": {"field": f.WORKPLACE_ADDRESS_REGION_CONCEPT_ID}},
                        "boost": 1.0
                    }
                },
            ]

        if abroad:
            plats_term_query += [
                {
                    "bool": {
                        "must_not": {"term": {f.WORKPLACE_ADDRESS_COUNTRY_CONCEPT_ID: {
                            "value": settings.SWEDEN_CONCEPT_ID}}},
                        "boost": 1.0
                    }
                },
            ]

        plats_term_query += [{"term": {
            f.WORKPLACE_ADDRESS_REGION_CODE: {
                "value": lkod, "boost": 1.0}}} for lkod in lan]
        plats_term_query += [{"term": {
            f.WORKPLACE_ADDRESS_REGION_CONCEPT_ID: {
                "value": lkod, "boost": 1.0}}} for lkod in lan]

        plats_term_query += [{"term": {
            f.WORKPLACE_ADDRESS_COUNTRY_CODE: {
                "value": ckod, "boost": 1.0}}} for ckod in land]
        plats_term_query += [{"term": {
            f.WORKPLACE_ADDRESS_COUNTRY_CONCEPT_ID: {
                "value": ckod, "boost": 1.0}}} for ckod in land]

        plats_bool_query = {"bool": {
            "should": plats_term_query}
        } if plats_term_query else {}
        neg_komm_term_query = []
        neg_lan_term_query = []
        neg_land_term_query = []
        if neg_komm:
            neg_komm_term_query = [{"term": {
                f.WORKPLACE_ADDRESS_MUNICIPALITY_CODE: {
                    "value": kkod}}} for kkod in neg_komm]
            neg_komm_term_query += [{"term": {
                f.WORKPLACE_ADDRESS_MUNICIPALITY_CONCEPT_ID: {
                    "value": kkod}}} for kkod in neg_komm]
        if neg_lan:
            neg_lan_term_query = [{"term": {
                f.WORKPLACE_ADDRESS_REGION_CODE: {
                    "value": lkod}}} for lkod in neg_lan]
            neg_lan_term_query += [{"term": {
                f.WORKPLACE_ADDRESS_REGION_CONCEPT_ID: {
                    "value": lkod}}} for lkod in neg_lan]

        if neg_land:
            neg_land_term_query = [{"term": {
                f.WORKPLACE_ADDRESS_COUNTRY_CODE: {
                    "value": ckod}}} for ckod in neg_land]
            neg_land_term_query += [{"term": {
                f.WORKPLACE_ADDRESS_COUNTRY_CONCEPT_ID: {
                    "value": ckod}}} for ckod in neg_land]

        if neg_komm_term_query or neg_lan_term_query or neg_land_term_query:
            if 'bool' not in plats_bool_query:
                plats_bool_query['bool'] = {}
            plats_bool_query['bool']['must_not'] = neg_komm_term_query + neg_lan_term_query + neg_land_term_query

        return plats_bool_query

    # Parses PUBLISHED_AFTER and PUBLISHED_BEFORE
    @staticmethod
    def _filter_timeframe(from_datestring, to_datetime):
        if not from_datestring and not to_datetime:
            return None
        range_query = {"range": {f.PUBLICATION_DATE: {}}}
        from_datetime = None
        if from_datestring and re.match(r'^\d+$', from_datestring):
            now = datetime.now()
            from_datetime = now - timedelta(minutes=int(from_datestring))
        elif from_datestring:
            # from_datetime = datetime.strptime(from_datestring, '%Y-%m-%dT%H:%M:%S')
            from_datetime = parser.parse(from_datestring)
        if from_datetime:
            log.debug("Filter ads from %s" % from_datetime)
            range_query['range'][f.PUBLICATION_DATE]['gte'] = from_datetime.isoformat()
        if to_datetime:
            range_query['range'][f.PUBLICATION_DATE]['lte'] = to_datetime.isoformat()
        return range_query

    # Parses PARTTIME_MIN and PARTTIME_MAX
    @staticmethod
    def _build_parttime_query(parttime_min, parttime_max):
        if not parttime_min and not parttime_max:
            return None
        if not parttime_min:
            parttime_min = 0.0
        if not parttime_max:
            parttime_max = 100.0
        parttime_query = {
            "bool": {
                "must": [
                    {
                        "range": {
                            f.SCOPE_OF_WORK_MIN: {
                                "lte": parttime_max,
                                "gte": parttime_min
                            },
                        }
                    },
                    {
                        "range": {
                            f.SCOPE_OF_WORK_MAX: {
                                "lte": parttime_max,
                                "gte": parttime_min
                            }
                        }
                    }
                ]
            }
        }
        return parttime_query

    @staticmethod
    def _build_generic_query(keys, itemlist):
        items = [] if not itemlist else itemlist
        term_query = []
        neg_term_query = []
        if isinstance(keys, str):
            keys = [keys]
        for key in keys:
            term_query += [{"term": {key: {"value": item}}}
                           for item in items if not item.startswith('-')]

            neg_term_query += [{"term": {key: {"value": item[1:]}}}
                               for item in items if item.startswith('-')]

        if term_query or neg_term_query:
            query = {'bool': {}}
            if term_query:
                query['bool']['should'] = term_query
            if neg_term_query:
                query['bool']['must_not'] = neg_term_query
            return query

        return None

    # Parses POSITION and POSITION_RADIUS
    @staticmethod
    def _build_geo_dist_filter(positions, coordinate_ranges):
        geo_bool = {"bool": {"should": []}} if positions else {}
        for index, position in enumerate(positions or []):
            latitude = None
            longitude = None
            coordinate_range = coordinate_ranges[index] \
                if coordinate_ranges is not None and index < len(coordinate_ranges) \
                else settings.DEFAULT_POSITION_RADIUS
            if position and ',' in position:
                try:
                    latitude = float(re.split(', ?', position)[0])
                    longitude = float(re.split(', ?', position)[1])
                except ValueError as e:
                    log.info("Bad position-parameter: \"%s\" (%s)" % (position, str(e)))

            geo_filter = {}
            if not latitude or not longitude or not coordinate_range:
                return {}
            elif ((-90 <= latitude <= 90)
                  and (-180 <= longitude <= 180) and (coordinate_range > 0)):
                geo_filter["geo_distance"] = {
                    "distance": str(coordinate_range) + "km",
                    # OBS! order in REST request: latitude,longitude
                    f.WORKPLACE_ADDRESS_COORDINATES: [longitude, latitude]
                }
            if geo_filter:
                geo_bool['bool']['should'].append(geo_filter)
        return geo_bool

    @staticmethod
    def create_auto_complete_suggester(word):
        """"
        parse args and create auto complete suggester
        """
        enriched_typeahead_field = f.KEYWORDS_ENRICHED_SYNONYMS

        fields = ['compound', ]
        search = elasticsearch_dsl.Search()
        search = search.source('suggest')
        for field in fields:
            search = search.suggest(
                '%s-suggest' % field,
                word,
                completion={
                    'field': '%s.%s.suggest' % (enriched_typeahead_field, field),
                    "skip_duplicates": True,
                    "size": 50,
                    "fuzzy": {
                        "min_length": 3,
                        "prefix_length": 0
                    }
                }
            )
        return search.to_dict()

    @staticmethod
    def create_phrase_suggester(input_words):
        """"
        parse args and create phrase suggester
        """
        enriched_typeahead_field = f.KEYWORDS_ENRICHED_SYNONYMS

        field = '%s.compound' % enriched_typeahead_field
        search = elasticsearch_dsl.Search()
        search = search.source('suggest')
        search = search.suggest(
            '%s_simple_phrase' % field,
            input_words,
            phrase={
                'field': '%s.trigram' % field,
                'size': 10,
                'max_errors': 2,
                'direct_generator': [{
                    'field': '%s.trigram' % field,
                    'suggest_mode': 'always',
                    'min_word_length': 1
                }, {
                    'field': '%s.reverse' % field,
                    'suggest_mode': 'always',
                    'pre_filter': 'reverse',
                    'post_filter': 'reverse',
                    'min_word_length': 1
                }]
            }
        )
        return search.to_dict()

    @staticmethod
    def create_suggest_search(suggest):
        enriched_typeahead_field = f.KEYWORDS_ENRICHED_SYNONYMS

        field = '%s.compound' % enriched_typeahead_field
        search = defaultdict(dict)
        query = search.setdefault('query', {})
        match = query.setdefault('match', {})
        field = match.setdefault(field, {})
        field['query'] = suggest
        field['operator'] = 'and'

        return json.dumps(search)

    @staticmethod
    def create_check_search_word_type_query(word):
        """"
            Create check search word type query
        """
        enriched_typeahead_field = f.KEYWORDS_ENRICHED_SYNONYMS
        search = defaultdict(dict)
        aggs = search.setdefault('aggs', {})
        for field in ('location', 'skill', 'occupation'):
            aggs['search_type_%s' % field] = {
                'terms': {
                    'field': '%s.%s.raw' % (enriched_typeahead_field, field),
                    'include': word
                }
            }
        return json.dumps(search)

    @staticmethod
    def create_suggest_extra_word_query(word, first_word_type, second_word_type):
        """"
           Create suggest extra word query
        """
        enriched_typeahead_field = f.KEYWORDS_ENRICHED_SYNONYMS
        search = defaultdict(dict)
        aggs = search.setdefault('aggs', {})
        first_word = aggs.setdefault('first_word', {})
        first_word['filter'] = {
            'term': {
                '%s.%s.raw' % (enriched_typeahead_field, first_word_type): word,
            }
        }
        first_word['aggs'] = {
            'second_word': {
                'terms': {
                    'field': '%s.%s.raw' % (enriched_typeahead_field, second_word_type),
                    'size': 6
                }
            }
        }
        return json.dumps(search)


def calculate_utc_offset():
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = - (time.altzone if is_dst else time.timezone)
    return int(utc_offset / 3600) if utc_offset > 0 else 0
