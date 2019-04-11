from flask_restplus import reqparse, inputs
from datetime import datetime
from valuestore import taxonomy
from sokannonser import settings

# Frågemodeller
QF_CHOICES = ['occupation', 'skill', 'location']
OPTIONS_BRIEF = 'brief'
OPTIONS_FULL = 'full'

# QUERYFIELDS
ID='id'
EXTERNAL_ID='external_id'
HEADLINE='rubrik'
APPLICATION_DEADLINE='sista_ansokningsdatum'
NUMBER_OF_VACANCIES='antal_platser'
DESCRIPTION_TEXT='beskrivning.annonstext'
DESCRIPTION_COMPANY_INFORMATION='beskrivning.information'
DESCRIPTION_NEEDS='beskrivning.behov'
DESCRIPTION_REQUIREMENTS='beskrivning.krav'
DESCRIPTION_CONDITIONS='beskrivning.villkor'
WORKPLACE_ID='arbetsplats_id'
EMPLOYMENT_TYPE='anstallningstyp'
SALARY_TYPE='lonetyp'
DURATION='varaktighet'
WORKING_HOURS_TYPE='arbetstidstyp'
SCOPE_OF_WORK_MIN='arbetsomfattning.min'
SCOPE_OF_WORK_MAX='arbetsomfattning.max'
ACCESS='tilltrade'
EMPLOYER_ID='arbetsgivare.id'
EMPLOYER_PHONE_NUMBER='arbetsgivare.telefonnummer'
EMPLOYER_EMAIL='arbetsgivare.epost'
EMPLOYER_URL='arbetsgivare.webbadress'
EMPLOYER_ORGANIZATION_NUMBER='arbetsgivare.organisationsnummer'
EMPLOYER_NAME='arbetsgivare.namn'
EMPLOYER_WORKPLACE='arbetsgivare.arbetsplats'
APPLICATION_DETAILS_INFORMATION='ansokningsdetaljer.information'
APPLICATION_DETAILS_REFERENCE='ansokningsdetaljer.referens'
APPLICATION_DETAILS_EMAIL='ansokningsdetaljer.epost'
APPLICATION_DETAILS_VIA_AF='ansokningsdetaljer.via_af'
APPLICATION_DETAILS_URL='ansokningsdetaljer.webbadress'
APPLICATION_DETAILS_OTHER='ansokningsdetaljer.annat'
EXPERIENCE_REQUIRED='erfarenhet_kravs'
ACCESS_TO_OWN_CAR='egen_bil'
DRIVING_LICENCE_REQUIRED='korkort_kravs'
DRIVING_LICENCE='korkort'
OCCUPATION='yrkesroll'
OCCUPATION_GROUP='yrkesgrupp'
OCCUPATION_FIELD='yrkesomrade'
CONCEPT_ID='kod'
LABEL='term'
LEGACY_AMS_TAXONOMY_ID='taxonomi-kod'
WORKPLACE_ADDRESS_MUNICIPALITY_CODE='arbetsplatsadress.kommunkod'
WORKPLACE_ADDRESS_MUNICIPALITY='arbetsplatsadress.kommun'
WORKPLACE_ADDRESS_REGION_CODE='arbetsplatsadress.lanskod'
WORKPLACE_ADDRESS_REGION='arbetsplatsadress.lan'
WORKPLACE_ADDRESS_COUNTRY_CODE='arbetsplatsadress.landskod'
WORKPLACE_ADDRESS_COUNTRY='arbetsplatsadress.land'
WORKPLACE_ADDRESS_STREET_ADDRESS='arbetsplatsadress.gatuadress'
WORKPLACE_ADDRESS_POSTCODE='arbetsplatsadress.postnummer'
WORKPLACE_ADDRESS_CITY='arbetsplatsadress.postort'
WORKPLACE_ADDRESS_COORDINATES='arbetsplatsadress.coordinates'
MUST_HAVE_SKILLS='krav.kompetenser'
MUST_HAVE_LANGUAGES='krav.sprak'
MUST_HAVE_WORK_EXPERIENCES='krav.yrkeserfarenheter'
NICE_TO_HAVE_SKILLS='meriterande.kompetenser'
NICE_TO_HAVE_LANGUAGES='meriterande.sprak'
NICE_TO_HAVE_WORK_EXPERIENCES='meriterande.yrkeserfarenheter'
PUBLICATION_DATE='publiceringsdatum'
LAST_PUBLICATION_DATE='status.sista_publiceringsdatum'
REMOVED='avpublicerad'
REMOVED_DATE='avpubliceringsdatum'
SOURCE_TYPE='kalla'

KEYWORDS_ENRICHED='keywords_enriched_binary'
KEYWORDS_EXTRACTED='keywords'

