import logging
import json
import time
from datetime import date, timedelta
from io import BytesIO
from zipfile import ZipFile
from elasticsearch.helpers import scan
from sokannonser import settings
from sokannonser.repository import elastic

log = logging.getLogger(__name__)


def _es_dsl():
    dsl = {
        "query": {
            "bool": {
                'filter': [
                    {
                        'range': {
                            'publication_date': {
                                'lte': 'now/m'
                            }
                        }
                    },
                    {
                        'range': {
                            'last_publication_date': {
                                'gte': 'now/m'
                            }
                        }
                    },
                ]
            }
        },
    }
    return dsl


def zip_ads(day, start_time=0):
    if start_time == 0:
        start_time = int(time.time() * 1000)

    dsl = _es_dsl()

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
    scan_result = scan(elastic, dsl, index=settings.ES_INDEX)
    in_memory = BytesIO()
    zf = ZipFile(in_memory, mode="w")

    ads = [remove_enriched_data(ad['_source']) for ad in scan_result]
    log.debug("Number of ads: %d" % len(ads))
    zf.writestr(f"ads_{day}.json", json.dumps(ads))
    zf.close()
    in_memory.seek(0)
    log.debug("File constructed after %d milliseconds."
              % (int(time.time() * 1000) - start_time))
    return in_memory


def convert_to_timestamp(date):
    if not date:
        return None

    ts = 0
    for dateformat in [
        '%Y-%m-%dT%H:%M:%S'
    ]:

        try:
            ts = time.mktime(time.strptime(date, dateformat)) * 1000
            log.debug("Converted date %s to %d" % (date, ts))
            break
        except ValueError as e:
            log.debug("Failed to convert date %s" % date, e)

    return int(ts)


# Generator function
def load_all(since):
    if since == 'yesterday':
        since = (date.today() - timedelta(1)).strftime('%Y-%m-%d')

    ts = time.mktime(since.timetuple()) * 1000

    dsl = _es_dsl()
    dsl['query']['bool']['must'] = [{
        "range": {
            "timestamp": {
                "gte": ts
            }
        }
    }]
    log.debug('load_all, dsl: %s' % dsl)
    scan_result = scan(elastic, dsl, index=settings.ES_INDEX)
    counter = 0
    yield '['
    for ad in scan_result:
        if counter > 0:
            yield ','
        source = ad['_source']
        remove_enriched_data(source)
        yield json.dumps(source)
        counter += 1
    log.info("Delivered %d ads as stream" % counter)
    yield ']'


def remove_enriched_data(source):
    keyword_node = source['keywords']
    try:
        del keyword_node['enriched']
    except KeyError:
        pass
    return source
