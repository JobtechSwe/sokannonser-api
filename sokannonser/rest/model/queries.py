from flask_restplus import reqparse, inputs
from datetime import datetime
from valuestore import taxonomy
from sokannonser import settings

# Frågemodeller
sok_platsannons_query = reqparse.RequestParser()
sok_platsannons_query.add_argument(settings.APIKEY, location='headers', required=True,
                                   default=settings.APIKEY_BACKDOOR)

sok_platsannons_query.add_argument(settings.OFFSET,
                                   type=inputs.int_range(0, settings.MAX_OFFSET),
                                   default=0)
sok_platsannons_query.add_argument(settings.LIMIT,
                                   type=inputs.int_range(0, settings.MAX_LIMIT),
                                   default=10)
sok_platsannons_query.add_argument(settings.SORT,
                                   choices=list(settings.sort_options.keys()))
sok_platsannons_query.add_argument(settings.PUBLISHED_BEFORE,
                                   type=lambda x: datetime.strptime(x,
                                                                    '%Y-%m-%dT%H:%M:%S'))
sok_platsannons_query.add_argument(settings.PUBLISHED_AFTER,
                                   type=lambda x: datetime.strptime(x,
                                                                    '%Y-%m-%dT%H:%M:%S'))
sok_platsannons_query.add_argument(settings.FREETEXT_QUERY)
sok_platsannons_query.add_argument(settings.TYPEAHEAD_QUERY)
sok_platsannons_query.add_argument(taxonomy.OCCUPATION, action='append')
sok_platsannons_query.add_argument(taxonomy.GROUP, action='append')
sok_platsannons_query.add_argument(taxonomy.FIELD, action='append')
sok_platsannons_query.add_argument(taxonomy.SKILL, action='append')
sok_platsannons_query.add_argument(taxonomy.WORKTIME_EXTENT, action='append')
sok_platsannons_query.add_argument(settings.PARTTIME_MIN, type=float)
sok_platsannons_query.add_argument(settings.PARTTIME_MAX, type=float)
sok_platsannons_query.add_argument(taxonomy.DRIVING_LICENCE, action='append')
sok_platsannons_query.add_argument(taxonomy.EMPLOYMENT_TYPE, action='append')
sok_platsannons_query.add_argument(settings.EXPERIENCE_REQUIRED, choices=['true', 'false'])
# sok_platsannons_query.add_argument(settings.PLACE)
sok_platsannons_query.add_argument(taxonomy.MUNICIPALITY, action='append')
sok_platsannons_query.add_argument(taxonomy.REGION, action='append')

sok_platsannons_query.add_argument(settings.LONGITUDE, type=float)
sok_platsannons_query.add_argument(settings.LATITUDE, type=float)
sok_platsannons_query.add_argument(settings.POSITION_RADIUS, type=int)
# sok_platsannons_query.add_argument(settings.PLACE_RADIUS, type=int)
sok_platsannons_query.add_argument(settings.STATISTICS, action='append',
                                   choices=[taxonomy.OCCUPATION, taxonomy.GROUP,
                                            taxonomy.FIELD])
sok_platsannons_query.add_argument(settings.STAT_LMT, type=int, required=False)
sok_platsannons_query.add_argument(settings.RESULT_MODEL, choices=settings.result_models)
# sok_platsannons_query.add_argument(settings.DATASET,
#                                    choices=settings.AVAILABLE_DATASETS,
#                                    default=settings.DATASET_AF)

auranest_query = reqparse.RequestParser()
auranest_query.add_argument(settings.APIKEY, location='headers', required=True,
                            default=settings.APIKEY_BACKDOOR)
auranest_query.add_argument('group_id')
auranest_query.add_argument(settings.OFFSET,
                            type=inputs.int_range(0, settings.MAX_OFFSET),
                            default=0)
auranest_query.add_argument(settings.LIMIT,
                            type=inputs.int_range(0, settings.MAX_LIMIT),
                            default=10)
auranest_query.add_argument(settings.SHOW_EXPIRED, choices=['true', 'false'])
auranest_query.add_argument(settings.FREETEXT_QUERY)
auranest_query.add_argument(settings.STATISTICS,
                            choices=list(settings.auranest_stats_options.keys()),
                            action='append')
auranest_query.add_argument(settings.STAT_LMT, type=inputs.int_range(0, 100), default=10)

auranest_typeahead = reqparse.RequestParser()
auranest_typeahead.add_argument(settings.APIKEY, location='headers', required=True,
                                default=settings.APIKEY_BACKDOOR)
auranest_typeahead.add_argument(settings.FREETEXT_QUERY)

taxonomy_query = reqparse.RequestParser()
taxonomy_query.add_argument(settings.APIKEY, location='headers', required=True,
                            default=settings.APIKEY_BACKDOOR)
taxonomy_query.add_argument(settings.OFFSET, type=int, default=0)
taxonomy_query.add_argument(settings.LIMIT, type=int, default=10)
taxonomy_query.add_argument(settings.FREETEXT_QUERY)
taxonomy_query.add_argument('kod', action='append')
taxonomy_query.add_argument('typ', choices=(taxonomy.OCCUPATION, taxonomy.GROUP,
                                            taxonomy.FIELD, taxonomy.SKILL,
                                            taxonomy.LANGUAGE, taxonomy.MUNICIPALITY,
                                            taxonomy.REGION, taxonomy.WORKTIME_EXTENT))
taxonomy_query.add_argument(settings.SHOW_COUNT, type=bool, default=False)
