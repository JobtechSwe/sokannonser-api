import pytest
import requests
from tests.test_resources.helper import get_search
from tests.test_resources.settings import SEARCH_URL


@pytest.mark.parametrize("query, expected", [

    ('C#/.net', 8),
    ('C# .net', 7),
    ('C# /.net', 6),
    ('C# / .net', 8),
    ('C#', 16),
    ('.NET/C#', 5),
    ('.NET / C#', 8),
    ('.NET C#', 7),
    ('.NET /C#', 8),
    ('.NET/ C#', 4),
    ('.NET', 17),
    ('dotnet', 17),

])
def test_freetext_search_slash(session, query, expected):
    response_json = get_search(session, {'q': query})
    assert response_json['total']['value'] == expected
