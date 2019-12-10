from flask_restplus import fields
from sokannonser.rest import ns_platsannons
from sokannonser import settings
from sokannonser.rest.model import fields as f

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

typeahead_item = ns_platsannons.model('TypeaheadItem', {
    'value': fields.String(),
    'found_phrase': fields.String(),
    'type': fields.String(),
    'occurrences': fields.Integer()
})

typeahead_results = ns_platsannons.model('TypeaheadResults', {
    'time_in_millis': fields.Integer(),
    'typeahead': fields.List(fields.Nested(typeahead_item))
})


class AdUrl(fields.Raw):
    def format(self, value):
        if settings.BASE_PB_URL[-1] == '/':
            return "%s%s" % (settings.BASE_PB_URL, value)
        else:
            return "%s/%s" % (settings.BASE_PB_URL, value)


# Result model v1
taxonomy_item = ns_platsannons.model('JobTechTaxonomyItem', {
    'concept_id': fields.String(),
    'label': fields.String(),
    'legacy_ams_taxonomy_id': fields.String()
})

weighted_taxonomy_item = ns_platsannons.inherit('WeightedJobtechTaxonomyItem',
                                                taxonomy_item, {
                                                    'weight': fields.Integer()
                                                })

min_max = ns_platsannons.model('ScopeOfWork', {
    'min': fields.Integer(),
    'max': fields.Integer()
})

description = ns_platsannons.model('JobAdDescription', {
    'text': fields.String(),
    'company_information': fields.String(),
    'needs': fields.String(),
    'requirements': fields.String(),
    'conditions': fields.String()
})

employer = ns_platsannons.model('Employer', {
    'phone_number': fields.String(),
    'email': fields.String(),
    'url': fields.String(),
    'organization_number': fields.String(),
    'name': fields.String(),
    'workplace': fields.String()
})

appl_details = ns_platsannons.model('ApplicationDetails', {
    'information': fields.String(),
    'reference': fields.String(),
    'email': fields.String(),
    'via_af': fields.Boolean(),
    'url': fields.String(),
    'other': fields.String()
})

work_address = ns_platsannons.model('WorkplaceAddress', {
    'municipality_code': fields.String(),
    'municipality': fields.String(),
    'region_code': fields.String(),
    'region': fields.String(),
    'country_code': fields.String(),
    'country': fields.String(),
    'street_address': fields.String(),
    'postcode': fields.String(),
    'city': fields.String(),
    'coordinates': fields.List(fields.Float())
})

requirements = ns_platsannons.model('Requirements', {
    'skills': fields.List(fields.Nested(weighted_taxonomy_item)),
    'languages': fields.List(fields.Nested(weighted_taxonomy_item)),
    'work_experiences': fields.List(fields.Nested(weighted_taxonomy_item)),
})

job_ad = ns_platsannons.model('JobAd', {
    f.ID: fields.String(),
    f.EXTERNAL_ID: fields.String(),
    f.AD_URL: AdUrl(attribute='id'),
    f.LOGO_URL: fields.String(),
    f.HEADLINE: fields.String(),
    f.APPLICATION_DEADLINE: fields.DateTime(),
    f.NUMBER_OF_VACANCIES: fields.Integer(),
    'description': fields.Nested(description),
    'employment_type': fields.Nested(taxonomy_item),
    'salary_type': fields.Nested(taxonomy_item),
    'salary_description': fields.String(),
    'duration': fields.Nested(taxonomy_item),
    'working_hours_type': fields.Nested(taxonomy_item),
    'scope_of_work': fields.Nested(min_max),
    f.ACCESS: fields.String(),
    'employer': fields.Nested(employer),
    'application_details': fields.Nested(appl_details),
    f.EXPERIENCE_REQUIRED: fields.Boolean(),
    f.ACCESS_TO_OWN_CAR: fields.Boolean(),
    f.DRIVING_LICENCE_REQUIRED: fields.Boolean(),
    'driving_license': fields.List(fields.Nested(taxonomy_item, skip_none=True)),
    'occupation': fields.Nested(taxonomy_item),
    'occupation_group': fields.Nested(taxonomy_item),
    'occupation_field': fields.Nested(taxonomy_item),
    'workplace_address': fields.Nested(work_address),
    'must_have': fields.Nested(requirements),
    'nice_to_have': fields.Nested(requirements),
    f.PUBLICATION_DATE: fields.DateTime(),
    f.LAST_PUBLICATION_DATE: fields.DateTime(),
    f.REMOVED: fields.Boolean(),
    f.REMOVED_DATE: fields.DateTime(),
    f.SOURCE_TYPE: fields.String(),
    'timestamp': fields.Integer(),
})

job_ad_searchresult = ns_platsannons.inherit('JobAdSearchResult', job_ad, {
    'relevance': fields.Float(),
})

stat_item = ns_platsannons.model('StatDetail', {
    'term': fields.String(),
    'code': fields.String(),
    'count': fields.Integer()
})

search_stats = ns_platsannons.model('Stats', {
    'type': fields.String(),
    'values': fields.List(fields.Nested(stat_item, skip_none=True))
})

freetext_concepts = ns_platsannons.model('FreetextConcepts', {
    'skill': fields.List(fields.String()),
    'occupation': fields.List(fields.String()),
    'location': fields.List(fields.String()),
    'skill_must': fields.List(fields.String()),
    'occupation_must': fields.List(fields.String()),
    'location_must': fields.List(fields.String()),
    'skill_must_not': fields.List(fields.String()),
    'occupation_must_not': fields.List(fields.String()),
    'location_must_not': fields.List(fields.String()),
})

number_of_hits = ns_platsannons.model('NumberOfHits', {
    'value': fields.Integer()
})

open_results = ns_platsannons.model('SearchResults', {
    'total': fields.Nested(number_of_hits),
    'positions': fields.Integer(),
    'query_time_in_millis': fields.Integer(),
    'result_time_in_millis': fields.Integer(),
    'stats': fields.List(fields.Nested(search_stats, skip_none=True)),
    'freetext_concepts': fields.Nested(freetext_concepts, skip_none=True),
    'hits': fields.List(fields.Nested(job_ad_searchresult), attribute='hits', skip_none=True)
})

# Resultmodel v2 JobPosting
