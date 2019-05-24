import logging
import json
from sokannonser import settings
from sokannonser.repository import elastic
from sokannonser.rest.model import fields

log = logging.getLogger(__name__)


def lista_lan(listnamn):
    (antal_annons, antal_plats) = _get_total_hits(
        {
            'bool': {
                'must': {
                    'term': {
                        fields.WORKPLACE_ADDRESS_COUNTRY_CODE: "199"
                    }
                }
            }
        })
    lanlista = _load_taxonomy("region", None, None,
                              fields.WORKPLACE_ADDRESS_REGION_CODE, 2)
    return _build_list("lan", antal_annons, antal_plats, lanlista)


def lista_lan2(listnamn):
    (antal_annons, antal_plats) = _get_total_hits()
    lanlista = _load_taxonomy("region", None, None,
                              fields.WORKPLACE_ADDRESS_REGION_CODE, 2)
    (annons_utomlands, plats_utomlands) = _get_total_hits(
        {
            'bool': {
                'must_not': {
                    'term': {
                        fields.WORKPLACE_ADDRESS_COUNTRY_CODE: "199"
                    }
                }
            }
        }
    )
    (annons_ospec, plats_ospec) = _get_total_hits({
                    'term': {
                        fields.WORKPLACE_ADDRESS_REGION_CODE: "90"
                    }
                })
    lanlista.append({'id': 90, 'namn': 'Ospecificed arbetsort',
                     'antal_platsannonser': annons_ospec,
                     'antal_ledigajobb': plats_ospec})
    lanlista.append({'id': 199, 'namn': 'Utomlands',
                     'antal_platsannonser': annons_utomlands,
                     'antal_ledigajobb': plats_utomlands})
    return _build_list("lan2", antal_annons, antal_plats, lanlista)


def lista_kommuner(lansid):
    (antal_annons, antal_plats) = _get_total_hits({
        "term": {
            fields.WORKPLACE_ADDRESS_REGION_CODE: f"{lansid:02d}"
        }
    })
    return _build_list("kommuner", antal_annons, antal_plats,
                       _load_taxonomy("municipality",
                                      "parent.legacy_ams_taxonomy_num_id",
                                      lansid,
                                      fields.WORKPLACE_ADDRESS_MUNICIPALITY_CODE, 4))


def lista_yrkesomraden():
    (antal_annons, antal_plats) = _get_total_hits()
    return _build_list("yrkesomraden", antal_annons, antal_plats,
                       _load_taxonomy("occupation-field", None, None,
                                      fields.OCCUPATION_FIELD+".legacy_ams_taxonomy_id"))


def lista_yrkesgrupper(yrkesomradeid):
    omrade_field = fields.OCCUPATION_FIELD + ".legacy_ams_taxonomy_id"
    grupp_field = fields.OCCUPATION_GROUP + ".legacy_ams_taxonomy_id"
    (antal_annons, antal_plats) = _get_total_hits(
        {"term": {omrade_field: yrkesomradeid}}
    )
    return _build_list("yrkesgrupper", antal_annons, antal_plats,
                       _load_taxonomy("occupation-group",
                                      "parent.legacy_ams_taxonomy_num_id",
                                      yrkesomradeid, grupp_field))


def lista_yrken(yrkesgruppid):
    grupp_field = fields.OCCUPATION_GROUP + ".legacy_ams_taxonomy_id"
    yrke_field = fields.OCCUPATION + ".legacy_ams_taxonomy_id"
    (antal_annons, antal_plats) = _get_total_hits(
        {"term": {grupp_field: yrkesgruppid}}
    )
    return _build_list("yrken", antal_annons, antal_plats,
                       _load_taxonomy("occupation-name",
                                      "parent.legacy_ams_taxonomy_num_id",
                                      yrkesgruppid, yrke_field))


def lista_yrken_by_string(benamning):
    yrke_field = fields.OCCUPATION + ".label"
    (antal_annons, antal_plats) = _get_total_hits(
        {"prefix": {yrke_field: benamning}}
    )
    return _build_list("yrken", antal_annons, antal_plats,
                       _load_taxonomy("occupation-name",
                                      None,
                                      None,
                                      fields.OCCUPATION + ".legacy_ams_taxonomy_id",
                                      0,
                                      benamning))


def _build_list(listnamn, antal_annons, antal_plats, sokdata):
    return {
        'soklista': {
            "listnamn": listnamn,
            "totalt_antal_platsannonser": antal_annons,
            "totalt_antal_ledigajobb": antal_plats,
            "sokdata": sokdata
        }
    }


def _load_taxonomy(taxtype, key, value, jobad_field, zero_fill=0, label_string=None):
    dsl = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"type": taxtype}},
                ]
            }
        },
        "size": 500
    }
    if key and value:
        dsl['query']['bool']['must'].append({"term": {key: value}})
    if label_string:
        dsl['query']['bool']['must'].append({"prefix": {"label": label_string}})

    log.debug("TAXONOMY DSL: %s" % json.dumps(dsl))
    result = elastic.search(index=settings.ES_TAX_INDEX, body=dsl)
    taxonomy_list = [{'id': hit['_source']['legacy_ams_taxonomy_num_id'],
                      'namn': hit['_source']['label']}
                     for hit in result.get('hits', {}).get('hits', [])]

    for entry in taxonomy_list:
        (a, p) = _get_total_hits(
            {
                'term': {
                    jobad_field: str(entry['id']).zfill(zero_fill)
                }
            }
        )
        entry['antal_platsannonser'] = a
        entry['antal_ledigajobb'] = p

    return taxonomy_list


def _get_total_hits(query={"match_all": {}}):
    dsl = {
        "query": query,
        "size": 0,
        "track_total_hits": True,
        "aggs": {
            "positions": {
                "sum": {"field": fields.NUMBER_OF_VACANCIES}
            }
        }
    }
    log.debug("TOTAL HITS DSL: %s" % json.dumps(dsl))
    result = elastic.search(index=settings.ES_INDEX, body=dsl)
    return (result.get('hits', {}).get('total', {}).get('value', 0),
            int(result.get('aggregations', {}).get('positions', {}).get('value', 0)))
