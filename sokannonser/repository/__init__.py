import logging
from elasticsearch import Elasticsearch
from sokannonser import settings

log = logging.getLogger(__name__)

log.info("Using Elasticsearch node at %s:%s" % (settings.ES_HOST, settings.ES_PORT))
elastic = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])
