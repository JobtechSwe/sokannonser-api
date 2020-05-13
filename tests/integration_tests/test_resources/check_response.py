def check_response_return_json(response):
    assert response.status == '200 OK', f"expected http status code 200/OK but got '{response.status}'. Error: {response.data}"
    return response.json
