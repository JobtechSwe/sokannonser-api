import sys
import pytest

from tests.test_resources.helper import get_search
from tests.test_resources.settings import TEST_USE_STATIC_DATA


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.parametrize("query, expected", [
    ('försäljning/marknad', 2),
    ('försäljning marknad', 7),
    ('försäljning / marknad', 10),
    ('C#/.net', 8),
    ('C# .net', 7),
    ('C# /.net', 6),
    ('lager/logistik', 3),
    ('lager / logistik', 2),
    ('lager logistik', 40),
    ('psykolog/beteendevetare', 9),
    ('psykolog / beteendevetare', 0),
    ('psykolog beteendevetare', 13),
    ('Affärsutvecklare/exploateringsingenjör', 0),
    ('Affärsutvecklare / exploateringsingenjör', 0),
    ('Affärsutvecklare exploateringsingenjör', 3),
    ('Affärsutvecklare/exploateringsingenjörer', 0),
    ('Affärsutvecklare / exploateringsingenjörer', 0),
    ('Affärsutvecklare exploateringsingenjörer', 3),
    ('barnpsykiatri/habilitering', 0),
    ('barnpsykiatri / habilitering', 0),
    ('barnpsykiatri habilitering', 8),
    ('mentor/kontaktlärare', 0),
    ('mentor / kontaktlärare', 0),
    ('mentor kontaktlärare', 0),
    ('Verktygsmakare/Montör', 8),
    ('Verktygsmakare / Montör', 0),
    ('Verktygsmakare Montör', 15),
    ('Kolloledare/specialpedagog', 3),
    ('Kolloledare / specialpedagog', 0),
    ('Kolloledare specialpedagog', 4),
    ('fritidshem/fritidspedagog', 2),
    ('fritidshem / fritidspedagog', 1),
    ('fritidshem fritidspedagog', 2),
    ('UX/UI Designer', 0),
    ('UX / UI Designer', 0),
    ('UX UI Designer', 0),
    ('.NET/C#', 5),
    ('.NET / C#', 8),
    ('.NET C#', 7),
])
def test_freetext_search_slash( session, query, expected):
    """
    Search with terms that are joined by a slash '/' included (x/y)
    with the terms separately (x y)
    and with a slash surrounded by space (x / y)
    """

    params = {'q': query, 'limit': '0'}
    response_json = get_search(session,  params=params)
    assert response_json['total']['value'] == expected


@pytest.mark.smoke
@pytest.mark.parametrize("query, expected", [
    ('programmerare', 49),
    ('Systemutvecklare', 49),
    ('Systemutvecklare/Programmerare', 2),
    ('Systemutvecklare Programmerare', 49),
    ('Systemutvecklare / Programmerare', 3)
])
def test_freetext_search_slash_short( session, query, expected):
    params = {'q': query, 'limit': '0'}
    response_json = get_search(session,  params=params)
    assert response_json['total']['value'] == expected
