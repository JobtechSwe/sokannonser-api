import logging
import json
import time
import zipfile
from flask_restx import Namespace
from datetime import date, timedelta
from io import BytesIO
from elasticsearch.helpers import scan
from sokannonser import settings
from sokannonser.repository import elastic
from sokannonser.rest.model.result_models import job_ad
from sokannonser.repository.querybuilder import calculate_utc_offset

log = logging.getLogger(__name__)
marshaller = Namespace('Marshaller')
offset = calculate_utc_offset()


def _es_dsl():
    dsl = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "publication_date": {
                                "lte": "now/m+%dH/m" % offset
                            }
                        }
                    },
                    {
                        "range": {
                            "last_publication_date": {
                                "gte": "now/m+%dH/m" % offset
                            }
                        }
                    }
                ]
            }
        },
    }
    return dsl


def zip_ads(day, start_time=0):
    if start_time == 0:
        start_time = int(time.time() * 1000)

    dsl = _es_dsl()
    index = settings.ES_STREAM_INDEX if _index_exists(settings.ES_STREAM_INDEX) \
        else settings.ES_INDEX

    if day == 'all':
        dsl['query']['bool']['must'] = [{"match_all": {}}]
    else:
        ts_from = convert_to_timestamp('%sT00:00:00' % str(day))
        ts_to = convert_to_timestamp('%sT23:59:59' % str(day))

        dsl['query']['bool']['must'] = [{
            "range": {
                "timestamp": {
                    "gte": ts_from,
                    "lte": ts_to
                }
            }
        }]
    log.debug('zip_ads, dsl: %s' % dsl)
    scan_result = scan(elastic, dsl, index=index)
    in_memory = BytesIO()
    zf = zipfile.ZipFile(in_memory, "w", zipfile.ZIP_DEFLATED)

    ads = [ad['_source'] for ad in scan_result]
    log.debug("Number of ads: %d" % len(ads))
    zf.writestr(f"ads_{day}.json", json.dumps(ads))
    zf.close()
    in_memory.seek(0)
    log.debug("File constructed after %d milliseconds."
              % (int(time.time() * 1000) - start_time))
    return in_memory


def _index_exists(idx_name):
    return elastic.indices.exists_alias(name=[idx_name]) \
           or elastic.indices.exists(index=[idx_name])


def convert_to_timestamp(day):
    if not day:
        return None

    ts = 0
    for dateformat in [
        '%Y-%m-%dT%H:%M:%S'
    ]:

        try:
            ts = time.mktime(time.strptime(day, dateformat)) * 1000
            log.debug("Converted date %s to %d" % (day, ts))
            break
        except ValueError as e:
            log.debug("Failed to convert date %s" % day, e)

    return int(ts)


# Generator function
def load_all(args):
    since = args.get(settings.DATE)
    # input is not allowed by type=inputs.datetime_from_iso8601
    if since == 'yesterday':
        since = (date.today() - timedelta(1)).strftime('%Y-%m-%d')

    ts = int(time.mktime(since.timetuple())) * 1000
    index = settings.ES_STREAM_INDEX if _index_exists(settings.ES_STREAM_INDEX) \
        else settings.ES_INDEX
    log.debug("Elastic index(load_all): % s" % index)

    dsl = _es_dsl()
    dsl['query']['bool']['must'] = [{
        "range": {
            "timestamp": {
                "gte": ts
            }
        }
    }]

    log.debug('load_all, dsl: %s' % json.dumps(dsl))

    scan_result = scan(elastic, dsl, index=index)
    counter = 0
    yield '['
    for ad in scan_result:
        if counter > 0:
            yield ','
        source = ad['_source']
        if source.get('removed', False):
            yield json.dumps(format_removed_ad(source))
        else:
            yield json.dumps(format_ad(source))
        counter += 1
    log.debug("Delivered %d ads as stream" % counter)
    yield ']'


def add_filter_occupation_query(dsl, occupation_concept_id):
    # add occupation concept id
    occupation_list = ['occupation', 'occupation_field', 'occupation_group']

    should_query = []
    for occupation in occupation_list:
        should_query.append({"term": {
                                "%s.concept_id.keyword" % occupation: occupation_concept_id
                            }})
    dsl['query']['bool']['filter'].append({"bool": {"should": should_query}})
    return dsl


@marshaller.marshal_with(job_ad)
def format_ad(ad_data):
    return ad_data


# @marshaller.marshal_with(removed_job_ad)
def format_removed_ad(ad_data):
    return {
        'id': ad_data.get('id'),
        'removed': ad_data.get('removed'),
        'removed_date': ad_data.get('removed_date'),
        'occupation': ad_data.get('occupation', None).get('concept_id', None),
        'occupation_group': ad_data.get('occupation_group', None).get('concept_id', None),
        'occupation_field': ad_data.get('occupation_field', None).get('concept_id', None),
        'municipality': ad_data.get('workplace_address', None).get('municipality_concept_id', None),
        'region': ad_data.get('workplace_address', None).get('region_concept_id', None),
        'country': ad_data.get('workplace_address', None).get('country_concept_id', None)
    }


def load_snapshot():
    index = settings.ES_STREAM_INDEX if _index_exists(settings.ES_STREAM_INDEX) \
        else settings.ES_INDEX
    dsl = _es_dsl()
    dsl['query']['bool']['filter'].append({"term": {"removed": False}})
    log.debug('QUERY(load_all): %s' % json.dumps(dsl))
    scan_result = scan(elastic, dsl, index=index)
    counter = 0
    yield '['
    for ad in scan_result:
        if counter > 0:
            yield ','
        source = ad['_source']
        yield json.dumps(format_ad(source))
        counter += 1
    log.debug("Delivered %d ads as stream" % counter)
    yield ']'
