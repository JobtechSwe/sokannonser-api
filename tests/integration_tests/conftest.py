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
def stream_url(scope="session"):
    """
    returns an url
    """
    test_url = os.getenv('TEST_URL_STREAM', 'http://localhost')
    port = os.getenv('TEST_PORT_STREAM', 5000)
    return f"{test_url}:{port}"


@pytest.fixture
def search_url(scope="session"):
    """
    returns an url
    """
    test_url = os.getenv('TEST_URL_SEARCH', 'http://localhost')
    port = os.getenv('TEST_PORT_SEARCH', 5000)
    return f"{test_url}:{port}"


@pytest.fixture
def search_url(scope="session"):
    """
    returns an url
    """
    test_url = os.getenv('TEST_URL_SEARCH', 'http://localhost')
    port = os.getenv('TEST_PORT_SEARCH', 5000)
    return f"{test_url}:{port}"
