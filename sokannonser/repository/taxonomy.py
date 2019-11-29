import logging
import os
import json
from elasticsearch.exceptions import RequestError

log = logging.getLogger(__name__)

ES_TAX_INDEX = os.getenv('ES_TAX_INDEX', 'taxonomy')
taxonomy_cache = {}

# Swedish Constants (not used)
OCCUPATION_SV = 'yrkesroll'
GROUP_SV = 'yrkesgrupp'
FIELD_SV = 'yrkesomrade'
SKILL_SV = 'kompetens'
PLACE_SV = 'plats'
MUNICIPALITY_SV = 'kommun'
REGION_SV = 'lan'
COUNTRY_SV = 'land'
LANGUAGE_SV = 'sprak'
WORKTIME_EXTENT_SV = 'arbetstidsomfattning'
EMPLOYMENT_TYPE_SV = 'anstallningstyp'
DRIVING_LICENCE_SV = 'korkort'
WAGE_TYPE_SV = 'lonetyp'
EDUCATION_LEVEL_SV = 'utbildningsniva'
EDUCATION_FIELD_SV = 'utbildningsinriktning'
DURATION_SV = 'varaktighet'
OCCUPATION_EXPERIENCE_SV = 'erfarenhetsniva'

# English Constants
OCCUPATION = 'occupation-name'
GROUP = 'occupation-group'
FIELD = 'occupation-field'
SKILL = 'skill'
PLACE = 'place'
MUNICIPALITY = 'municipality'
REGION = 'region'
COUNTRY = 'country'
LANGUAGE = 'language'
WORKTIME_EXTENT = 'worktime-extent'
EMPLOYMENT_TYPE = 'employment-type'
DRIVING_LICENCE = 'driving-license'
DRIVING_LICENCE_REQUIRED = 'driving-license-required'
WAGE_TYPE = 'wage-type'
EDUCATION_LEVEL = 'educationlevel'
DEPRECATED_EDUCATION_LEVEL = 'deprecated_educationlevel'
EDUCATION_FIELD = 'educationfield'
DEPRECATED_EDUCATION_FIELD = 'deprecated_educationfield'
DURATION = 'employment-duration'
OCCUPATION_EXPERIENCE = 'experience'


class JobtechTaxonomy:
    REGION = 'region'
    COUNTRY = 'country'
    DEPRECATED_EDUCATION_LEVEL = 'deprecated-education-level'
    DEPRECATED_EDUCATION_FIELD = 'deprecated-education-field'
    DRIVING_LICENCE = 'driving-license'
    EMPLOYMENT_DURATION = 'employment-duration'
    EMPLOYMENT_TYPE = 'employment-type'
    LANGUAGE = 'language'
    MUNICIPALITY = 'municipality'
    OCCUPATION_GROUP = 'occupation-group'
    OCCUPATION_EXPERIENCE_YEARS = 'occupation-experience-years'
    OCCUPATION_FIELD = 'occupation-field'
    OCCUPATION_NAME = 'occupation-name'
    SKILL = 'skill'
    SUN_EDUCATION_LEVEL_1 = 'sun-education-level-1'
    SUN_EDUCATION_LEVEL_2 = 'sun-education-level-2'
    SUN_EDUCATION_LEVEL_3 = 'sun-education-level-3'
    SUN_EDUCATION_FIELD_1 = 'sun-education-field-1'
    SUN_EDUCATION_FIELD_2 = 'sun-education-field-2'
    SUN_EDUCATION_FIELD_3 = 'sun-education-field-3'
    WAGE_TYPE = 'wage-type'
    WORKTIME_EXTENT = 'worktime-extent'


