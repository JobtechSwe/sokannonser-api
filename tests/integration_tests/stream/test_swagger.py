import json
from sokannonser import settings


def test_swagger(session, url):
    """
    Test Swagger info
    """
    response = session.get(f"{url}/swagger.json")
    response.raise_for_status()
    response_json = json.loads(response.content)
    assert response_json['info']['version'] == settings.API_VERSION
    assert response_json['paths']['/stream']
    assert len(response_json['paths']['/stream']['get']['responses']) == 4
    assert response_json['paths']['/snapshot']
    assert len(response_json['paths']['/snapshot']['get']['responses']) == 4
