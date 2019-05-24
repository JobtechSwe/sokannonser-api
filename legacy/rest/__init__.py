from simplexml import dumps
from flask_restplus import Api, Namespace, reqparse
from flask import make_response

api = Api(version='1.0', title='Platsannonser',
          description='Arbetsförmedlingens öppna sök-API',
          default='legacy',
          default_label="Ett API för att söka jobbannonser.",
          default_mediatype='application/xml')

ns_legacy = Namespace('Legacy API', description='Feature replicated legacy API')


def output_xml(data, code, headers=None):
    """Makes a Flask response with a XML encoded body"""
    resp = make_response(dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


api.add_namespace(ns_legacy, '/')
api.representations['application/xml'] = output_xml

kommunlista_query = reqparse.RequestParser()
kommunlista_query.add_argument('lanid', type=int, required=True)

yrkesgrupp_query = reqparse.RequestParser()
yrkesgrupp_query.add_argument('yrkesomradeid', type=int, required=True)

yrkes_query = reqparse.RequestParser()
yrkes_query.add_argument('yrkesgruppid', type=int, required=True)

yrkespath_query = reqparse.RequestParser()
yrkespath_query.add_argument('benamning', required=True)

legacy_query = reqparse.RequestParser()
legacy_query.add_argument('lanid', type=int)
legacy_query.add_argument('kommunid', type=int)
legacy_query.add_argument('nyckelord')
legacy_query.add_argument('yrkesid', type=int)
legacy_query.add_argument('sida', type=int)
legacy_query.add_argument('antalrader', type=int)
