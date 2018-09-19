import logging
from elasticsearch import Elasticsearch
from sokannonser import settings

log = logging.getLogger(__name__)

log.info("Using Elasticsearch node at %s:%s" % (settings.ES_HOST, settings.ES_PORT))
if settings.ES_USER and settings.ES_PWD:
    elastic = Elasticsearch([settings.ES_HOST], port=settings.ES_PORT,
                            use_ssl=True, scheme='https', sniff_on_start=False,
                            sniff_on_connection_fail=True, sniffer_timeout=60,
                            http_auth=(settings.ES_USER, settings.ES_PWD))
else:
    elastic = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])