swagger_doc_params = {
    settings.APIKEY: "Required API key",
    settings.PUBLISHED_AFTER: "Fetch job ads published after specified date and time "
    "(format YYYY-mm-ddTHH:MM:SS)",
    settings.PUBLISHED_BEFORE: "Fetch job ads published before specified date and time "
                               "(format YYYY-mm-ddTHH:MM:SS)",
    settings.FREETEXT_QUERY: "Freetext query. Search in ad headline, ad description and "
                             "place of work.",
    settings.FREETEXT_FIELDS: "Fields to freetext search in, in addition to default "
                              "freetext search "
                              "(parameter " + settings.FREETEXT_QUERY + ").\n"
                              "Valid input values: " + str(QF_CHOICES) + "\n"
                              "Default (no input): Search in ad headline, ad description "
                              "and place of work",
    settings.EMPLOYER: "Name or organisation number (numbers only, no dashes or spaces) "
    "of employer",
    taxonomy.OCCUPATION: "One or more occupational codes according to the taxonomy",
    taxonomy.GROUP: "One or more occupational group codes according to the taxonomy",
    taxonomy.FIELD: "One or more occupational area codes according to the taxonomy",
    taxonomy.SKILL: "One or more competency codes according to the taxonomy",
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
    settings.POSITION: "Latitude and longitude in the format \"59.329, 18.068\" "
                       "(latitude, longitude).",
    settings.POSITION_RADIUS: "Radius from the specified " + settings.POSITION +
    " (latitude, longitude) in kilometers (km)",
}
swagger_filter_doc_params = {
    settings.DETAILS: "Show 'full' (default) or 'brief' results details",
    settings.OFFSET: "The offset parameter defines the offset from the first result you "
    "want to fetch. "
                     "Valid range is (0-%d)" % settings.MAX_OFFSET,
    settings.LIMIT: "Number of results to fetch (0-%d)" % settings.MAX_LIMIT,
    settings.SORT: "Sorting.\npubdate-desc: published date, descending (newest job ad "
    "first)\n"
    "pubdate-asc: published date, ascending (oldest job ad first)\n"
    "applydate-desc: last apply date, descending (newest apply date first)\n"
    "applydate-asc: last apply date, descending (oldest apply date first, few days left "
    "for application)\n"
    "updated: sort by update date (descending)\n"
    "relevance: Relevance (points) (default sorting)",
    settings.STATISTICS: "Show statistics for specified fields "
    "(available fields: %s, %s and %s)" % (
        taxonomy.OCCUPATION,
        taxonomy.GROUP,
        taxonomy.FIELD),
    settings.STAT_LMT: "Maximum number of statistical rows per field",
}


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
annons_complete_query.add_argument(taxonomy.WORKTIME_EXTENT, action='append')
annons_complete_query.add_argument(settings.PARTTIME_MIN, type=float)
annons_complete_query.add_argument(settings.PARTTIME_MAX, type=float)
annons_complete_query.add_argument(taxonomy.DRIVING_LICENCE, action='append')
annons_complete_query.add_argument(taxonomy.EMPLOYMENT_TYPE, action='append')
annons_complete_query.add_argument(settings.EXPERIENCE_REQUIRED,
                                   choices=['true', 'false'])
annons_complete_query.add_argument(taxonomy.MUNICIPALITY, action='append')
annons_complete_query.add_argument(taxonomy.REGION, action='append')
annons_complete_query.add_argument(taxonomy.COUNTRY, action='append')
annons_complete_query.add_argument(settings.POSITION,
                                   type=inputs.regex('^[\\d\\.]+, ?[\\d\\.]+$'),
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
pb_query.add_argument(settings.SORT, choices=list(settings.sort_options.keys()))
pb_query.add_argument(settings.STATISTICS, action='append',
                      choices=[taxonomy.OCCUPATION, taxonomy.GROUP,
                               taxonomy.FIELD])
pb_query.add_argument(settings.STAT_LMT, type=inputs.int_range(0, 20), required=False)

taxonomy_query = reqparse.RequestParser()
taxonomy_query.add_argument(settings.APIKEY, location='headers', required=True)
taxonomy_query.add_argument(settings.OFFSET, type=int, default=0)
taxonomy_query.add_argument(settings.LIMIT, type=int, default=10)
taxonomy_query.add_argument(settings.FREETEXT_QUERY)
taxonomy_query.add_argument('parent-id', action='append')
taxonomy_query.add_argument('type',
                            choices=(
                                taxonomy.JobtechTaxonomy.OCCUPATION_NAME,
                                taxonomy.JobtechTaxonomy.OCCUPATION_GROUP,
                                taxonomy.JobtechTaxonomy.OCCUPATION_FIELD,
                                taxonomy.JobtechTaxonomy.SKILL,
                                taxonomy.JobtechTaxonomy.LANGUAGE,
                                taxonomy.JobtechTaxonomy.MUNICIPALITY,
                                taxonomy.JobtechTaxonomy.REGION,
                                taxonomy.JobtechTaxonomy.COUNTRY,
                                taxonomy.JobtechTaxonomy.WAGE_TYPE,
                                taxonomy.JobtechTaxonomy.EMPLOYMENT_TYPE,
                                taxonomy.JobtechTaxonomy.DRIVING_LICENCE,
                                taxonomy.JobtechTaxonomy.WORKTIME_EXTENT,
                                taxonomy.JobtechTaxonomy.SUN_EDUCATION_FIELD_1,
                                taxonomy.JobtechTaxonomy.SUN_EDUCATION_FIELD_2,
                                taxonomy.JobtechTaxonomy.SUN_EDUCATION_FIELD_3,
                                taxonomy.JobtechTaxonomy.SUN_EDUCATION_LEVEL_1,
                                taxonomy.JobtechTaxonomy.SUN_EDUCATION_LEVEL_2,
                                taxonomy.JobtechTaxonomy.SUN_EDUCATION_LEVEL_3,
                            ))
taxonomy_query.add_argument(settings.SHOW_COUNT, type=bool, default=False)
