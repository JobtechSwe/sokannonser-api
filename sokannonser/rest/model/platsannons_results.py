from flask_restplus import fields
from sokannonser.rest import ns_platsannons
from sokannonser import settings

# Platsannonser
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
    'senastModifierad': fields.String(attribute='_source.timestamp'),
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


class FormattedUrl(fields.Raw):
    def format(self, value):
        return "%s/af/ad/%s" % (settings.BASE_URL, value)


matchande_annons_simple = ns_platsannons.model('MatchandeAnnons', {
    'annons': fields.Nested({
        'annonsid': fields.String(attribute='id'),
        'annons_url': FormattedUrl(attribute='id'),
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
