import sys
import pytest

from tests.test_resources.helper import get_search
from tests.test_resources.settings import TEST_USE_STATIC_DATA


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.parametrize("query, expected", [
    ('försäljning/marknad', 0),
    ('försäljning marknad', 9),
    ('försäljning / marknad', 10),
    ('C#/.net', 6),
    ('C# .net', 11),
    ('C# /.net', 3),
    ('lager/logistik', 5),
    ('lager / logistik', 2),
    ('lager logistik', 31),
    ('psykolog/beteendevetare', 5),
    ('psykolog / beteendevetare', 0),
    ('psykolog beteendevetare', 8),
    ('Affärsutvecklare/exploateringsingenjör', 3),
    ('Affärsutvecklare / exploateringsingenjör', 0),
    ('Affärsutvecklare exploateringsingenjör', 4),
    ('Affärsutvecklare/exploateringsingenjörer', 3),
    ('Affärsutvecklare / exploateringsingenjörer', 0),
    ('Affärsutvecklare exploateringsingenjörer', 4),
    ('barnpsykiatri/habilitering', 1),
    ('barnpsykiatri / habilitering', 0),
    ('barnpsykiatri habilitering', 5),
    ('mentor/kontaktlärare', 0),
    ('mentor / kontaktlärare', 0),
    ('mentor kontaktlärare', 0),
    ('Verktygsmakare/Montör', 4),
    ('Verktygsmakare / Montör', 0),
    ('Verktygsmakare Montör', 9),
    ('Kolloledare/specialpedagog', 3),
    ('Kolloledare / specialpedagog', 0),
    ('Kolloledare specialpedagog', 5),
    ('fritidshem/fritidspedagog', 4),
    ('fritidshem / fritidspedagog', 0),
    ('fritidshem fritidspedagog', 5),
    ('UX/UI Designer', 1),
    ('UX / UI Designer', 0),
    ('UX UI Designer', 0),
    ('.NET/C#', 4),
    ('.NET / C#', 11),
    ('.NET C#', 11),
])
def test_freetext_search_slash(session, search_url, query, expected):
    """
    Search with terms that are joined by a slash '/' included (x/y)
    with the terms separately (x y)
    and with a slash surrounded by space (x / y)
    """
    print('==================', sys._getframe().f_code.co_name, '================== ')
    params = {'q': query, 'limit': '0'}
    response_json = get_search(session, search_url, params=params)
    assert response_json['total']['value'] == expected


@pytest.mark.smoke
@pytest.mark.parametrize("query, expected", [
    ('programmerare', 27),
    ('Systemutvecklare', 27),
    ('Systemutvecklare/Programmerare', 4),
    ('Systemutvecklare Programmerare', 27),
    ('Systemutvecklare / Programmerare', 1)
])
def test_freetext_search_slash_short(session, search_url, query, expected):
    params = {'q': query, 'limit': '0'}
    response_json = get_search(session, search_url, params=params)
    assert response_json['total']['value'] == expected
