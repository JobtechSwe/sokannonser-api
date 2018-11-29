import logging
import base64
import binascii
import re
from flask import request
from flask_restplus import abort
from sokannonser import settings


log = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")


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
        abort(401, message="Access denied!")
        apikey = request.headers.get(settings.APIKEY)
        decoded_key = _decode_key(apikey) \
            if apikey != settings.APIKEY_BACKDOOR else settings.APIKEY_BACKDOOR
        if decoded_key == settings.APIKEY_BACKDOOR or EMAIL_REGEX.match(decoded_key):
            log.info("API key %s is valid." % decoded_key)
            return func(*args, **kwargs)
        log.info("Failed validation for key '%s'" % decoded_key)

    return wrapper


# Decodes the API which is in base64 format
def _decode_key(apikey):
    decoded = 'Invalid API key'
    if apikey:
        for i in range(3):
            try:
                decoded = base64.urlsafe_b64decode(apikey).decode('utf-8').strip()
                break
            except binascii.Error as e:
                log.debug("Failed to decode api key: %s: %s" % (apikey, e))
            except UnicodeDecodeError as u:
                log.debug("Failed to decode utf-8 key: %s: %s" % (apikey, u))
            # Reappend trailing '=' to find correct padding
            apikey = "%s=" % apikey
    return decoded
