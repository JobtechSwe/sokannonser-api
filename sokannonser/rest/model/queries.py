from flask_restplus import reqparse, inputs
from datetime import datetime
from sokannonser import settings
from sokannonser.repository import taxonomy
from sokannonser.rest.model import fields

# Frågemodeller
QF_CHOICES = ['occupation', 'skill', 'location', 'employer']
VF_TYPE_CHOICES = [taxonomy.OCCUPATION, taxonomy.GROUP, taxonomy.FIELD, taxonomy.SKILL,
                   taxonomy.MUNICIPALITY, taxonomy.REGION, taxonomy.COUNTRY,
                   taxonomy.PLACE, taxonomy.WAGE_TYPE, taxonomy.WORKTIME_EXTENT,
                   taxonomy.DRIVING_LICENCE, taxonomy.EMPLOYMENT_TYPE]
OPTIONS_BRIEF = 'brief'
OPTIONS_FULL = 'full'

swagger_doc_params = {
    settings.APIKEY: "Required API key",
    settings.PUBLISHED_AFTER: "Fetch job ads published after specified date and time "
    "(format YYYY-mm-ddTHH:MM:SS)",
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
    taxonomy.SKILL: "One or more competency codes according to the taxonomy",
    taxonomy.LANGUAGE: "One or more language codes according to the taxonomy",
    taxonomy.DRIVING_LICENCE_REQUIRED: "Set to true if driving license required"
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
    settings.POSITION: "Latitude and longitude in the format \"59.329,18.068\" "
    "(latitude,longitude)",
    settings.POSITION_RADIUS: "Radius from the specified " + settings.POSITION +
    " (latitude,longitude) in kilometers (km)",
}
swagger_filter_doc_params = {
    settings.DETAILS: "Show 'full' (default) or 'brief' results details",
    settings.OFFSET: "The offset parameter defines the offset from the first result you "
    "want to fetch"
    "Valid range is (0-%d)" % settings.MAX_OFFSET,
    settings.LIMIT: "Number of results to fetch (0-%d)" % settings.MAX_LIMIT,
    settings.SORT: "Sorting.\n"
    "relevance: relevance (points) (default sorting)\n"
    "pubdate-desc: published date, descending (newest job ad first)\n"
    "pubdate-asc: published date, ascending (oldest job ad first)\n"
    "applydate-desc: last apply date, descending (newest apply date first)\n"
    "applydate-asc: last apply date, descending (oldest apply date first, "
    "few days left for application)\n"
    "updated: sort by update date (descending)\n"
    "id: sort by job ad id (ascending)\n",
    settings.STATISTICS: "Show statistics for specified fields "
    "(available fields: %s, %s and %s)" % (
        taxonomy.OCCUPATION,
        taxonomy.GROUP,
        taxonomy.FIELD),
    settings.STAT_LMT: "Maximum number of statistical rows per field",
}


load_ad_query = reqparse.RequestParser()
load_ad_query.add_argument(settings.APIKEY, location='headers', required=True)

annons_complete_query = reqparse.RequestParser()
annons_complete_query.add_argument(settings.APIKEY, location='headers', required=True)
annons_complete_query.add_argument(settings.PUBLISHED_BEFORE,
                                   type=lambda x: datetime.strptime(x,
                                                                    '%Y-%m-%dT%H:%M:%S'))
annons_complete_query.add_argument(settings.PUBLISHED_AFTER,
                                   type=lambda x: datetime.strptime(x,
                                                                    '%Y-%m-%dT%H:%M:%S'))
annons_complete_query.add_argument(taxonomy.OCCUPATION, action='append')
annons_complete_query.add_argument(taxonomy.GROUP, action='append')
annons_complete_query.add_argument(taxonomy.FIELD, action='append')
annons_complete_query.add_argument(taxonomy.SKILL, action='append')
annons_complete_query.add_argument(taxonomy.LANGUAGE, action='append')
annons_complete_query.add_argument(taxonomy.WORKTIME_EXTENT, action='append')
annons_complete_query.add_argument(settings.PARTTIME_MIN, type=float)
annons_complete_query.add_argument(settings.PARTTIME_MAX, type=float)
annons_complete_query.add_argument(taxonomy.DRIVING_LICENCE_REQUIRED, type=inputs.boolean)
annons_complete_query.add_argument(taxonomy.DRIVING_LICENCE, action='append')
annons_complete_query.add_argument(taxonomy.EMPLOYMENT_TYPE, action='append')
annons_complete_query.add_argument(settings.EXPERIENCE_REQUIRED,
                                   choices=['true', 'false'])
annons_complete_query.add_argument(taxonomy.MUNICIPALITY, action='append')
annons_complete_query.add_argument(taxonomy.REGION, action='append')
annons_complete_query.add_argument(taxonomy.COUNTRY, action='append')
# Matches(lat,long) +90.0,-127.554334; 45,180; -90,-180; -90.000,-180.0000; +90,+180
# r for raw, PEP8
position_regex = r'^[-+]?([1-8]?\d(\.\d*)?|90(\.0*)?),' \
            r'[-+]?(180(\.0*)?|((1[0-7]\d)|([1-9]?\d))(\.\d*)?)$'
annons_complete_query.add_argument(settings.POSITION,
                                   type=inputs.regex(position_regex),
                                   action='append')
annons_complete_query.add_argument(settings.POSITION_RADIUS, type=int, action='append')
annons_complete_query.add_argument(settings.EMPLOYER, action='append')
annons_complete_query.add_argument(settings.FREETEXT_QUERY)
annons_complete_query.add_argument(settings.FREETEXT_FIELDS, action='append',
                                   choices=QF_CHOICES)

pb_query = annons_complete_query.copy()
pb_query.add_argument(settings.DETAILS, choices=[OPTIONS_FULL, OPTIONS_BRIEF])
pb_query.add_argument(settings.OFFSET, type=inputs.int_range(0, settings.MAX_OFFSET),
                      default=0)
pb_query.add_argument(settings.LIMIT, type=inputs.int_range(0, settings.MAX_LIMIT),
                      default=10)
pb_query.add_argument(settings.SORT, choices=list(fields.sort_options.keys()))
pb_query.add_argument(settings.STATISTICS, action='append',
                      choices=[taxonomy.OCCUPATION, taxonomy.GROUP,
                               taxonomy.FIELD])
pb_query.add_argument(settings.STAT_LMT, type=inputs.int_range(0, 30), required=False)

taxonomy_query = reqparse.RequestParser()
taxonomy_query.add_argument(settings.APIKEY, location='headers', required=True)
taxonomy_query.add_argument(settings.OFFSET, type=int, default=0)
taxonomy_query.add_argument(settings.LIMIT, type=int, default=10)
taxonomy_query.add_argument(settings.FREETEXT_QUERY)
taxonomy_query.add_argument('type', action='append',
                            choices=VF_TYPE_CHOICES),
taxonomy_query.add_argument(settings.SHOW_COUNT, type=inputs.boolean, default=False)
taxonomy_query.add_argument('parent-id', action='append')
