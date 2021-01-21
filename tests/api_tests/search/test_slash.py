import pytest

from tests.test_resources.helper import get_search
from tests.test_resources.settings import TEST_USE_STATIC_DATA


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.parametrize("query, expected", [
    ('försäljning/marknad', 2),
    ('försäljning marknad', 7),
    ('försäljning / marknad', 10),
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
])
def test_freetext_search_slash(session, query, expected):
    """
    Search with terms that are joined by a slash '/' included (x/y)
    with the terms separately (x y)
    and with a slash surrounded by space (x / y)
    """
    params = {'q': query, 'limit': '0'}
    assert get_search(session, params=params)['total']['value'] == expected


@pytest.mark.skipif(not TEST_USE_STATIC_DATA, reason="depends on a fixed set of ads")
@pytest.mark.parametrize("query, expected", [
    ('.NET/C#', 7),
    ('.NET / C#', 2),
    ('.NET C#', 25),
    ('.NET /C#', 1),
    ('.NET/ C#', 6),
    ('.NET', 17),
    ('C#/.net', 8),
    ('C# .net', 25),
    ('C# /.net', 6),
    ('C# / .net', 2),
    ('C#', 16),
    ('C#/.net', 8),
    ('C# .net', 25),
    ('C# /.net', 6),
    ('dotnet', 17)
])
def test_freetext_search_dot_hash_slash(session, query, expected):
    """
    Search with terms that are joined by a slash '/' included (x/y)
    with the terms separately (x y)
    and with a slash surrounded by space (x / y)
    for words that have . or # (e.g. '.net', 'c#')
    """
    params = {'q': query, 'limit': '0'}
    assert get_search(session, params=params)['total']['value'] == expected


@pytest.mark.smoke
@pytest.mark.parametrize("query, expected", [
    ('programmerare', 49),
    ('Systemutvecklare', 49),
    ('Systemutvecklare/Programmerare', 2),
    ('Systemutvecklare Programmerare', 49),
    ('Systemutvecklare / Programmerare', 3)
])
def test_freetext_search_slash_short(session, query, expected):
    params = {'q': query, 'limit': '0'}
    assert get_search(session, params=params)['total']['value'] == expected
