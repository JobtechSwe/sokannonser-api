import logging
from sokannonser import settings
from sokannonser.repository import elastic
from valuestore import taxonomy
from valuestore.taxonomy import tax_type

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
            return query_dsl

        must_queries = list()

        must_queries.append(self._build_freetext_query(args.get(settings.FREETEXT_QUERY)))
        must_queries.append(self._build_yrkes_query(args.get(taxonomy.OCCUPATION),
                                                    args.get(taxonomy.GROUP),
                                                    args.get(taxonomy.FIELD)))
        must_queries.append(self._filter_timeframe(args.get(settings.PUBLISHED_AFTER),
                                                   args.get(settings.PUBLISHED_BEFORE)))
        must_queries.append(self._build_parttime_query(args.get(settings.PARTTIME_MIN),
                                                       args.get(settings.PARTTIME_MAX)))
        must_queries.append(self._build_plats_query(args.get(taxonomy.MUNICIPALITY),
                                                    args.get(taxonomy.REGION)))
        must_queries.append(self._build_generic_query("krav.kompetenser.kod",
                                                      args.get(taxonomy.SKILL)))
        must_queries.append(self._build_generic_query("arbetstidstyp.kod",
                                                      args.get(taxonomy.WORKTIME_EXTENT)))
        must_queries.append(self._build_generic_query("korkort.kod",
                                                      args.get(taxonomy.DRIVING_LICENCE)))
        must_queries.append(self._build_generic_query("anstallningstyp.kod",
                                                      args.get(taxonomy.EMPLOYMENT_TYPE)))

        # TODO: Maybe check if NO skills are listed in ad instead?
        if args.get(settings.EXPERIENCE_REQUIRED) == 'false':
            must_queries.append({"term": {"erfarenhet_kravs": False}})
        if args.get(settings.EXPERIENCE_REQUIRED) == 'true':
            must_queries.append({"term": {"erfarenhet_kravs": True}})

        filter_queries = list()
        geo_filter = self._build_geo_dist_filter(args.get(settings.LONGITUDE),
                                                 args.get(settings.LATITUDE),
                                                 args.get(settings.POSITION_RADIUS))
        filter_queries.append(geo_filter)

        query_dsl = self._assemble_queries(query_dsl, must_queries, filter_queries)

        stats = args.get(settings.STATISTICS) if args.get(settings.STATISTICS) else []
        for stat in stats:
            size = args.get(settings.STAT_LMT) if args.get(settings.STAT_LMT) else 5
            query_dsl['aggs'][stat] = {
                "terms": {
                    "field": settings.stats_options[stat],
                    "size": size
                }
            }

        return query_dsl

    def filter_aggs(self, aggs, freetext):
        fwords = freetext.split(' ') if freetext else []
        filtered_aggs = []
        for agg in aggs:
            if not agg.get('key') in fwords:
                filtered_aggs.append(agg)

        return filtered_aggs

    def _bootstrap_query(self, args):
        query_dsl = dict()
        query_dsl['from'] = args.pop(settings.OFFSET, 0)
        query_dsl['size'] = args.pop(settings.LIMIT, 10)
        # Remove api-key from args to make sure an empty query can occur
        args.pop(settings.APIKEY)

        # Make sure to only serve published ads
        query_dsl['query'] = {
            'bool': {
                'must': [],
                'filter': [
                    # {'term': {'status.publicerad': True}},
                    {
                        'range': {
                            'publiceringsdatum': {
                                'lte': 'now'
                            }
                        }
                    },
                    {
                        'range': {
                            'status.sista_publiceringsdatum': {
                                'gte': 'now'
                            }
                        }
                    },
                ]
            },
        }
        complete_string = args.get(settings.TYPEAHEAD_QUERY)
        query_dsl['aggs'] = {
            "positions": {
                "sum": {"field": "antal_platser"}
            }
        }
        if complete_string:
            complete = complete_string.split(' ')[-1]
            query_dsl['aggs']['complete'] = {
                "terms": {
                    "field": "keywords.raw",
                    "size": 20,
                    "include": "%s.*" % complete
                }
            }

        if args.get(settings.SORT):
            query_dsl['sort'] = [settings.sort_options.get(args.pop(settings.SORT))]
        return query_dsl

    def _assemble_queries(self, query_dsl, additional_queries, additional_filters):
        for query in additional_queries:
            if query:
                query_dsl['query']['bool']['must'].append(query)
        for f in additional_filters:
            if f:
                query_dsl['query']['bool']['filter'].append(f)
        return query_dsl

    def _build_freetext_query(self, querystring):
        if not querystring:
            return None
        inc_words = ' '.join([w for w in querystring.split(' ') if not w.startswith('-')])
        exc_words = ' '.join([w[1:] for w in querystring.split(' ') if w.startswith('-')])
        shoulds = self.freetext_fields(inc_words) if inc_words else None
        mustnts = self.freetext_fields(exc_words) if exc_words else None
        ft_query = {"bool": {}}
        if shoulds:
            ft_query['bool']['should'] = shoulds
        if mustnts:
            ft_query['bool']['must_not'] = mustnts

        return ft_query

    def _build_yrkes_query(self, yrkesroller, yrkesgrupper, yrkesomraden):
        yrken = [] if not yrkesroller else yrkesroller
        yrkesgrupper = [] if not yrkesgrupper else yrkesgrupper
        yrkesomraden = [] if not yrkesomraden else yrkesomraden

        yrke_term_query = [{
            "term": {
                "yrkesroll.kod": {
                    "value": y,
                    "boost": 2.0}}} for y in yrken if y and not y.startswith('-')]
        yrke_term_query += [{
            "term": {
                "yrkesgrupp.kod": {
                    "value": y,
                    "boost": 1.0}}} for y in yrkesgrupper if y and not y.startswith('-')]
        yrke_term_query += [{
            "term": {
                "yrkesomrade.kod": {
                    "value": y,
                    "boost": 1.0}}} for y in yrkesomraden if y and not y.startswith('-')]

        neg_yrke_term_query = [{
            "term": {
                "yrkesroll.kod": {
                    "value": y[1:]}}} for y in yrken if y and y.startswith('-')]
        neg_yrke_term_query += [{
            "term": {
                "yrkesgrupp.kod": {
                    "value": y[1:]}}} for y in yrkesgrupper if y and y.startswith('-')]
        neg_yrke_term_query += [{
            "term": {
                "yrkesomrade.kod": {
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

    def _build_plats_query(self, kommunkoder, lanskoder):
        kommuner = []
        neg_komm = []
        for kkod in kommunkoder if kommunkoder else []:
            if kkod.startswith('-'):
                neg_komm.append(kkod[1:])
            else:
                kommuner.append(kkod)

        kommunlanskoder = []
        for lanskod in lanskoder if lanskoder is not None else []:
            ttype = tax_type.get(taxonomy.MUNICIPALITY)
            if lanskod.startswith('-'):
                kommun_results = taxonomy.find_concepts(elastic, None, lanskod[1:],
                                                        ttype
                                                        ).get('hits', {}).get('hits', [])
                neg_komm += [entitet['_source']['id'] for entitet in kommun_results]
            else:
                kommun_results = taxonomy.find_concepts(elastic, None, lanskod,
                                                        ttype
                                                        ).get('hits', {}).get('hits', [])
                kommunlanskoder += [e['_source']['id'] for e in kommun_results]

        plats_term_query = [{"term": {
            "arbetsplatsadress.kommunkod": {
                "value": kkod, "boost": 2.0}}} for kkod in kommuner]
        plats_term_query += [{"term": {
            "arbetsplatsadress.kommunkod": {
                "value": lkod, "boost": 1.0}}} for lkod in kommunlanskoder]
        plats_bool_query = {"bool": {
            "should": plats_term_query}
        } if plats_term_query else {}
        if neg_komm:
            neg_plats_term_query = [{"term": {
                "arbetsplatsadress.kommunkod": {
                    "value": kkod}}} for kkod in neg_komm]
            if 'bool' not in plats_bool_query:
                plats_bool_query['bool'] = {}
            plats_bool_query['bool']['must_not'] = neg_plats_term_query
        return plats_bool_query

    def _filter_timeframe(self, from_datetime, to_datetime):
        if not from_datetime and not to_datetime:
            return None
        range_query = {"range": {"publiceringsdatum": {}}}
        if from_datetime:
            range_query['range']['publiceringsdatum']['gte'] = from_datetime.isoformat()
        if to_datetime:
            range_query['range']['publiceringsdatum']['lte'] = to_datetime.isoformat()
        return range_query

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
                            "arbetsomfattning.min": {
                                "lte": parttime_max,
                                "gte": parttime_min
                            },
                        }
                    },
                    {
                        "range": {
                            "arbetsomfattning.max": {
                                "lte": parttime_max,
                                "gte": parttime_min
                            }
                        }
                    }
                ]
            }
        }
        return parttime_query

    def _build_generic_query(self, key, itemlist):
        items = [] if not itemlist else itemlist

        term_query = [{"term": {key: {"value": item}}}
                      for item in items if not item.startswith('-')]

        neg_term_query = [{"term": {key: {"value": item[1:]}}}
                          for item in items if item.startswith('-')]

        if term_query or neg_term_query:
            query = {'bool': {}}
            if term_query:
                query['bool']['should'] = term_query
            if neg_term_query:
                query['bool']['must_not'] = neg_term_query
            return query

        return None

    def _build_geo_dist_filter(self, longitude, latitude, coordinate_range):
        geo_filter = {}
        if (not longitude
                or not latitude
                or not coordinate_range):
            return geo_filter
        elif ((-180 <= longitude <= 180)
              and (-90 <= latitude <= 90)
              and (coordinate_range > 0)):
            geo_filter["geo_distance"] = {
                "distance": str(coordinate_range) + "km",
                "arbetsplatsadress.coordinates": [longitude, latitude]
            }
        return geo_filter


