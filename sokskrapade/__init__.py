import logging
from flask import Flask
from flask_cors import CORS
from jobtech.common.customlogging import configure_logging
from sokannonser import appconf
from sokskrapade.rest import api
from sokskrapade.rest.skrapade import SearchJobLink

app = Flask(__name__)
CORS(app)
configure_logging([__name__.split('.')[0], 'sokskrapade', 'jobtech'])
log = logging.getLogger(__name__)
log.info(logging.getLevelName(log.getEffectiveLevel()) + ' log level activated')
log.info("Starting %s" % __name__)


if __name__ == '__main__':
    appconf.initialize_app(app, api)
    app.run(debug=True)
else:
    appconf.initialize_app(app, api)

