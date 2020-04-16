import os
import pytest
import requests

test_api_key = os.getenv('TEST_API_KEY')
headers = {'api-key': test_api_key, 'accept': 'application/json'}


@pytest.fixture
def session(scope="session"):
    """
    creates a Session object which will persist over the entire test run ("session").
    http connections will be reused (higher performance, less resource usage)
    Returns a Session object
    """
    s = requests.sessions.Session()
    s.headers.update(headers)
    return s


@pytest.fixture
def url(scope="session"):
    """
    returns an url

    """
    test_url = os.getenv('TEST_URL', 'localhost')
    port = os.getenv('TEST_PORT', 5000)

    return f"http://{test_url}:{port}"
