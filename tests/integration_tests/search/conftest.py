import os
import pytest
import requests
from tests.test_resources.settings import headers_search



@pytest.fixture
def integration_session(scope="session"):
    """
    creates a Session object which will persist over the entire test run ("session").
    http connections will be reused (higher performance, less resource usage)
    Returns a Session object
    """
    s = requests.sessions.Session()
    s.headers.update(headers_search)
    return s


@pytest.fixture
def integration_url(scope="session"):
    """
    returns an url
    """
    test_url = os.getenv('TEST_URL_INTEGRATION', 'http://127.0.0.1')
    port = os.getenv('TEST_PORT_INTEGRATION', 5000)
    return f"{test_url}:{port}"