tax_type = {
    OCCUPATION: JobtechTaxonomy.OCCUPATION_NAME,
    OCCUPATION_SV: JobtechTaxonomy.OCCUPATION_NAME,
    'yrkesroll': JobtechTaxonomy.OCCUPATION_NAME,
    GROUP: JobtechTaxonomy.OCCUPATION_GROUP,
    GROUP_SV: JobtechTaxonomy.OCCUPATION_GROUP,
    FIELD: JobtechTaxonomy.OCCUPATION_FIELD,
    FIELD_SV: JobtechTaxonomy.OCCUPATION_FIELD,
    SKILL: JobtechTaxonomy.SKILL,
    SKILL_SV: JobtechTaxonomy.SKILL,
    MUNICIPALITY: JobtechTaxonomy.MUNICIPALITY,
    MUNICIPALITY_SV: JobtechTaxonomy.MUNICIPALITY,
    REGION: JobtechTaxonomy.REGION,
    REGION_SV: JobtechTaxonomy.REGION,
    COUNTRY: JobtechTaxonomy.COUNTRY,
    COUNTRY_SV: JobtechTaxonomy.COUNTRY,
    WORKTIME_EXTENT: JobtechTaxonomy.WORKTIME_EXTENT,
    WORKTIME_EXTENT_SV: JobtechTaxonomy.WORKTIME_EXTENT,
    PLACE: 'place',
    PLACE_SV: 'place',
    LANGUAGE: JobtechTaxonomy.LANGUAGE,
    LANGUAGE_SV: JobtechTaxonomy.LANGUAGE,
    EMPLOYMENT_TYPE: JobtechTaxonomy.EMPLOYMENT_TYPE,
    EMPLOYMENT_TYPE_SV: JobtechTaxonomy.EMPLOYMENT_TYPE,
    DRIVING_LICENCE: JobtechTaxonomy.DRIVING_LICENCE,
    DRIVING_LICENCE_SV: JobtechTaxonomy.DRIVING_LICENCE,
    WAGE_TYPE: JobtechTaxonomy.WAGE_TYPE,
    WAGE_TYPE_SV: JobtechTaxonomy.WAGE_TYPE,
    EDUCATION_LEVEL: JobtechTaxonomy.DEPRECATED_EDUCATION_LEVEL,
    EDUCATION_LEVEL_SV: JobtechTaxonomy.DEPRECATED_EDUCATION_LEVEL,
    EDUCATION_FIELD: JobtechTaxonomy.DEPRECATED_EDUCATION_FIELD,
    EDUCATION_FIELD_SV: JobtechTaxonomy.DEPRECATED_EDUCATION_FIELD,
    DURATION: JobtechTaxonomy.EMPLOYMENT_DURATION,
    DURATION_SV: JobtechTaxonomy.EMPLOYMENT_DURATION,
    OCCUPATION_EXPERIENCE: JobtechTaxonomy.OCCUPATION_EXPERIENCE_YEARS,
    OCCUPATION_EXPERIENCE_SV: JobtechTaxonomy.OCCUPATION_EXPERIENCE_YEARS,
}

reverse_tax_type = {item[1]: item[0] for item in tax_type.items()}

annons_key_to_jobtech_taxonomy_key = {
    'yrkesroll': JobtechTaxonomy.OCCUPATION_NAME,
    OCCUPATION: JobtechTaxonomy.OCCUPATION_NAME,
    GROUP: JobtechTaxonomy.OCCUPATION_GROUP,
    FIELD: JobtechTaxonomy.OCCUPATION_FIELD,
    OCCUPATION_SV: JobtechTaxonomy.OCCUPATION_NAME,
    GROUP_SV: JobtechTaxonomy.OCCUPATION_GROUP,
    FIELD_SV: JobtechTaxonomy.OCCUPATION_FIELD,
    'anstallningstyp': JobtechTaxonomy.EMPLOYMENT_TYPE,
    'lonetyp': JobtechTaxonomy.WAGE_TYPE,
    'varaktighet': JobtechTaxonomy.EMPLOYMENT_DURATION,
    'arbetstidstyp': JobtechTaxonomy.WORKTIME_EXTENT,
    'kommun': JobtechTaxonomy.MUNICIPALITY,
    'lan': JobtechTaxonomy.REGION,
    'land': JobtechTaxonomy.COUNTRY,
    'korkort': JobtechTaxonomy.DRIVING_LICENCE,
    'kompetens': JobtechTaxonomy.SKILL,
    SKILL: JobtechTaxonomy.SKILL,
    SKILL_SV: JobtechTaxonomy.SKILL,
    'sprak': JobtechTaxonomy.LANGUAGE,
    'deprecated_educationlevel': JobtechTaxonomy.DEPRECATED_EDUCATION_LEVEL,
    'deprecated_educationfield': JobtechTaxonomy.DEPRECATED_EDUCATION_FIELD,
}


