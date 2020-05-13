import pytest
import urllib3
import requests

@pytest.mark.live_data
@pytest.mark.smoke
@pytest.mark.integration
def test_zip_endpoint_expect_not_found_response(session, stream_url):
    """
    This test will detect if the endpoint is mistakenly activated

    test that a 'not found' response (http 404) is returned
    when trying to access the /zip endpoint or that the test can't connect at all.

    """
    try:
        r = session.get(f"{stream_url}/zip")
    except (IOError, urllib3.exceptions.HTTPError):
        pass  # not being able to connect to the endpoint is fine
    else:  # received an http response, check that it's '404 not found'
        assert r.status_code == requests.codes.not_found
