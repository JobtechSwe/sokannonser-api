import logging
import base64
import binascii
import re
import time
from flask import request
from flask_restplus import abort
from sokannonser import settings
from sokannonser.repository import elastic


log = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
valid_api_keys = dict()
last_check_ts = 0


def check_api_key(func):
    def wrapper(*args, **kwargs):
        apikey = request.headers.get(settings.APIKEY)
        decoded_key = _decode_key(apikey) \
            if apikey != settings.APIKEY_BACKDOOR else settings.APIKEY_BACKDOOR
        if decoded_key == settings.APIKEY_BACKDOOR or EMAIL_REGEX.match(decoded_key):
            log.info("API key %s is valid." % decoded_key)
            return func(*args, **kwargs)
        log.info("Failed validation for key '%s'" % decoded_key)
        abort(401, message="You're no monkey!")

    return wrapper


def check_api_key_auranest(func):
    def wrapper(*args, **kwargs):
        global last_check_ts, valid_api_keys
        if int(time.time()) > last_check_ts + 60:  # Refresh keys every 60 secs
            log.debug("Reloading API keys")
            valid_api_keys = elastic.get_source(index=settings.ES_SYSTEM_INDEX,
                                                doc_type='_all',
                                                id=settings.ES_APIKEYS_DOC_ID)
            last_check_ts = time.time()
        apikey = request.headers.get(settings.APIKEY)
        decoded_key = _decode_key(apikey)
        if valid_api_keys and apikey in valid_api_keys.get('validkeys', []):
            log.info("API key \"%s\" is valid." % decoded_key)
            return func(*args, **kwargs)
        log.info("Failed validation for key '%s'" % decoded_key)
        abort(401, message="You're no monkey!")

    return wrapper


# Decodes the API which is in base64 format
def _decode_key(apikey):
    decoded = apikey or 'Invalid Key: None'
    if apikey:
        for i in range(3):
            try:
                decoded = base64.urlsafe_b64decode(apikey).decode('utf-8').strip()
                break
            except binascii.Error as e:
                # log.debug("Failed to decode api key: %s: %s" % (apikey, e))
                pass
            except UnicodeDecodeError as u:
                log.debug("Failed to decode utf-8 key: %s: %s" % (apikey, u))
                decoded = 'Invalid Key'  # Prevents users from sending plain email adress
            # Reappend trailing '=' to find correct padding
            apikey = "%s=" % apikey
    return decoded
