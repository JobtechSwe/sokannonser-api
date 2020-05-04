import pytest
import requests
from tests.integration_tests.test_resources.stream import get_stream_expect_error


@pytest.mark.smoke
@pytest.mark.integration
def test_zip_endpoint_expect_not_found_response(session, url):
    """
    test that a 'not found' response (http 404) is returned
    when trying to access the /zip endpoint
    This test will detect if the endpoint is mistakenly activated
    """
    get_stream_expect_error(session, url, path='/zip', params={},
                            expected_http_code=requests.codes.not_found)
