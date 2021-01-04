import pytest


@pytest.fixture(scope='function', autouse=True)
def print_name(request):
    """
    executed automatically for every test
    does not have to be called
    prints:
    - the name of the test
    - parameters if test is parametrized
    - the name and path of the file the test is in
    """
    name_of_test = request.node.originalname
    if not name_of_test:
        name_of_test = request.node.name
    path_and_file = request.node.location[0]
    param_message = _param_msg(request)

    print(f"\n==========   start of '{name_of_test}' {param_message} in file '{path_and_file}'      =========== ")
    yield  # test is executed
    print(f"\n================================================================================================ ")


def _param_msg(request):
    markers = request.node.own_markers

    if not markers:  # test is not parametrized
        return ''
    else:
        try:
            tmp = request.node.keywords.node.name
            param = tmp.split('[')[1].strip(']')
        except Exception:
            return ''
        return f"( {param} )"
