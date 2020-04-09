import pytest
import requests

from tests.integration_tests.test_resources.settings import headers


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
    # Todo: use environment variables
    base_url = 'localhost'  # from ENV
    port = 5000  # from env
    return f"http://{base_url}:{port}"