def _build_query(query_string, taxonomy_code, entity_type, offset, limit):
    musts = []
    sort = None
    if query_string:
        musts.append({"bool": {"should": [
            {
                "match_phrase_prefix": {
                    "label": {
                        "query": query_string
                    }
                }
            },
            {
                "term": {
                    "concept_id": {"value": query_string}
                }
            },
            {
                "term": {
                    "legacy_ams_taxonomy_id": {"value": query_string}
                }
            }
        ]}})
    else:
        # Sort numerically for non-query_string-queries
        sort = [
            {
                "legacy_ams_taxonomy_num_id": {"order": "asc"}
            }
        ]
    if taxonomy_code:
        if not isinstance(taxonomy_code, list):
            taxonomy_code = [taxonomy_code]
        terms = [{"term": {"parent.legacy_ams_taxonomy_id": t}} for t in taxonomy_code]
        terms += [{"term": {"parent.concept_id.keyword": t}} for t in taxonomy_code]
        terms += [{"term":
                   {"parent.parent.legacy_ams_taxonomy_id": t}
                   } for t in taxonomy_code]
        terms += [{"term":
                   {"parent.parent.concept_id.keyword": t}
                   } for t in taxonomy_code]
        parent_or_grandparent = {"bool": {"should": terms}}
        # musts.append({"term": {"parent.id": taxonomy_code}})
        musts.append(parent_or_grandparent)
    if entity_type:
        musts.append({"bool": {"should": [{"term": {"type": et}} for et in entity_type]}})
        # musts.append({"term": {"type": entity_type}})

    if not musts:
        query_dsl = {"query": {"match_all": {}}, "from": offset, "size": limit}
    else:
        query_dsl = {
                "query": {
                    "bool": {
                        "must": musts
                    }
                },
                "from": offset,
                "size": limit
            }
    if sort:
        query_dsl['sort'] = sort

    query_dsl['track_total_hits'] = True
    log.debug(json.dumps(query_dsl))
    return query_dsl


def get_term(elastic_client, taxtype, taxid):
    if taxtype not in taxonomy_cache:
        taxonomy_cache[taxtype] = {}
    if taxid in taxonomy_cache[taxtype]:
        return taxonomy_cache[taxtype][taxid]
    taxonomy_entity = find_concept_by_legacy_ams_taxonomy_id(elastic_client,
                                                             taxtype, taxid, {})
    label = None
    if 'label' in taxonomy_entity:
        label = taxonomy_entity['label']
    if 'term' in taxonomy_entity:
        label = taxonomy_entity['term']
    taxonomy_cache[taxtype][taxid] = label
    return label


def get_entity(elastic_client, taxtype, taxid, not_found_response=None):

    # old version doc_id = "%s-%s" % (taxtype_legend.get(taxtype, ''), taxid)
    doc_id = taxid  # document id changed from type-id format to just the concept_id
    taxonomy_entity = elastic_client.get_source(index=ES_TAX_INDEX,
                                                id=doc_id,
                                                doc_type='_all', ignore=404)
    if not taxonomy_entity:
        log.warning("No taxonomy entity found for type %s and id %s (%s)" % (taxtype,
                                                                             taxid,
                                                                             doc_id))
        return not_found_response
    return taxonomy_entity


def find_concept_by_legacy_ams_taxonomy_id(elastic_client, taxonomy_type,
                                           legacy_ams_taxonomy_id,
                                           not_found_response=None):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"legacy_ams_taxonomy_id": {
                        "value": legacy_ams_taxonomy_id}}},
                    {"term": {
                        "type": {
                            "value": annons_key_to_jobtech_taxonomy_key.get(taxonomy_type,
                                                                            '')
                        }
                    }}
                ]
            }
        }
    }
    try:
        elastic_response = elastic_client.search(index=ES_TAX_INDEX, body=query)
    except RequestError as e:
        log.warning("RequestError", str(e))
        return not_found_response

    hits = elastic_response.get('hits', {}).get('hits', [])
    if not hits:
        log.warning("No taxonomy entity found for type %s and "
                    "legacy id %s" % (taxonomy_type,
                                      legacy_ams_taxonomy_id))
        return not_found_response
    return hits[0]['_source']


def find_concepts(elastic_client, query_string=None, taxonomy_code=[], entity_type=[],
                  offset=0, limit=10):
    query_dsl = _build_query(query_string, taxonomy_code, entity_type, offset, limit)
    log.debug("Query: %s" % json.dumps(query_dsl))
    try:
        elastic_response = elastic_client.search(index=ES_TAX_INDEX, body=query_dsl)
        log.debug("Find concepts response metrics: took: %s, timed_out: %s" %
                  (elastic_response.get('took', ''),
                   elastic_response.get('timed_out', '')))
        return elastic_response
    except RequestError:
        log.error("Failed to query Elasticsearch")
        return None


def format_response(elastic_response):
    response = {
            "antal": elastic_response.get('hits', {}).get('total'),
            "entiteter": []
            }
    for sourcehit in elastic_response.get('hits', {}).get('hits', []):
        hit = sourcehit['_source']
        response['entiteter'].append({"kod": hit['legacy_ams_taxonomy_id'],
                                      "term": hit['label'],
                                      "typ": hit['type']})

    return response
