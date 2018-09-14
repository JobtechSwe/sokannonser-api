import logging
import json
from sokannonser import settings
from sokannonser.repository import elastic

log = logging.getLogger(__name__)


def find_annonser(args):
    query_dsl = _parse_args(args)
    log.debug(json.dumps(query_dsl, indent=2))
    query_result = elastic.search(index=settings.ES_AURANEST, body=query_dsl)
    return query_result


def _parse_args(args):
    return {}
