import logging
from flask import Flask
from flask_cors import CORS
from sokannonser.rest import api
from sokannonser.rest.endpoints import Search, Valuestore
from sokannonser import settings

app = Flask(__name__)
CORS(app)

logging.basicConfig()

# Set log level debug for module specific events
# and level warning for all third party dependencies
for key in logging.Logger.manager.loggerDict:
    if key.startswith(__name__) or key.startswith('valuestore'):
        logging.getLogger(key).setLevel(logging.DEBUG)
    else:
        logging.getLogger(key).setLevel(logging.WARNING)

log = logging.getLogger(__name__)

log.info("Starting %s" % __name__)


def configure_app(flask_app):
    flask_app.config.SWAGGER_UI_DOC_EXPANSION = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config.RESTPLUS_VALIDATE = settings.RESTPLUS_VALIDATE
    flask_app.config.RESTPLUS_MASK_SWAGGER = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config.ERROR_404_HELP = settings.RESTPLUS_ERROR_404_HELP


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
