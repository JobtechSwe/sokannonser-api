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
                            'publiceringsdatum': {
                                'lte': 'now/m'
                            }
                        }
                    },
                    {
                        'range': {
                            'status.sista_publiceringsdatum': {
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
        start_time = int(time.time()*1000)
    if day == 'yesterday':
        day = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    dsl = _es_dsl()
    if day == 'all':
        dsl['query']['bool']['must'] = [{"match_all": {}}]
    else:
        dsl['query']['bool']['must'] = [{
            "range": {
                "status.uppdaterad": {
                    "gte": day,
                    "lte": day
                }
            }
        }]
    scan_result = scan(elastic, dsl, index=settings.ES_INDEX)
    in_memory = BytesIO()
    zf = ZipFile(in_memory, mode="w")

    ads = [ad['_source'] for ad in scan_result]
    log.debug("Number of ads: %d" % len(ads))
    zf.writestr(f"ads_{day}.json", json.dumps(ads))
    zf.close()
    in_memory.seek(0)
    log.debug("File constructed after %d milliseconds."
              % (int(time.time()*1000)-start_time))
    return in_memory


# Generator function
def load_all(since):
    if since == 'yesterday':
        since = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    dsl = _es_dsl()
    dsl['query']['bool']['must'] = [{
        "range": {
            "status.uppdaterad": {
                "gte": since
            }
        }
    }]
    scan_result = scan(elastic, dsl, index=settings.ES_INDEX)
    counter = 0
    yield '['
    for ad in scan_result:
        if counter > 0:
            yield ','
        yield json.dumps(ad['_source'])
        counter += 1
    log.info("Delivered %d ads as stream" % counter)
    yield ']'
