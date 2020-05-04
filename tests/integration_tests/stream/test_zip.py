import pytest
import requests
from tests.integration_tests.test_resources.stream import get_zip_expect_connection_refused_error_or_not_found


@pytest.mark.smoke
@pytest.mark.integration
def test_zip_endpoint_expect_not_found_response(session, url):
    """
    test that a 'not found' response (http 404) is returned
    when trying to access the /zip endpoint
    This test will detect if the endpoint is mistakenly activated
    """
    get_zip_expect_connection_refused_error_or_not_found(session, url)
