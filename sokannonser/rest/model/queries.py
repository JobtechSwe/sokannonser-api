from flask_restplus import reqparse, inputs
from datetime import datetime
from valuestore import taxonomy
from sokannonser import settings

# Frågemodeller
QF_CHOICES = ['occupation', 'skill', 'location']

swagger_doc_params = {
    settings.APIKEY: "Nyckel som krävs för att använda API:et",
    settings.PUBLISHED_AFTER: "Visa annonser publicerade efter angivet datum "
    "(på formen YYYY-mm-ddTHH:MM:SS)",
    settings.PUBLISHED_BEFORE: "Visa annonser publicerade innan angivet datum "
    "(på formen YYYY-mm-ddTHH:MM:SS)",
    settings.FREETEXT_QUERY: "Fritextfråga",
    settings.FREETEXT_FIELDS: "Välj vilka fält utöver standardfälten (rubrik, "
    "arbetsplatsnamn och annonstext) "
    "som ska användas för fritextfråga "
    "(" + settings.FREETEXT_QUERY + "). Påverkar också "
    "autocomplete (" + settings.TYPEAHEAD_QUERY + ").\n"
    "Alternativ: " + str(QF_CHOICES) + "\n"
    "Default: samtliga",
    taxonomy.OCCUPATION: "En eller flera yrkesbenämningskoder enligt taxonomi",
    taxonomy.GROUP: "En eller flera yrkesgruppskoder enligt taxonomi",
    taxonomy.FIELD: "En eller flera yrkesområdeskoder enligt taxonomi",
    taxonomy.SKILL: "En eller flera kompetenskoder enligt taxonomi",
    taxonomy.DRIVING_LICENCE: "Typ av körkort som efterfrågas (taxonomikod)",
    taxonomy.EMPLOYMENT_TYPE: "Anställningstyp enligt taxonomi",
    settings.EXPERIENCE_REQUIRED: "Sätt till 'false' för att visa enbart jobb "
    "som inte kräver erfarenhet",
    taxonomy.WORKTIME_EXTENT: "En eller flera arbetstidsomfattningskoder enligt "
    "taxonomi",
    settings.PARTTIME_MIN: "För deltidsjobb, minsta omfattning",
    settings.PARTTIME_MAX: "För deltidsjobb, maximal omfattning",
    taxonomy.MUNICIPALITY: "En eller flera kommunkoder",
    taxonomy.REGION: "En eller flera länskoder",
    taxonomy.COUNTRY: "Ett eller flera länder enligt taxonomikod.",
    settings.POSITION: "Latitud och longitud på formen \"59.329, 18.068\" (latitud, longitud).",
    settings.POSITION_RADIUS: "Radie från punkt i km",
}
swagger_filter_doc_params = {
    settings.OFFSET: "Börja lista resultat från denna position "
    "(0-%d)" % settings.MAX_OFFSET,
    settings.LIMIT: "Antal resultat att visa (0-%d)" % settings.MAX_LIMIT,
    settings.SORT: "Sortering.\npubdate-desc: publiceringsdatum, nyast först\n"
    "pubdate-asc: publiceringsdatum, äldst först\n"
    "applydate-desc: sista ansökningsdatum, nyast först\n"
    "applydate-asc: sista ansökningsdatum, äldst först\n"
    "relevance: Relevans (poäng) (default)",
    settings.STATISTICS: "Visa sökstatistik för angivna fält "
    "(tillgängliga fält: %s, %s och %s)" % (
        taxonomy.OCCUPATION,
        taxonomy.GROUP,
        taxonomy.FIELD),
    settings.STAT_LMT: "Antal statistikrader per typ",
}


sok_platsannons_query = reqparse.RequestParser()
sok_platsannons_query.add_argument(settings.APIKEY, location='headers', required=True,
                                   default=settings.APIKEY_BACKDOOR)
sok_platsannons_query.add_argument(settings.PUBLISHED_BEFORE,
                                   type=lambda x: datetime.strptime(x,
                                                                    '%Y-%m-%dT%H:%M:%S'))
