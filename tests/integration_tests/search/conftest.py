import os
import pytest
import requests
from sokannonser import settings


@pytest.fixture
def integration_session(scope="session"):
    """
    creates a Session object which will persist over the entire test run ("session").
    http connections will be reused (higher performance, less resource usage)
    Returns a Session object
    """
    s = requests.sessions.Session()
    s.headers.update(settings.headers_search)
    return s


@pytest.fixture
def integration_url(scope="session"):
    """
    returns an url
    """

    test_url = os.getenv('TEST_URL_INTEGRATION', 'http://localhost')

    port = os.getenv('TEST_PORT_INTEGRATION', 5000)
    return f"{test_url}:{port}"
