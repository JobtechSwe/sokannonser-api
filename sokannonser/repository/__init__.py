import logging
import certifi
from ssl import create_default_context
from elasticsearch import Elasticsearch
from sokannonser import settings
from sokannonser.repository.text_to_concept import TextToConcept

log = logging.getLogger(__name__)

log.info("Using Elasticsearch node at %s:%s" % (settings.ES_HOST, settings.ES_PORT))
if settings.ES_USER and settings.ES_PWD:
    context = create_default_context(cafile=certifi.where())
    elastic = Elasticsearch([settings.ES_HOST], port=settings.ES_PORT,
                            use_ssl=True, scheme='https',
                            ssl_context=context,
                            http_auth=(settings.ES_USER, settings.ES_PWD))
else:
    elastic = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])


ttc = TextToConcept(ontologyhost="https://%s:%s" % (settings.ES_HOST,
                                                    settings.ES_PORT),
                    ontologyuser=settings.ES_USER,
                    ontologypwd=settings.ES_PWD)

