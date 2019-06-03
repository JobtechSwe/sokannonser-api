import logging
import re
from sokannonser import settings
from sokannonser.repository import ttc, taxonomy
from sokannonser.rest.model import queries
from sokannonser.rest.model import fields as f

log = logging.getLogger(__name__)


class QueryBuilder(object):
    def parse_args(self, args):
        """
        Parse arguments for query and return an elastic query dsl

        Keyword arguments:
        args -- dictionary containing parameters from query
        """
        query_dsl = self._bootstrap_query(args)

        # Check for empty query
        if not any(v is not None for v in args.values()):
            log.debug("Constructing match-all query")
            query_dsl['query']['bool']['must'].append({'match_all': {}})
            if 'sort' not in query_dsl:
                query_dsl['sort'] = [f.sort_options.get('pubdate-desc')]
            return query_dsl

        must_queries = list()

        must_queries.append(
            self._build_freetext_query(args.get(settings.FREETEXT_QUERY),
                                       args.get(settings.FREETEXT_FIELDS))
        )
        must_queries.append(self._build_employer_query(args.get(settings.EMPLOYER)))
        must_queries.append(self._build_yrkes_query(args.get(taxonomy.OCCUPATION),
                                                    args.get(taxonomy.GROUP),
                                                    args.get(taxonomy.FIELD)))
        must_queries.append(self._filter_timeframe(args.get(settings.PUBLISHED_AFTER),
                                                   args.get(settings.PUBLISHED_BEFORE)))
        must_queries.append(self._build_parttime_query(args.get(settings.PARTTIME_MIN),
                                                       args.get(settings.PARTTIME_MAX)))
        must_queries.append(self._build_plats_query(args.get(taxonomy.MUNICIPALITY),
                                                    args.get(taxonomy.REGION)))
        must_queries.append(self._build_country_query(args.get(taxonomy.COUNTRY)))
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

    def filter_aggs(self, aggs, freetext):
        fwords = freetext.split(' ') if freetext else []
        value_dicts = []
        for agg in aggs:
            if agg.startswith('complete_'):
                value_dicts += [{"type": agg[9:], **bucket}
                                for bucket in aggs[agg]['buckets']]

            filtered_aggs = [{"value": kv['key'],
                              "type": kv['type'],
                              "occurrences": kv['doc_count']}
                             for kv in sorted(value_dicts,
                                              key=lambda k: k['doc_count'],
                                              reverse=True)
                             if kv['key'] not in fwords]
        if len(filtered_aggs) > 10:
            return filtered_aggs[0:10]
        return filtered_aggs

    def _bootstrap_query(self, args):
        query_dsl = dict()
        query_dsl['from'] = args.pop(settings.OFFSET, 0)
        query_dsl['size'] = args.pop(settings.LIMIT, 10)
        # No need to track all results if used for typeahead
        if not args.get(settings.TYPEAHEAD_QUERY):
            query_dsl['track_total_hits'] = True
        if args.pop(settings.DETAILS, '') == queries.OPTIONS_BRIEF:
            query_dsl['_source'] = [f.ID, f.HEADLINE, f.APPLICATION_DEADLINE,
                                    f.EMPLOYMENT_TYPE+"."+f.LABEL,
                                    f.WORKING_HOURS_TYPE+"."+f.LABEL,
                                    f.EMPLOYER_NAME,
                                    f.PUBLICATION_DATE]
        # Remove api-key from args to make sure an empty query can occur
        args.pop(settings.APIKEY)

        # Make sure to only serve published ads
        query_dsl['query'] = {
            'bool': {
                'must': [],
                'filter': [
                    {
                        'range': {
                            f.PUBLICATION_DATE: {
                                'lte': 'now/m'
                            }
                        }
                    },
                    {
                        'range': {
                            f.LAST_PUBLICATION_DATE: {
                                'gte': 'now/m'
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
        complete_fields = args.get(settings.FREETEXT_FIELDS) or queries.QF_CHOICES
        if complete_string:
            complete = complete_string.split(' ')[-1]
            size = 12/len(complete_fields)
            for field in complete_fields:
                dkey = "complete_%s" % field
                base_field = f.KEYWORDS_EXTRACTED \
                    if field in ['location', 'employer'] else f.KEYWORDS_ENRICHED
                query_dsl['aggs'][dkey] = {
                    "terms": {
                        "field": "%s.%s.raw" % (base_field, field),
                        "size": size,
                        "include": "%s.*" % complete.lower()
                    }
                }

        if args.get(settings.SORT):
            query_dsl['sort'] = f.sort_options.get(args.pop(settings.SORT))
        else:
            query_dsl['sort'] = ["_score", {f.ID: "asc"}]
        return query_dsl

    def _assemble_queries(self, query_dsl, additional_queries, additional_filters):
        for query in additional_queries:
            if query:
                query_dsl['query']['bool']['must'].append(query)
        for af in additional_filters:
            if af:
                query_dsl['query']['bool']['filter'].append(af)
        return query_dsl

    def __rewrite_word_for_regex(self, word):
        if '+' in word:
            modded_term = ''
            for c in word:
                if c == '+':
                    modded_term += '\\'
                modded_term += c
            return modded_term
        return word

    # Parses FREETEXT_QUERY and FREETEXT_FIELDS
    def _build_freetext_query(self, querystring, queryfields):
        if not querystring:
            return None
        if not queryfields:
            queryfields = queries.QF_CHOICES

        concepts = ttc.text_to_concepts(querystring)
        # Sort all concepts by string length
        all_concepts = sorted(concepts['occupation'] +
                              concepts['skill'] +
                              concepts['occupation_must'] +
                              concepts['skill_must'] +
                              concepts['occupation_must_not'] +
                              concepts['skill_must_not'],
                              key=lambda c: len(c),
                              reverse=True)
        original_querystring = querystring
        # Remove found concepts from querystring
        for term in [concept['term'] for concept in all_concepts]:
            term = self.__rewrite_word_for_regex(term)
            p = re.compile(f'(\\s*){term}(\\s*)')
            querystring = p.sub('\\1\\2', querystring).strip()

        inc_words = ' '.join([w for w in querystring.split(' ')
                              if w and not w.startswith('+')
                              and not w.startswith('-')])
        req_words = ' '.join([w[1:] for w in querystring.split(' ')
                              if w.startswith('+')
                              and w[1:].strip()])
        exc_words = ' '.join([w[1:] for w in querystring.split(' ')
                              if w.startswith('-')
                              and w[1:].strip()])
        shoulds = self.__freetext_fields(inc_words) if inc_words else []
        musts = self.__freetext_fields(req_words) if req_words else []
        mustnts = self.__freetext_fields(exc_words) if exc_words else []

        ft_query = {"bool": {}}
        # Add "common" words to query
        if shoulds:
            # Include all "must" words in should, to make sure any single "should"-word
            # not becomes exclusive
            ft_query['bool']['should'] = shoulds + musts
        if musts:
            ft_query['bool']['must'] = musts
        if mustnts:
            ft_query['bool']['must_not'] = mustnts
        # Make all "musts" "shoulds" as well
        for qf in queryfields:
            if qf in concepts:
                must_key = "%s_must" % qf
                concepts[qf] += [c['concept'].lower() for c in concepts.get(must_key, [])]
        # Add concepts to query
        for concept_type in queryfields:
            sub_should = self.__freetext_concepts({"bool": {}}, concepts,
                                                  querystring,
                                                  [concept_type], "should")
            if 'should' in sub_should['bool']:
                if 'must' not in ft_query['bool']:
                    ft_query['bool']['must'] = []
                ft_query['bool']['must'].append(sub_should)
        # Remove unwanted concepts from query
        self.__freetext_concepts(ft_query, concepts, querystring,
                                 queryfields, 'must_not')

        # Add required concepts to query
        self.__freetext_concepts(ft_query, concepts, querystring,
                                 queryfields, 'must')

        # Add a headline query as well
        ft_query = self.__freetext_headline(ft_query, original_querystring)
        return ft_query

    def __freetext_headline(self, query_dict, querystring):
        if 'must' not in query_dict['bool']:
            query_dict['bool']['must'] = []
        musts = query_dict['bool']['must']
        if not musts:
            if 'should' not in query_dict['bool']:
                query_dict['bool']['should'] = []
            shoulds = query_dict['bool']['should']
        else:
            shoulds = musts[0]['bool']['should']

        shoulds.append(
            {
                "match": {
                    f.HEADLINE + ".words": {
                        "query": querystring,
                        "operator": "and",
                        "boost": 5
                    }
                }
            }
        )
        return query_dict

    def __freetext_concepts(self, query_dict, concepts,
                            querystring, concept_keys, bool_type):
        for key in concept_keys:
            dict_key = "%s_%s" % (key, bool_type) if bool_type != 'should' else key
            for value in [c['concept'].lower() for c in concepts.get(dict_key, [])]:
                if bool_type not in query_dict['bool']:
                    query_dict['bool'][bool_type] = []

                base_field = f.KEYWORDS_EXTRACTED \
                    if key in ['location', 'employer'] else f.KEYWORDS_ENRICHED
                field = "%s.%s.raw" % (base_field, key)
                query_dict['bool'][bool_type].append(
                    {
                        "term": {
                            field: {
                                "value": value,
                                "boost": 10
                            }
                        }
                    }
                )

        return query_dict

    def __freetext_fields(self, searchword):
        return [
            {
                "multi_match": {
                    "query": searchword,
                    "type": "cross_fields",
                    "operator": "and",
                    "fields": [f.HEADLINE+"^3", f.EMPLOYER_NAME+"^2",
                               f.EMPLOYER_WORKPLACE+"^2", f.DESCRIPTION_TEXT,
                               f.ID, f.EXTERNAL_ID]
                }
            }
        ]

    # Parses EMPLOYER
    def _build_employer_query(self, employers):
        if employers:
            bool_segment = {"bool": {"should": []}}
            for employer in employers:
                if employer.isdigit():
                    bool_segment['bool']['should'].append(
                        {"prefix": {f.EMPLOYER_ORGANIZATION_NUMBER: employer}}
                    )
                else:
                    bool_segment['bool']['should'].append(
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

    # Parses OCCUPATION, FIELD and GROUP
    def _build_yrkes_query(self, yrkesroller, yrkesgrupper, yrkesomraden):
        yrken = yrkesroller or []
        yrkesgrupper = yrkesgrupper or []
        yrkesomraden = yrkesomraden or []

        yrke_term_query = [{
            "term": {
                f.OCCUPATION+"."+f.CONCEPT_ID+".keyword": {
                    "value": y,
                    "boost": 2.0}}} for y in yrken if y and not y.startswith('-')]
        yrke_term_query += [{
            "term": {
                f.OCCUPATION+"."+f.LEGACY_AMS_TAXONOMY_ID: {
                    "value": y,
                    "boost": 2.0}}} for y in yrken if y and not y.startswith('-')]
        yrke_term_query += [{
            "term": {
                f.OCCUPATION_GROUP+"."+f.CONCEPT_ID+".keyword": {
                    "value": y,
                    "boost": 1.0}}} for y in yrkesgrupper if y and not y.startswith('-')]
        yrke_term_query += [{
            "term": {
                f.OCCUPATION_GROUP+"."+f.LEGACY_AMS_TAXONOMY_ID: {
                    "value": y,
                    "boost": 1.0}}} for y in yrkesgrupper if y and not y.startswith('-')]
        yrke_term_query += [{
            "term": {
                f.OCCUPATION_FIELD+"."+f.CONCEPT_ID+".keyword": {
                    "value": y,
                    "boost": 1.0}}} for y in yrkesomraden if y and not y.startswith('-')]
        yrke_term_query += [{
            "term": {
                f.OCCUPATION_FIELD+"."+f.LEGACY_AMS_TAXONOMY_ID: {
                    "value": y,
                    "boost": 1.0}}} for y in yrkesomraden if y and not y.startswith('-')]
        neg_yrke_term_query = [{
            "term": {
                f.OCCUPATION+"."+f.CONCEPT_ID+".keyword": {
                    "value": y[1:]}}} for y in yrken if y and y.startswith('-')]
        neg_yrke_term_query = [{
            "term": {
                f.OCCUPATION+"."+f.LEGACY_AMS_TAXONOMY_ID: {
                    "value": y[1:]}}} for y in yrken if y and y.startswith('-')]
        neg_yrke_term_query += [{
            "term": {
                f.OCCUPATION_GROUP+"."+f.CONCEPT_ID+".keyword": {
                    "value": y[1:]}}} for y in yrkesgrupper if y and y.startswith('-')]
        neg_yrke_term_query += [{
            "term": {
                f.OCCUPATION_GROUP+"."+f.LEGACY_AMS_TAXONOMY_ID: {
                    "value": y[1:]}}} for y in yrkesgrupper if y and y.startswith('-')]
        neg_yrke_term_query += [{
            "term": {
                f.OCCUPATION_FIELD+"."+f.CONCEPT_ID+".keyword": {
                    "value": y[1:]}}} for y in yrkesomraden if y and y.startswith('-')]
        neg_yrke_term_query += [{
            "term": {
                f.OCCUPATION_FIELD+"."+f.LEGACY_AMS_TAXONOMY_ID: {
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
    def _build_plats_query(self, kommunkoder, lanskoder):
        kommuner = []
        neg_komm = []
        lan = []
        neg_lan = []
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
        plats_term_query = [{"term": {
            f.WORKPLACE_ADDRESS_MUNICIPALITY_CODE: {
                "value": kkod, "boost": 2.0}}} for kkod in kommuner]
        plats_term_query += [{"term": {
            f.WORKPLACE_ADDRESS_MUNICIPALITY_CONCEPT_ID: {
                "value": kkod, "boost": 2.0}}} for kkod in kommuner]
        plats_term_query += [{"term": {
            f.WORKPLACE_ADDRESS_REGION_CODE: {
                "value": lkod, "boost": 1.0}}} for lkod in lan]
        plats_term_query += [{"term": {
            f.WORKPLACE_ADDRESS_REGION_CONCEPT_ID: {
                "value": lkod, "boost": 1.0}}} for lkod in lan]
        plats_bool_query = {"bool": {
            "should": plats_term_query}
        } if plats_term_query else {}
        neg_komm_term_query = []
        neg_lan_term_query = []
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
        if neg_komm_term_query or neg_lan_term_query:
            if 'bool' not in plats_bool_query:
                plats_bool_query['bool'] = {}
            plats_bool_query['bool']['must_not'] = neg_komm_term_query + \
                neg_lan_term_query
        return plats_bool_query

    # Parses COUNTRY
    def _build_country_query(self, landskoder):
        lander = []
        neg_land = []
        country_term_query = []
        neg_country_term_query = []
        for lkod in landskoder if landskoder else []:
            if lkod.startswith('-'):
                neg_land.append(lkod[1:])
            else:
                lander.append(lkod)
        country_term_query = [{"term": {
            f.WORKPLACE_ADDRESS_COUNTRY_CODE: {
                "value": lkod, "boost": 1.0}}} for lkod in lander]
        country_term_query += [{"term": {
            f.WORKPLACE_ADDRESS_COUNTRY_CONCEPT_ID: {
                "value": lkod, "boost": 1.0}}} for lkod in lander]
        country_bool_query = {"bool": {
            "should": country_term_query}
        } if country_term_query else {}
        if neg_land:
            neg_country_term_query = [{"term": {
                f.WORKPLACE_ADDRESS_COUNTRY_CODE: {
                    "value": lkod}}} for lkod in neg_land]
            neg_country_term_query += [{"term": {
                f.WORKPLACE_ADDRESS_COUNTRY_CONCEPT_ID: {
                    "value": lkod}}} for lkod in neg_land]
            if 'bool' not in country_bool_query:
                country_bool_query['bool'] = {}
            country_bool_query['bool']['must_not'] = neg_country_term_query
        return country_bool_query

    # Parses PUBLISHED_AFTER and PUBLISHED_BEFORE
    def _filter_timeframe(self, from_datetime, to_datetime):
        if not from_datetime and not to_datetime:
            return None
        range_query = {"range": {f.PUBLICATION_DATE: {}}}
        if from_datetime:
            range_query['range'][f.PUBLICATION_DATE]['gte'] = from_datetime.isoformat()
        if to_datetime:
            range_query['range'][f.PUBLICATION_DATE]['lte'] = to_datetime.isoformat()
        return range_query

    # Parses PARTTIME_MIN and PARTTIME_MAX
    def _build_parttime_query(self, parttime_min, parttime_max):
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

    def _build_generic_query(self, keys, itemlist):
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
    def _build_geo_dist_filter(self, positions, coordinate_ranges):
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
            if (not latitude or not longitude or not coordinate_range):
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
