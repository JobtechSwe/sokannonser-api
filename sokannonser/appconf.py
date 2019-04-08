import logging
from jobtech.common.customlogging import JobtechLogFormatter
from sokannonser import settings
import os
from elasticapm.contrib.flask import ElasticAPM


log = logging.getLogger(__name__)


def configure_logging():
    logging.basicConfig()
    # Remove basicConfig-handlers and replace with custom formatter.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    stream_handler = logging.StreamHandler()

    f = create_log_formatter()
    stream_handler.setFormatter(f)
    root = logging.getLogger()
    # root.setLevel(logging.INFO)
    root.addHandler(stream_handler)

    set_custom_log_level()


def create_log_formatter():
    if os.getenv('FLASK_ENV', '') == 'development':
        is_develop_mode = True
    else:
        is_develop_mode = False
    f = JobtechLogFormatter('%(asctime)s|%(levelname)s|%(name)s|MESSAGE: %(message)s',
                            '%Y-%m-%d %H:%M:%S%z', is_develop_mode=is_develop_mode)
    return f


def set_custom_log_level():
    # Set log level debug for module specific events
    # and level warning for all third party dependencies
    for key in logging.Logger.manager.loggerDict:
        # for handler in logging.getLogger(key).handlers[:]:
        #     logging.getLogger(key).removeHandler(handler)
        if key.startswith(__name__) or key.startswith('valuestore'):
            logging.getLogger(key).setLevel(logging.DEBUG)

        else:
            logging.getLogger(key).setLevel(logging.WARNING)


# NarvalLogFormatter.printTestLogMessages(log)


def configure_app(flask_app):
    flask_app.config.SWAGGER_UI_DOC_EXPANSION = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config.RESTPLUS_VALIDATE = settings.RESTPLUS_VALIDATE
    flask_app.config.RESTPLUS_MASK_SWAGGER = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config.ERROR_404_HELP = settings.RESTPLUS_ERROR_404_HELP
    if settings.APM_SERVICE_NAME and settings.APM_SERVICE_URL and settings.APM_SECRET:
        flask_app.config['ELASTIC_APM'] = {
            'SERVICE_NAME': settings.APM_SERVICE_NAME,
            'SERVER_URL': settings.APM_SERVICE_URL,
            'SECRET_TOKEN': settings.APM_SECRET
        }
        apm = ElasticAPM(flask_app, logging=logging.INFO)
        log.info("ElasticAPM enabled")
        log.debug("APM details: %s" % str(apm))
    else:
        log.info("ElasticAPM is disabled")


def initialize_app(flask_app, api):
    configure_app(flask_app)
    api.init_app(flask_app)
