from datetime import datetime
from flask_restplus import fields, reqparse, inputs
from valuestore import taxonomy
from sokannonser import settings
from sokannonser.rest import ns_platsannons

# Models
# Resultatmodeller
resultat_plats = ns_platsannons.model('Plats', {
    'id': fields.String(attribute='id'),
    'namn': fields.String(attribute='label')
})

resultat_geoposition = ns_platsannons.inherit('GeoPosition', resultat_plats, {
    'longitud': fields.Float(attribute='longitude'),
    'latitud': fields.Float(attribute='latitude')
})

resultat_taxonomi = ns_platsannons.model('TaxonomiEntitet', {
    'kod': fields.String(),
    'term': fields.String()
})


matchande_annons = ns_platsannons.model('MatchandeAnnons', {
    'arbetssokandeprofilId': fields.String(attribute='_source.id'),
    'rubrik': fields.String(attribute='_source.rubrik'),
    'senastModifierad': fields.DateTime(attribute='_source.timestamp'),
    'efterfragadArbetsplats': fields.Nested({
        'land': fields.List(fields.Nested(resultat_plats), attribute='krav.land'),
        'lan': fields.List(fields.Nested(resultat_plats), attribute='krav.lan'),
        'kommun': fields.List(fields.Nested(resultat_plats), attribute='krav.kommun'),
        'geoPosition': fields.List(fields.Nested(resultat_geoposition),
                                   attribute='krav.geoPosition')
    }, attribute='_source', skip_none=True),
    'matchningsresultatKandidat': fields.Nested({
        'efterfragade': fields.Nested({
            'yrke': fields.List(fields.Nested(resultat_taxonomi)),
            'anstallningstyp': fields.List(fields.Nested(resultat_taxonomi)),
            'efterfragade': fields.List(fields.Nested(resultat_taxonomi)),
        }, attribute='krav', skip_none=True),
        'erbjudande': fields.Nested({
            'yrke': fields.List(fields.Nested(resultat_taxonomi)),
            'kompetens': fields.List(fields.Nested(resultat_taxonomi))
        }, attribute='erfarenhet', skip_none=True)
    }, attribute='_source')
})

matchande_annons_simple = ns_platsannons.model('MatchandeAnnons', {
    'annons': fields.Nested({
        'annonsid': fields.String(attribute='id'),
        'platsannons_url': fields.String(attribute='url'),
        'annonsrubrik': fields.String(attribute='rubrik'),
        'annonstext': fields.String(attribute='beskrivning.annonstext'),
        'yrkesbenamning': fields.String(attribute='yrkesroll.term'),
        'yrkesid': fields.String(attribute='yrkesroll.kod'),
        'publiceraddatum': fields.DateTime(attribute='publiceringsdatum'),
        'antal_platser': fields.Integer(attribute='antal_platser'),
        'kommunnamn': fields.String(attribute='arbetsplatsadress.komun'),
        'kommunkod': fields.Integer(attribute='arbetsplatsadress.kommunkod')
    }, attribute='_source', skip_none=True),
    'villkor': fields.Nested({
        'varaktighet': fields.String(attribute='varaktighet.term'),
        'arbetstid': fields.String(attribute='arbetstidstyp.term'),
        'lonetyp': fields.String(attribute='lonetyp.term'),
        'loneform': fields.String(attribute='lonetyp.term')
    }, attribute='_source', skip_none=True),
    'ansokan': fields.Nested({
        'referens': fields.String(attribute='ansokningsdetaljer.referens'),
        'epostadress': fields.String(attribute='ansokningsdetaljer.epost'),
        'sista_ansokningsdag': fields.DateTime(attribute='sista_ansokningsdatum'),
        'ovrigt_om_ansokan': fields.String(attribute='ansokningsdetaljer.annat')
    }, attribute='_source', skip_none=True),
    'arbetsplats': fields.Nested({
        'arbetsplatsnamn': fields.String(attribute='arbetsgivare.arbetsplats'),
        'postnummer': fields.String(attribute='arbetsplatsadress.postnummer'),
        'postadress': fields.String(attribute='arbetsplatsadress.gatuadress'),
        'postort': fields.String(attribute='arbetsplatsadress.postort'),
        'postland': fields.String(attribute='postadress.land'),
        'land': fields.String(attribute='arbetsplatsadress.land.term'),
        'besoksadress': fields.String(attribute='besoksadress.gatuadress'),
        'besoksort': fields.String(attribute='besoksadress.postort'),
        'telefonnummer': fields.String(attribute='arbetsgivare.telefonnummer'),
        'faxnummer': fields.String(attribute='arbetsgivare.faxnummer'),
        'epostadress': fields.String(attribute='arbetsgivare.epost'),
        'hemsida': fields.String(attribute='arbetsgivare.webbadress')
    }, attribute='_source', skip_none=True),
    'krav': fields.Nested({'egen_bil': fields.Boolean(attribute='_source.egen_bil')},
                          skip_none=True)
}, skip_none=True)


pbapi_lista = ns_platsannons.model('Platsannonser', {
    'antal': fields.Integer(attribute='total'),
    'annonser': fields.List(fields.Nested(matchande_annons), attribute='hits')
})

simple_lista = ns_platsannons.model('Platsannonser', {
    'antal_platsannonser': fields.Integer(attribute='total'),
    'platsannonser': fields.List(fields.Nested(matchande_annons_simple), attribute='hits')
})


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
sok_platsannons_query.add_argument(taxonomy.DRIVING_LICENCE, action='append')
sok_platsannons_query.add_argument(taxonomy.EMPLOYMENT_TYPE, action='append')
sok_platsannons_query.add_argument(settings.NO_EXPERIENCE, type=bool, default=False)
# sok_platsannons_query.add_argument(settings.PLACE)
sok_platsannons_query.add_argument(taxonomy.MUNICIPALITY, action='append')
sok_platsannons_query.add_argument(taxonomy.REGION, action='append')
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
auranest_query.add_argument(settings.FREETEXT_QUERY)
auranest_query.add_argument('group_id')

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
