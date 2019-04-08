import re
from flask_restplus import fields
from market.rest import ns_market as api


class ShortString(fields.Raw):
    element_pattern = re.compile('<([a-z]+) *[^/]*?>')

    def _find_last_element(self, words):
        for word in reversed(words):
            match = self.element_pattern.findall(word)
            if match:
                return "</%s>" % match[-1]
        return None

    def format(self, value):
        words = re.split(r'\s+', value)
        if len(words) > 100:
            valid_words = words[0:100]
            last_element = self._find_last_element(valid_words)
            new_value = " ".join(valid_words) + " ..."
            if last_element:
                new_value += last_element
        else:
            new_value = value

        return new_value


employer = api.model('Employer', {
    'name': fields.String(),
    'logoUrl': fields.String()
})

site = api.model('Site', {
    'url': fields.String(),
    'name': fields.String()
})

application = api.model('Application', {
    'url': fields.String(),
    'email': fields.String(),
    'deadline': fields.DateTime(),
    'reference': fields.String(),
    'site': fields.Nested(site, attribute='site')
})

keywords = api.model('DetectedKeywords', {
    'occupations': fields.List(fields.String),
    'skills': fields.List(fields.String),
    'traits': fields.List(fields.String)
})

sources = api.model('Sources', {
    'id': fields.String(attribute='_source.id'),
    'name': fields.String(attribute='_source.source.site.name'),
    'url': fields.String(attribute='_source.source.url'),
})

annons = api.model('JobAd', {
    'id': fields.String(attribute='_source.id'),
    'header': fields.String(attribute='_source.header'),
    'content': ShortString(attribute='_source.content.text'),
    'markup': ShortString(attribute='_source.content.xml'),
    'employer': fields.Nested(employer, attribute='_source.employer', skip_none=True),
    'location': fields.String(attribute='_source.location.translations.sv-SE'),
    'application': fields.Nested(application, attribute='_source.application',
                                 skip_none=True),
    'detected_keywords': fields.Nested(keywords, attribute='_source'),
    'sources': fields.List(fields.Nested(sources), attribute='inner_hits.other.hits.hits')
})

stat_value = api.model('StatValue', {
    'value': fields.String(attribute='key'),
    'count': fields.Integer(attribute='doc_count')
})

stats = api.model('Stats', {
    'employers': fields.List(fields.Nested(stat_value),
                             attribute='employers.buckets'),
    'sites': fields.List(fields.Nested(stat_value),
                         attribute='sites.buckets'),
    'locations': fields.List(fields.Nested(stat_value),
                             attribute='locations.buckets'),
})

market_list = api.model('JobAds', {
    'total': fields.Integer(attribute='aggregations.total.value'),
    'stats': fields.Nested(stats, attribute='aggregations', skip_none=True),
    'hits': fields.List(fields.Nested(annons), attribute='hits.hits')
})

# Autocomplete model
autocomplete_list = api.model('AutocompleteResults', {
    'typeahead': fields.List(fields.String)
})
