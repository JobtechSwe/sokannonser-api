import os
import pytest

from sokannonser import app

test_api_key = os.getenv("TEST_API_KEY")


# @pytest.mark.skip(reason="missing test data?")
@pytest.mark.parametrize("query, expected_number", [
    ('murar*', 0),
    ('systemutvecklar*', 10),
    ('*utvecklare', 37),
    ('utvecklare*', 18),
    ('*utvecklare*', 0),  # double wildcard does not work
    ('Anläggningsarbetar*', 0),
    ('Arbetsmiljöingenjö*', 2),
    ('Beläggningsarbetar*', 0),
    ('Behandlingsassisten*', 3),
    ('Bilrekonditionerar*', 1),
    ('Eventkoordinato*', 0),
    ('Fastighetsförvaltar*', 2),
    ('Fastighetsskötar*', 6),
    ('Fastighet*', 48),
    ('Kundtjänstmedarbetar*', 6),
    ('*undtjänstmedarbetare', 6),
    ('Kundtjänst*', 37),
    ('sjukskö*', 100),
    ('*sköterska', 100)
])
@pytest.mark.integration
def test_wildcard_search(query, expected_number):
    app.testing = True
    with app.test_client() as testclient:
        headers = {'api-key': test_api_key, 'accept': 'application/json'}
        results = testclient.get('/search', headers=headers, data={'q': query, "limit": 100})
        assert 'hits' in results.json
        actual_number = len(results.json['hits'])
        assert actual_number == expected_number, f"wrong number of hits for query '{query}'"

# min 3 chars
        assert len(results.json['hits']) > 0, f"no hits for query '{query}'"
        # print(results.json)
