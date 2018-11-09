import logging
import json
from flask import Flask
from flask_cors import CORS
from sokannonser.rest import api
from sokannonser.rest.endpoint.auranest import AuranestSearch
from sokannonser.rest.endpoint.platsannonser import Search
from sokannonser.rest.endpoint.valuestore import Valuestore
from sokannonser import settings



app = Flask(__name__)
CORS(app)

#TODO: Move to separate file/class.
class NarvalLogFormatter(logging.Formatter):
    def format(self, record):
        is_json_str = False
        json_obj = None
        # print(type(record.msg))
        if type(record.msg) == str and '{' in record.msg:
            try:
                json_obj = json.loads(record.msg)
                is_json_str = True
            except ValueError:
                # print('Got ValueError when trying json.loads')
                pass

        if is_json_str and json_obj is not None:
            # print('json.dumping')
            message = json.dumps(json_obj)
            record.msg = message

        result = super(NarvalLogFormatter, self).format(record)
        return result.replace('\n', '')


    def formatException(self, exc_info):
        result = super(NarvalLogFormatter, self).formatException(exc_info)
        return result.replace('\n', '')

    def formatMessage(self, record):
        result = super(NarvalLogFormatter, self).formatMessage(record)
        return result.replace('\n', '')


def configure_logging():
    logging.basicConfig()
    # Remove basicConfig-handlers and replace with custom formatter.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    fh = logging.StreamHandler()
    f = NarvalLogFormatter('%(asctime)s|%(levelname)s|%(name)s|MESSAGE: %(message)s')
    fh.setFormatter(f)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
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


def test_logging():
    log.info('Testing log levels - BEGIN')
    log.debug('DEBUG log level activated')
    log.info('INFO log level activated')
    log.warning('WARNING log level activated')
    log.error('ERROR log level activated')

    test_dict = {
        "prop1":"dict_val1",
        "prop2": "dict_val2",
        "inner": {
            "innerobjprop":"innerobjval"
        }
    }
    log.debug(test_dict)

    test_json = '''{
        "jsontestprop1": "jsontestval1",
        "jsontestprop2": "jsontestval2"
        
    }'''

    log.debug(test_json)
    log.info('Testing log levels - END')



configure_logging()



log = logging.getLogger(__name__)

log.info("Starting %s" % __name__)

test_logging()


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
