import json
from sokannonser import settings
from tests.test_resources.settings import STREAM_URL

def test_swagger(session):
    """
    Test Swagger info
    """
    response = session.get(f"{STREAM_URL}/swagger.json")
    response.raise_for_status()
    response_json = json.loads(response.content)
    assert response_json['info']['version'] == settings.API_VERSION
    assert response_json['paths']['/stream']
    assert len(response_json['paths']['/stream']['get']['responses']) == 4
    assert response_json['paths']['/snapshot']
    assert len(response_json['paths']['/snapshot']['get']['responses']) == 4
