from flask_restplus import fields
from sokannonser.rest import ns_auranest as api


annons = api.model('Ad', {
    'id': fields.String(attribute='_source.id'),
    'header': fields.String(attribute='_source.header'),
    'content': fields.String(attribute='_source.content.text'),
    'employer': fields.Nested({
        'name': fields.String(),
        'logoUrl': fields.String()
    }, attribute='employer', skip_none=True),
    'location': fields.String(attribute='_source.location.translations.sv-SE'),
    'application': fields.Nested({
        'url': fields.String(),
        'email': fields.String(),
        'deadline': fields.DateTime(),
        'reference': fields.String(),
        'site': fields.Nested({
            'url': fields.String(),
            'name': fields.String()
        }, attribute='site')
    }, attribute='_source.application', skip_none=True),
    'sources': fields.List(fields.Nested({
        'name': fields.String(attribute='_source.source.site.name'),
        'url': fields.String(attribute='_source.source.url')
    }), attribute='inner_hits.other.hits.hits')
})

stat_value = api.model('StatValue', {
    'value': fields.String(attribute='key'),
    'count': fields.Integer(attribute='doc_count')
})

auranest_lista = api.model('Ads', {
    'total': fields.Integer(attribute='hits.total'),
    'stats': fields.Nested({
        'employers': fields.List(fields.Nested(stat_value),
                                 attribute='employers.buckets'),
        'sites': fields.List(fields.Nested(stat_value),
                             attribute='sites.buckets'),
        'locations': fields.List(fields.Nested(stat_value),
                                 attribute='locations.buckets'),
    }, attribute='aggregations', skip_none=True),
    'hits': fields.List(fields.Nested(annons), attribute='hits.hits')
})

