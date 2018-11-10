from sokannonser.repository import elastic, platsannonser
from sokannonser import settings
from valuestore import taxonomy as t
from valuestore.taxonomy import tax_type
from dateutil import parser
import sys, pytest, logging

log = logging.getLogger(__name__)


def find(key, dictionary): 
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                if isinstance(d, dict):
                    for result in find(key, d):
                        yield result


tax_stat = [tax_type[t.OCCUPATION], tax_type[t.GROUP], tax_type[t.FIELD], tax_type[t.SKILL], tax_type[t.WORKTIME_EXTENT]]
tax_other = [tax_type[t.MUNICIPALITY], tax_type[t.REGION], tax_type[t.PLACE], tax_type[t.LANGUAGE]]
tax_noexist = ['', 'blabla', ' ']


@pytest.mark.integration
@pytest.mark.parametrize("taxonomy_type", tax_stat + tax_other + tax_noexist)
def test_get_stats_for(taxonomy_type):
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    # print(platsannonser.get_stats_for(taxonomy_type) )
    if taxonomy_type not in tax_stat:
        try:
            platsannonser.get_stats_for(taxonomy_type)
        except KeyError as e:
            print('KeyError exception. Reason: taxonomy type %s' % str(e))
            assert "'" + taxonomy_type + "'" == str(e)
        except Exception as ex:
            pytest.fail('ERROR: This is not a KeyError exception: %s' % str(ex), pytrace=False)
    else:  # taxonomy_type is in 5 mentioned in platsannonser.py::get_stats_for()
        for k, v in platsannonser.get_stats_for(taxonomy_type).items():
            assert isinstance(int(k), int)  # check k is string of int
            assert isinstance(v, int)  # check v is int

            
def safe_execute(default, exception, function, *args):
    # safe_execute("Felkod", ValueError, int, kkod) != "Felkod"
    try:
        return function(*args)
    except exception:
        logging.exception(default)
        return default

    
@pytest.mark.integration
@pytest.mark.parametrize("kommunkoder", [["2510", "0118"], ["0118"], None, []])
@pytest.mark.parametrize("lanskoder", [["25"], ["01", "03"], ["ejLanKod"], None, []])
def test_build_plats_query(kommunkoder, lanskoder):
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    d = platsannonser._build_plats_query(kommunkoder, lanskoder)
    print(d)
    kommunlanskoder = []
    for lanskod in lanskoder if lanskoder is not None else []:
        kommun_results = t.find_concepts(elastic, None, lanskod, tax_type.get(t.MUNICIPALITY)).get('hits', []).get('hits', [])
        kommunlanskoder += [entitet['_source']['id'] for entitet in kommun_results]
    # OBS: Casting kommunkod values to ints the way currently stored in elastic
    if kommunkoder:
        # int_kommunkoder = [ int(kommunkod) for kommunkod in kommunkoder] # if safe_execute("Fel", ValueError, int, kommunkod) != "Fel"]
        assert set(kommunkoder).issubset(set(find("value", d)))
    if kommunlanskoder:
        # int_kommunlanskoder = [ int(kommunlanskod) for kommunlanskod in kommunlanskoder]
        assert set(kommunlanskoder).issubset(set(find("value", d)))
    if kommunkoder is None and kommunlanskoder is None:
        assert d is None

        
@pytest.mark.unit
@pytest.mark.parametrize("from_datetime", ["2018-09-28T00:00:00", '2018-09-28', '', None, []])
@pytest.mark.parametrize("to_datetime", ["2018-09-28T00:01", '2018-09-27', '', None, []])
def test_build_timeframe_query(from_datetime, to_datetime):
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    print(from_datetime, to_datetime)
    if not from_datetime and not to_datetime:  # from and to date are empty
        assert platsannonser._build_timeframe_query(from_datetime, to_datetime) is None
        return
    if from_datetime and to_datetime:
        d = platsannonser._build_timeframe_query(parser.parse(from_datetime), parser.parse(to_datetime))
        print(d)
        assert d['range']['publiceringsdatum']['gte'] == parser.parse(from_datetime).isoformat()
        assert d['range']['publiceringsdatum']['lte'] == parser.parse(to_datetime).isoformat()
        return
    if from_datetime:
        d = platsannonser._build_timeframe_query(parser.parse(from_datetime), to_datetime)
        assert d['range']['publiceringsdatum']['gte'] == parser.parse(from_datetime).isoformat()
        return
    if to_datetime:
        d = platsannonser._build_timeframe_query(from_datetime, parser.parse(to_datetime))
        assert d['range']['publiceringsdatum']['lte'] == parser.parse(to_datetime).isoformat()

        
@pytest.mark.unit
@pytest.mark.parametrize("args, exist, expected", [({settings.APIKEY: "",
                                                     settings.LONGITUDE: 17.1,
                                                     settings.LATITUDE: 60.5,
                                                     settings.POSITION_RADIUS: 5},
                                                    True,
                                                    {"geo_distance": {"distance": "5km",
                                                                      "arbetsplatsadress.coordinates": [
                                                                          17.1, 60.5
                                                                      ]}}),
                                                   ({settings.APIKEY: "",
                                                     settings.LONGITUDE: 399.1,
                                                     settings.LATITUDE: 60.5,
                                                     settings.POSITION_RADIUS: 5},
                                                    False,
                                                    {"geo_distance": {"distance": "5km",
                                                                      "arbetsplatsadress.coordinates": [
                                                                          399.1, 60.5
                                                                      ]}}),
                                                   ({settings.APIKEY: "",
                                                     settings.LONGITUDE: 17.1,
                                                     settings.LATITUDE: 60.5,
                                                     settings.POSITION_RADIUS: -5},
                                                    False,
                                                    {"geo_distance": {"distance": "-5km",
                                                                      "arbetsplatsadress.coordinates": [
                                                                          17.1, 60.5
                                                                      ]}})])
def test_geo_distance_filter(args, exist, expected):
    query_dsl = platsannonser._parse_args(args)
    assert (expected in query_dsl["query"]["bool"]["filter"]) == exist
    
