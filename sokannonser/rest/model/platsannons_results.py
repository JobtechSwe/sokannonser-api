from flask_restplus import fields
from sokannonser.rest import ns_platsannons
from sokannonser import settings
from sokannonser.rest.model import fields as f

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


class FormattedUrl(fields.Raw):
    def format(self, value):
        return "%s/ad/%s" % (settings.BASE_URL, value)


# DEPRECATED
matchande_annons = ns_platsannons.model('MatchandeAnnons', {
    'annons': fields.Nested({
        'annonsid': fields.String(attribute=f.ID),
        'annons_url': FormattedUrl(attribute=f.ID),
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

statistics = ns_platsannons.model('Statistik', {
    'typ': fields.String(attribute='type'),
    'poster': fields.List(fields.Nested({
        'term': fields.String(),
        'kod': fields.String(attribute='code'),
        'antal': fields.Integer(attribute='count')
    }), attribute='values')
})

pbapi_lista = ns_platsannons.model('Platsannonser', {
    'antal': fields.Integer(attribute='total'),
    'annonser': fields.List(fields.Nested(matchande_annons), attribute='hits')
})

simple_lista = ns_platsannons.model('Platsannonser', {
    'antal_platsannonser': fields.Integer(attribute='total'),
    'statistik': fields.Nested(statistics, attribute='stats'),
    'platsannonser': fields.List(fields.Nested(matchande_annons), attribute='hits')
})
