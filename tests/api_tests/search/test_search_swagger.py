import json
import pytest
from sokannonser import settings
from tests.test_resources.settings import SEARCH_URL


def test_search_swagger( session):
    """
    Test Swagger info for search
    """
    response = session.get(f"{SEARCH_URL}/swagger.json")
    response.raise_for_status()
    response_json = json.loads(response.content)
    assert response_json['info']['version'] == settings.API_VERSION

    expected = [('/ad/{id}', 3), ('/ad/{id}/logo', 1), ('/complete', 2), ('/search', 2), ('/taxonomy/search', 1)]
    for expected_path, expected_number in expected:
        assert response_json['paths'][expected_path]
        assert len(response_json['paths'][expected_path]['get']['responses']) == expected_number
