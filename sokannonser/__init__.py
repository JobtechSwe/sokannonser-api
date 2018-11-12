import logging
import json
from sokannonser.customlogging import NarvalLogFormatter
from flask import Flask
from flask_cors import CORS
from sokannonser.rest import api
from sokannonser.rest.endpoint.auranest import AuranestSearch
from sokannonser.rest.endpoint.platsannonser import Search
from sokannonser.rest.endpoint.valuestore import Valuestore
from sokannonser import settings
import os



app = Flask(__name__)
CORS(app)



def configure_logging():
    logging.basicConfig()
    # Remove basicConfig-handlers and replace with custom formatter.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    fh = logging.StreamHandler()

    if os.getenv('FLASK_ENV', '') == 'development':
        is_develop_mode = True
    else:
        is_develop_mode = False

    f = NarvalLogFormatter('%(asctime)s|%(levelname)s|%(name)s|MESSAGE: %(message)s', is_develop_mode=is_develop_mode)
    fh.setFormatter(f)
    root = logging.getLogger()
    # root.setLevel(logging.INFO)
    root.addHandler(fh)

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

NarvalLogFormatter.printTestLogMessages(log)


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
