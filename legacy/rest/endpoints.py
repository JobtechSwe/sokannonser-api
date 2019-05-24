import logging
from legacy.rest import ns_legacy, kommunlista_query, yrkesgrupp_query, yrkes_query, yrkespath_query
from legacy import repository

from flask_restplus import Resource

log = logging.getLogger(__name__)


@ns_legacy.route('soklista/lan')
class SoklistaLan(Resource):

    def get(self):
        return repository.lista_lan('lan')

@ns_legacy.route('soklista/lan2')
class SoklistaLan2(Resource):

    def get(self):
        return repository.lista_lan2('lan2')

@ns_legacy.route('soklista/kommuner')
class SoklistaKommuner(Resource):

    @ns_legacy.expect(kommunlista_query)
    def get(self):
        args = kommunlista_query.parse_args()
        return repository.lista_kommuner(args['lanid'])

@ns_legacy.route('soklista/yrkesomraden')
class SoklistaYrkesomraden(Resource):

    def get(self):
        return repository.lista_yrkesomraden()

@ns_legacy.route('soklista/yrkesgrupper')
class SoklistaYrkesgrupper(Resource):

    @ns_legacy.expect(yrkesgrupp_query)
    def get(self):
        args = yrkesgrupp_query.parse_args()
        return repository.lista_yrkesgrupper(args['yrkesomradeid'])

@ns_legacy.route('soklista/yrken')
class SoklistaYrken(Resource):

    @ns_legacy.expect(yrkes_query)
    def get(self):
        args = yrkes_query.parse_args()
        return repository.lista_yrken(args['yrkesgruppid'])


@ns_legacy.route('soklista/yrken/<benamning>')
class SoklistaYrkenPath(Resource):

    def get(self, benamning):
        print("BEN: %s" % benamning)
        return repository.lista_yrken_by_string(benamning)

