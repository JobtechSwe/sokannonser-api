from flask_restx import reqparse, inputs
from datetime import datetime
from sokannonser import settings
from sokannonser.repository import taxonomy
from sokannonser.rest.model import fields

# Frågemodeller
QF_CHOICES = ['occupation', 'skill', 'location', 'employer']
VF_TYPE_CHOICES = [taxonomy.OCCUPATION, taxonomy.GROUP, taxonomy.FIELD, taxonomy.SKILL,
                   taxonomy.MUNICIPALITY, taxonomy.REGION, taxonomy.COUNTRY,
                   taxonomy.PLACE, taxonomy.WAGE_TYPE, taxonomy.WORKTIME_EXTENT,
                   taxonomy.DRIVING_LICENCE, taxonomy.EMPLOYMENT_TYPE, taxonomy.LANGUAGE]
OPTIONS_BRIEF = 'brief'
OPTIONS_FULL = 'full'

swagger_doc_params = {
    settings.APIKEY: "Required API key",
    settings.X_FEATURE_FREETEXT_BOOL_METHOD: "Boolean method to use for unclassified "
    "freetext words. Defaults to \"" + settings.DEFAULT_FREETEXT_BOOL_METHOD + "\".",
    settings.X_FEATURE_DISABLE_SMART_FREETEXT: "Disables machine learning enriched queries."
    " Freetext becomes traditional freetext query according to the setting of " 
    "\"%s\"" % settings.X_FEATURE_FREETEXT_BOOL_METHOD,
    settings.X_FEATURE_ENABLE_FALSE_NEGATIVE: "Enables extra search for the current known "
    "term in free text to avoid false negatives ",
    settings.PUBLISHED_AFTER: "Fetch job ads published after specified date and time."
    "Accepts either datetime (format YYYY-mm-ddTHH:MM:SS) or number of minutes "
    "(e.g 120 means published in the last two hours)",
    settings.PUBLISHED_BEFORE: "Fetch job ads published before specified date and time "
    "(format YYYY-mm-ddTHH:MM:SS)",
    settings.FREETEXT_QUERY: "Freetext query. Search in ad headline, ad description and "
    "place of work",
    settings.FREETEXT_FIELDS: "Fields to freetext search in, in addition to default "
    "freetext search "
    "(parameter " + settings.FREETEXT_QUERY + ")\n"
    "Valid input values: " + str(QF_CHOICES) + "\n"
    "Default (no input): Search in ad headline, ad description "
    "and place of work",
    settings.EMPLOYER: "Name or organisation number (numbers only, no dashes or spaces) "
    "of employer",
    taxonomy.OCCUPATION: "One or more occupational codes according to the taxonomy",
    taxonomy.GROUP: "One or more occupational group codes according to the taxonomy",
    taxonomy.FIELD: "One or more occupational area codes according to the taxonomy",
    taxonomy.COLLECTION: "One or more occupational collections according to the taxonomy. "
                         "Excludes not matching occupations, groups, fields",
    taxonomy.SKILL: "One or more competency codes according to the taxonomy",
    taxonomy.LANGUAGE: "One or more language codes according to the taxonomy",
    taxonomy.DRIVING_LICENCE_REQUIRED: "Set to true if driving licence required"
    ", false if not",
    taxonomy.DRIVING_LICENCE: "One or more types of demanded driving licenses, code "
    "according to the taxonomy",
    taxonomy.EMPLOYMENT_TYPE: "Employment type, code according to the taxonomy",
    settings.EXPERIENCE_REQUIRED: "Input 'false' to filter jobs that don't require "
    "experience",
    taxonomy.WORKTIME_EXTENT: "One or more codes for worktime extent, code according to "
    "the taxonomy",
    settings.PARTTIME_MIN: "For part-time jobs, minimum extent in percent "
    "(for example 50 for 50%)",
    settings.PARTTIME_MAX: "For part-time jobs, maximum extent in percent "
    "(for example 100 for 100%)",
    taxonomy.MUNICIPALITY: "One or more municipality codes, code according to "
    "the taxonomy",
    taxonomy.REGION: "One or more region codes, code according to the taxonomy",
    taxonomy.COUNTRY: "One or more country codes, code according to the taxonomy",
    settings.UNSPECIFIED_SWEDEN_WORKPLACE: "True will return all unspecified ads in Sweden",
    settings.ABROAD: "True will return ads for work outside of Sweden even when searching for places "
                     "matching Swedish municipality/region/country. False does nothing",
    settings.POSITION: "Latitude and longitude in the format \"59.329,18.068\" "
    "(latitude,longitude)",
    settings.POSITION_RADIUS: "Radius from the specified " + settings.POSITION +
    " (latitude,longitude) in kilometers (km)",
}
swagger_filter_doc_params = {
    settings.MIN_RELEVANCE: "Set a result relevance threshold between 0 and 1",
    settings.DETAILS: "Show 'full' (default) or 'brief' results details",
    settings.OFFSET: "The offset parameter defines the offset from the first result you "
    "want to fetch. Valid range is (0-%d)" % settings.MAX_OFFSET,
    settings.LIMIT: "Number of results to fetch. Valid range is (0-%d)" % settings.MAX_LIMIT,
    settings.SORT: "Sorting.\n"
    "relevance: relevance (points) (default sorting)\n"
    "pubdate-desc: published date, descending (newest job ad first)\n"
    "pubdate-asc: published date, ascending (oldest job ad first)\n"
    "applydate-desc: last apply date, descending (newest apply date first)\n"
    "applydate-asc: last apply date, descending (oldest apply date first, "
    "few days left for application)\n"
    "updated: sort by update date (descending)\n",
    settings.STATISTICS: "Show statistics for specified fields "
    "(available fields: %s, %s, %s, %s, %s and %s)" % (
        taxonomy.OCCUPATION,
        taxonomy.GROUP,
        taxonomy.FIELD,
        taxonomy.COUNTRY,
        taxonomy.MUNICIPALITY,
        taxonomy.REGION),
    settings.STAT_LMT: "Maximum number of statistical rows per field",
}