sok_platsannons_query.add_argument(settings.PUBLISHED_AFTER,
                                   type=lambda x: datetime.strptime(x,
                                                                    '%Y-%m-%dT%H:%M:%S'))
sok_platsannons_query.add_argument(taxonomy.OCCUPATION, action='append')
sok_platsannons_query.add_argument(taxonomy.GROUP, action='append')
sok_platsannons_query.add_argument(taxonomy.FIELD, action='append')
sok_platsannons_query.add_argument(taxonomy.SKILL, action='append')
sok_platsannons_query.add_argument(taxonomy.WORKTIME_EXTENT, action='append')
sok_platsannons_query.add_argument(settings.PARTTIME_MIN, type=float)
sok_platsannons_query.add_argument(settings.PARTTIME_MAX, type=float)
sok_platsannons_query.add_argument(taxonomy.DRIVING_LICENCE, action='append')
sok_platsannons_query.add_argument(taxonomy.EMPLOYMENT_TYPE, action='append')
sok_platsannons_query.add_argument(settings.EXPERIENCE_REQUIRED,
                                   choices=['true', 'false'])
sok_platsannons_query.add_argument(taxonomy.MUNICIPALITY, action='append')
sok_platsannons_query.add_argument(taxonomy.REGION, action='append')
sok_platsannons_query.add_argument(taxonomy.COUNTRY, action='append')
sok_platsannons_query.add_argument(settings.POSITION,
                                   type=inputs.regex('^[\\d\\.]+, ?[\\d\\.]+$'),
                                   action='append')
sok_platsannons_query.add_argument(settings.POSITION_RADIUS, type=int)
sok_platsannons_query.add_argument(settings.FREETEXT_QUERY)
sok_platsannons_query.add_argument(settings.FREETEXT_FIELDS, action='append',
                                   choices=QF_CHOICES)
pb_query = sok_platsannons_query.copy()
pb_query.add_argument(settings.OFFSET, type=inputs.int_range(0, settings.MAX_OFFSET),
                      default=0)
pb_query.add_argument(settings.LIMIT, type=inputs.int_range(0, settings.MAX_LIMIT),
                      default=10)
pb_query.add_argument(settings.SORT, choices=list(settings.sort_options.keys()))
pb_query.add_argument(settings.STATISTICS, action='append',
                      choices=[taxonomy.OCCUPATION, taxonomy.GROUP,
                               taxonomy.FIELD])
pb_query.add_argument(settings.STAT_LMT, type=inputs.int_range(0, 20), required=False)

auranest_query = reqparse.RequestParser()
auranest_query.add_argument(settings.APIKEY, location='headers', required=True)
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
taxonomy_query.add_argument('parent-id', action='append')
taxonomy_query.add_argument('type',
                            choices=(
                                taxonomy.JobtechTaxonomy.OCCUPATION_NAME,
                                taxonomy.JobtechTaxonomy.OCCUPATION_GROUP,
                                taxonomy.JobtechTaxonomy.OCCUPATION_FIELD,
                                taxonomy.JobtechTaxonomy.SKILL,
                                taxonomy.JobtechTaxonomy.LANGUAGE,
                                taxonomy.JobtechTaxonomy.MUNICIPALITY,
                                taxonomy.JobtechTaxonomy.COUNTY,
                                taxonomy.JobtechTaxonomy.WORKTIME_EXTENT,
                                taxonomy.JobtechTaxonomy.SUN_EDUCATION_FIELD_1,
                                taxonomy.JobtechTaxonomy.SUN_EDUCATION_FIELD_2,
                                taxonomy.JobtechTaxonomy.SUN_EDUCATION_FIELD_3,
                                taxonomy.JobtechTaxonomy.SUN_EDUCATION_LEVEL_1,
                                taxonomy.JobtechTaxonomy.SUN_EDUCATION_LEVEL_2,
                                taxonomy.JobtechTaxonomy.SUN_EDUCATION_LEVEL_3,
                            ))
taxonomy_query.add_argument(settings.SHOW_COUNT, type=bool, default=False)