class PlatsbankenQuery(QueryBuilder):
    def freetext_fields(self, searchword):
        return [
            {
                "match": {
                    "rubrik": {
                        "query": searchword,
                        "boost": 3
                    }
                }
            },
            {
                "match": {
                    "arbetsgivare.namn": {
                        "query": searchword,
                        "boost": 2
                    }
                }
            },
            {
                "multi_match": {
                    "query": searchword,
                    "fields": ["beskrivning.information",
                               "beskrivning.behov",
                               "beskrivning.krav",
                               "beskrivning.annonstext"]
                }
            }
        ]


class DefaultQuery(QueryBuilder):
    def freetext_fields(self, searchword):
        return [
            {
                "match": {
                    "rubrik": {
                        "query": searchword,
                        "boost": 3
                    }
                }
            },
            {
                "match": {
                    "arbetsgivare.namn": {
                        "query": searchword,
                        "boost": 2
                    }
                }
            },
            {
                "match": {
                    "keywords": {
                        "query": searchword,
                        "boost": 2
                    }
                }
            },
            {
                "multi_match": {
                    "query": searchword,
                    "fields": ["beskrivning.information",
                               "beskrivning.behov",
                               "beskrivning.krav",
                               "beskrivning.annonstext"]
                }
            }
        ]