def lowercase_maxlength(value):
    if value is None:
        raise ValueError('string type must be non-null')
    if len(value) > 255:
        raise ValueError('parameter can not be longer than 255 characters')

    return str(value).lower()


load_ad_query = reqparse.RequestParser()
load_ad_query.add_argument(settings.APIKEY, location='headers', required=True)

base_annons_query = reqparse.RequestParser()
base_annons_query.add_argument(settings.APIKEY, location='headers', required=True)
base_annons_query.add_argument(settings.X_FEATURE_FREETEXT_BOOL_METHOD, choices=['and', 'or'],
                               default=settings.DEFAULT_FREETEXT_BOOL_METHOD,
                               location='headers', required=False)
base_annons_query.add_argument(settings.X_FEATURE_DISABLE_SMART_FREETEXT, type=inputs.boolean,
                               location='headers', required=False),
base_annons_query.add_argument(settings.X_FEATURE_ENABLE_FALSE_NEGATIVE, type=inputs.boolean,
                               location='headers', required=False),
base_annons_query.add_argument(settings.PUBLISHED_BEFORE,
                               type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'))
# annons_complete_query.add_argument(settings.PUBLISHED_AFTER,
#                                    type=lambda x: datetime.strptime(x,
#                                                                     '%Y-%m-%dT%H:%M:%S'))
datetime_or_minutes_regex = r'^(\d\d\d\d-(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01])T(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9]))|(\d+)$'
base_annons_query.add_argument(settings.PUBLISHED_AFTER,
                               type=inputs.regex(datetime_or_minutes_regex))
base_annons_query.add_argument(taxonomy.OCCUPATION, action='append')
base_annons_query.add_argument(taxonomy.GROUP, action='append')
base_annons_query.add_argument(taxonomy.FIELD, action='append')
base_annons_query.add_argument(taxonomy.COLLECTION, action='append')
base_annons_query.add_argument(taxonomy.SKILL, action='append')
base_annons_query.add_argument(taxonomy.LANGUAGE, action='append')
base_annons_query.add_argument(taxonomy.WORKTIME_EXTENT, action='append')
base_annons_query.add_argument(settings.PARTTIME_MIN, type=float)
base_annons_query.add_argument(settings.PARTTIME_MAX, type=float)
base_annons_query.add_argument(taxonomy.DRIVING_LICENCE_REQUIRED, type=inputs.boolean)
base_annons_query.add_argument(taxonomy.DRIVING_LICENCE, action='append')
base_annons_query.add_argument(taxonomy.EMPLOYMENT_TYPE, action='append')
base_annons_query.add_argument(settings.EXPERIENCE_REQUIRED,
                               choices=['true', 'false'])
base_annons_query.add_argument(taxonomy.MUNICIPALITY, action='append')
base_annons_query.add_argument(taxonomy.REGION, action='append')
base_annons_query.add_argument(taxonomy.COUNTRY, action='append')
base_annons_query.add_argument(settings.UNSPECIFIED_SWEDEN_WORKPLACE, type=inputs.boolean)
base_annons_query.add_argument(settings.ABROAD, type=inputs.boolean)
# Matches(lat,long) +90.0,-127.554334; 45,180; -90,-180; -90.000,-180.0000; +90,+180
# r for raw, PEP8
position_regex = r'^[-+]?([1-8]?\d(\.\d*)?|90(\.0*)?),' \
            r'[-+]?(180(\.0*)?|((1[0-7]\d)|([1-9]?\d))(\.\d*)?)$'
base_annons_query.add_argument(settings.POSITION,
                               type=inputs.regex(position_regex),
                               action='append')
base_annons_query.add_argument(settings.POSITION_RADIUS, type=int, action='append')
base_annons_query.add_argument(settings.EMPLOYER, action='append')
base_annons_query.add_argument(settings.FREETEXT_QUERY, type=lowercase_maxlength)
base_annons_query.add_argument(settings.FREETEXT_FIELDS, action='append',
                               choices=QF_CHOICES)

annons_complete_query = base_annons_query.copy()
annons_complete_query.add_argument(settings.LIMIT, type=inputs.int_range(0, settings.MAX_COMPLETE_LIMIT),
                                   default=10)
annons_complete_query.add_argument(settings.CONTEXTUAL_TYPEAHEAD, type=inputs.boolean,
                                   default=True)


pb_query = base_annons_query.copy()
pb_query.add_argument(settings.MIN_RELEVANCE, type=float),
pb_query.add_argument(settings.DETAILS, choices=[OPTIONS_FULL, OPTIONS_BRIEF])
pb_query.add_argument(settings.OFFSET, type=inputs.int_range(0, settings.MAX_OFFSET),
                      default=0)
pb_query.add_argument(settings.LIMIT, type=inputs.int_range(0, settings.MAX_LIMIT),
                      default=10)
# TODO: Remove sort_option 'id' in next major version
pb_query.add_argument(settings.SORT, choices=list(fields.sort_options.keys()) + ['id'])
pb_query.add_argument(settings.STATISTICS, action='append',
                      choices=[taxonomy.OCCUPATION, taxonomy.GROUP,
                               taxonomy.FIELD, taxonomy.COUNTRY,
                               taxonomy.MUNICIPALITY, taxonomy.REGION])
pb_query.add_argument(settings.STAT_LMT, type=inputs.int_range(0, 30), required=False)

taxonomy_query = reqparse.RequestParser()
taxonomy_query.add_argument(settings.APIKEY, location='headers', required=True)
taxonomy_query.add_argument(settings.OFFSET,
                            type=inputs.int_range(0, settings.MAX_OFFSET),
                            default=0)
taxonomy_query.add_argument(settings.LIMIT, type=inputs.int_range(0, settings.MAX_TAXONOMY_LIMIT),
                            default=10)
taxonomy_query.add_argument(settings.FREETEXT_QUERY)
taxonomy_query.add_argument('type', action='append',
                            choices=VF_TYPE_CHOICES),
taxonomy_query.add_argument(settings.SHOW_COUNT, type=inputs.boolean, default=False)
taxonomy_query.add_argument('parent-id', action='append')
