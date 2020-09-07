import os
import pytest
import requests
import tests.test_resources.settings as settings


@pytest.fixture
def session(scope="session"):
    """
    creates a Session object which will persist over the entire test run ("session").
    http connections will be reused (higher performance, less resource usage)
    Returns a Session object
    """
    s = requests.sessions.Session()
    s.headers.update(settings.headers_search)
    return s


@pytest.fixture
def session_stream(scope="session"):
    """
    creates a Session object which will persist over the entire test run ("session").
    http connections will be reused (higher performance, less resource usage)
    Returns a Session object
    """
    s = requests.sessions.Session()
    s.headers.update(settings.headers_stream)
    return s


@pytest.fixture
def stream_url(scope="session"):
    """
    returns an url
    """
    test_url = os.getenv('TEST_URL_STREAM', 'http://127.0.0.1')
    port = os.getenv('TEST_PORT_STREAM', 5000)
    return f"{test_url}:{port}"


@pytest.fixture
def search_url(scope="session"):
    """
    returns an url
    """
    test_url = os.getenv('TEST_URL_SEARCH', 'http://localhost')
    #test_url = 'https://dev-testset-jobsearch.test.services.jtech.se'
    port = os.getenv('TEST_PORT_SEARCH', 5000)
    #port = 443
    return f"{test_url}:{port}"

