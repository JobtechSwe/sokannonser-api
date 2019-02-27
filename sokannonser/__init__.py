import logging
from sokannonser.customlogging import NarvalLogFormatter
from flask import Flask
from flask_cors import CORS
from sokannonser.rest import api
from sokannonser.rest.endpoint.auranest import AuranestSearch
from sokannonser.rest.endpoint.platsannonser import PBSearch
from sokannonser.rest.endpoint.openapi import OpenSearch, Proxy
from sokannonser.rest.endpoint.valuestore import Valuestore
from sokannonser import settings
import os
from elasticapm.contrib.flask import ElasticAPM

app = Flask(__name__)
CORS(app)


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
    f = NarvalLogFormatter('%(asctime)s|%(levelname)s|%(name)s|MESSAGE: %(message)s', '%Y-%m-%d %H:%M:%S%z',
                           is_develop_mode=is_develop_mode)
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


configure_logging()

log = logging.getLogger(__name__)
log.debug(logging.getLevelName(log.getEffectiveLevel()) + ' log level activated')
log.info("Starting %s" % __name__)

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
    else:
        log.info("ElasticAPM is disabled")


def initialize_app(flask_app):
    configure_app(flask_app)
    api.init_app(flask_app)


if __name__ == '__main__':
    # Used only when starting this script directly, i.e. for debugging
    initialize_app(app)
    app.run(debug=True)
else:
    # Main entrypoint
    initialize_app(app)
