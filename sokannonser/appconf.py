import logging
from sokannonser import settings
from elasticapm.contrib.flask import ElasticAPM


log = logging.getLogger(__name__)


def configure_app(flask_app):
    flask_app.config.SWAGGER_UI_DOC_EXPANSION = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config.RESTPLUS_VALIDATE = settings.RESTPLUS_VALIDATE
    flask_app.config.RESTPLUS_MASK_SWAGGER = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config.ERROR_404_HELP = settings.RESTPLUS_ERROR_404_HELP
    if settings.APM_SERVICE_NAME and settings.APM_SERVICE_URL and settings.APM_SECRET:
        flask_app.config['ELASTIC_APM'] = {
            'SERVICE_NAME': settings.APM_SERVICE_NAME,
            'SERVER_URL': settings.APM_SERVICE_URL,
            'SECRET_TOKEN': settings.APM_SECRET,
            'COLLECT_LOCAL_VARIABLES': 'off',
            # regex to ignore specific routes
            'TRANSACTIONS_IGNORE_PATTERNS': ['^OPTIONS ', '^HEAD ', '^.*\/\s*$', '.*swagger']
        }
        apm = ElasticAPM(flask_app, logging=settings.APM_LOG_LEVEL)
        apm.capture_message('hello, apm!')
        log.info("ElasticAPM enabled")
        log.debug("APM details: %s, log level: %s" % (str(apm), settings.APM_LOG_LEVEL))
    else:
        log.info("ElasticAPM is disabled")


def initialize_app(flask_app, api):
    configure_app(flask_app)
    api.init_app(flask_app)
