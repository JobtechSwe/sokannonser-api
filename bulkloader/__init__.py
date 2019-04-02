import logging
from flask import Flask
from flask_cors import CORS
from sokannonser import appconf
from bulkloader.rest import api
# Import all Resources that are to be made visible for the app
from bulkloader.rest.bulk import BulkZip
from bulkloader.rest.bulk import BulkLoad

app = Flask(__name__)
CORS(app)
appconf.configure_logging()
log = logging.getLogger(__name__)
log.debug(logging.getLevelName(log.getEffectiveLevel()) + ' log level activated')
log.info("Starting %s" % __name__)


if __name__ == '__main__':
    # Used only when starting this script directly, i.e. for debugging
    appconf.initialize_app(app, api)
    app.run(debug=True)
else:
    # Main entrypoint
    appconf.initialize_app(app, api)
