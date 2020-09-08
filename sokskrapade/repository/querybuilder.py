import logging
import re

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

    def parse_args(self, args):
        query_dsl = self._bootstrap_query(args)
        must_queries = list()

        must_queries.append(
            self._build_freetext_query(args.get(settings.FREETEXT_QUERY),
                                       args.get(settings.FREETEXT_FIELDS))
        )
        must_queries.append(self._build_yrkes_query(args.get(taxonomy.OCCUPATION),
                                                    args.get(taxonomy.GROUP),
                                                    args.get(taxonomy.FIELD)))
        must_queries.append(self._build_plats_query(args.get(taxonomy.MUNICIPALITY),
                                                    args.get(taxonomy.REGION),
                                                    args.get(taxonomy.COUNTRY)))

        query_dsl = self._assemble_queries(query_dsl, must_queries)
        return query_dsl

    def _bootstrap_query(self, args):
        query_dsl = dict()
        query_dsl['size'] = args.pop(settings.LIMIT, 10)
        query_dsl['query'] = {
            "bool": {
                "must": []
            },
        }
        return query_dsl

    def _assemble_queries(self, query_dsl, additional_queries):
        for query in additional_queries:
            if query:
                query_dsl['query']['bool']['must'].append(query)
        return query_dsl

    def _rewrite_word_for_regex(self, word):
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

    def extract_quoted_phrases(self, text):
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

    def _build_freetext_query(self, querystring, queryfields):
        if not querystring:
            return None
        if not queryfields:
            queryfields = queries.QF_CHOICES.copy()
        querystring = ' '.join([w.strip(',.!?:; ') for w in re.split('\\s|\\,', querystring)])
        original_querystring = querystring
        (phrases, querystring) = self.extract_quoted_phrases(querystring)
        concepts = self.ttc.text_to_concepts(querystring)
        querystring = self._rewrite_querystring(querystring, concepts)
        ft_query = self._create_base_ft_query(querystring)

        # Make all "musts" concepts "shoulds" as well
        for qf in queryfields:
            if qf in concepts:
                must_key = "%s_must" % qf
                concepts[qf] += [c for c in concepts.get(must_key, [])]

        for concept_type in queryfields:
            sub_should = self._freetext_concepts({"bool": {}}, concepts,
                                                 querystring, [concept_type], "should")
            if 'should' in sub_should['bool']:
                if 'must' not in ft_query['bool']:
                    ft_query['bool']['must'] = []
                ft_query['bool']['must'].append(sub_should)
        self._freetext_concepts(ft_query, concepts, querystring, queryfields, 'must_not')
        self._freetext_concepts(ft_query, concepts, querystring, queryfields, 'must')
        self._add_phrases_query(ft_query, phrases)

        ft_query = self._freetext_headline(ft_query, original_querystring)
        return ft_query

    def _add_phrases_query(self, ft_query, phrases):
        for bool_type in ['should', 'must', 'must_not']:
            key = 'phrases' if bool_type == 'should' else "phrases_%s" % bool_type

            for phrase in phrases[key]:
                if bool_type not in ft_query['bool']:
                    ft_query['bool'][bool_type] = []
                ft_query['bool'][bool_type].append({"multi_match":
                                                    {"query": phrase,
                                                     "fields": ["originalJobPosting.title", ],
                                                     "type": "phrase"}})

        return ft_query

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

    def _create_base_ft_query(self, querystring):
        # Creates a base query dict for "independent" freetext words
        # (e.g. words not found in text_to_concepts)
        method = 'or'
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
            musts.append(self._freetext_wildcard(prefix_words, "prefix", method))
        if suffix_words:
            musts.append(self._freetext_wildcard(suffix_words, "suffix", method))
        if musts:
            ft_query['bool']['must'].append({"bool": {"must": musts}})
        if mustnts:
            ft_query['bool']['must_not'] = mustnts
        return ft_query

    def _freetext_fields(self, searchword, method=settings.DEFAULT_FREETEXT_BOOL_METHOD):
        return [{
                "multi_match": {
                    "query": searchword,
                    "type": "cross_fields",
                    "operator": method,
                    "fields": ["originalJobPosting.title" + "^3",
                               f.KEYWORDS_EXTRACTED + ".location^5"]
                }
        }]

    def _freetext_wildcard(self, searchword, wildcard_side, method=settings.DEFAULT_FREETEXT_BOOL_METHOD):
        return [{
                "multi_match": {
                    "query": searchword,
                    "type": "cross_fields",
                    "operator": method,
                    "fields": ["originalJobPosting.title" + "." + wildcard_side, ]
                }
        }]

    def _freetext_headline(self, query_dict, querystring):
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
                            "originalJobPosting.title" + ".words": {
                                "query": querystring.strip(),
                                "operator": "and",
                                "boost": 5
                            }
                        }
                    })
            except KeyError:
                log.error("No bool clause for title query")

        return query_dict

    def _freetext_concepts(self, query_dict, concepts,
                           querystring, concept_keys, bool_type):
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

                    field = "%s.%s" % (base_field, key)
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

        return query_dict

    # Parses OCCUPATION, FIELD and GROUP
    def _build_yrkes_query(self, yrkesroller, yrkesgrupper, yrkesomraden):
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
                f.OCCUPATION_GROUP + "." + f.CONCEPT_ID + ".keyword": {
                    "value": y,
                    "boost": 1.0}}} for y in yrkesgrupper if y and not y.startswith('-')]

        yrke_term_query += [{
            "term": {
                f.OCCUPATION_FIELD + "." + f.CONCEPT_ID + ".keyword": {
                    "value": y,
                    "boost": 1.0}}} for y in yrkesomraden if y and not y.startswith('-')]

        neg_yrke_term_query = [{
            "term": {
                f.OCCUPATION + "." + f.CONCEPT_ID + ".keyword": {
                    "value": y[1:]}}} for y in yrken if y and y.startswith('-')]

        neg_yrke_term_query += [{
            "term": {
                f.OCCUPATION_GROUP + "." + f.CONCEPT_ID + ".keyword": {
                    "value": y[1:]}}} for y in yrkesgrupper if y and y.startswith('-')]

        neg_yrke_term_query += [{
            "term": {
                f.OCCUPATION_FIELD + "." + f.CONCEPT_ID + ".keyword": {
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

    # Parses MUNICIPALITY and REGION
    def _build_plats_query(self, kommunkoder, lanskoder, landskoder):
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
            f.WORKPLACE_ADDRESS_MUNICIPALITY_CONCEPT_ID + ".keyword": {
                "value": kkod, "boost": 2.0}}} for kkod in kommuner]

        plats_term_query += [{"term": {
            f.WORKPLACE_ADDRESS_REGION_CONCEPT_ID + ".keyword": {
                "value": lkod, "boost": 1.0}}} for lkod in lan]

        plats_term_query += [{"term": {
            f.WORKPLACE_ADDRESS_COUNTRY_CONCEPT_ID + ".keyword": {
                "value": ckod, "boost": 1.0}}} for ckod in land]

        plats_bool_query = {"bool": {
            "should": plats_term_query}
        } if plats_term_query else {}
        neg_komm_term_query = []
        neg_lan_term_query = []
        neg_land_term_query = []
        if neg_komm:
            neg_komm_term_query += [{"term": {
                f.WORKPLACE_ADDRESS_MUNICIPALITY_CONCEPT_ID: {
                    "value": kkod}}} for kkod in neg_komm]
        if neg_lan:
            neg_lan_term_query += [{"term": {
                f.WORKPLACE_ADDRESS_REGION_CONCEPT_ID: {
                    "value": lkod}}} for lkod in neg_lan]

        if neg_land:
            neg_land_term_query += [{"term": {
                f.WORKPLACE_ADDRESS_COUNTRY_CONCEPT_ID: {
                    "value": ckod}}} for ckod in neg_land]

        if neg_komm_term_query or neg_lan_term_query or neg_land_term_query:
            if 'bool' not in plats_bool_query:
                plats_bool_query['bool'] = {}
            plats_bool_query['bool']['must_not'] = neg_komm_term_query + neg_lan_term_query + neg_land_term_query

        return plats_bool_query
