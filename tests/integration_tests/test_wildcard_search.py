import os
import pytest

from sokannonser import app

test_api_key = os.getenv("TEST_API_KEY")


@pytest.mark.skip(reason="Disabled until changes in index mapping have taken hold")
@pytest.mark.parametrize("query", [
    'murar*',
    'sjukskö*',
    'systemutvecklar*',
    'Anläggningsarbetar*',
    'Arbetsmiljöingenjö*',
    'Beläggningsarbetar*',
    'Behandlingsassisten*',
    'Bilrekonditionerar*',
    'Eventkoordinato*',
    'Fastighetsförvaltar*',
    'Fastighetsskötar*',
    'Kundtjänstmedarbetar*',
    '*utvecklare',
    '*sköterska',
    '*undtjänstmedarbetare',
])
@pytest.mark.integration
def test_wildcard_search(query):
    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        results = testclient.get('/search', headers=headers, data={'q': query})
        assert 'hits' in results.json
        assert len(results.json['hits']) > 0
