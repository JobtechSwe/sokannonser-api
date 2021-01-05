import sys
import pytest
from tests.test_resources.helper import get_search


@pytest.mark.slow
@pytest.mark.parametrize("relevance_threshold", [-1, 0, 0.1, 0.5, 0.8, 0.99, 1, 1.11])
def test_search_relevance_multiple_times( session, relevance_threshold):
    """
    This test is created to reproduce a bug where number of hits differ between queries
    """

    old_total = sys.maxsize
    old_pos = sys.maxsize
    failures = []
    params = {'q': 'sjuksköterska', 'relevance-threshold': relevance_threshold}

    for i in range(10):
        result = get_search(session,  params)
        total = result['total']
        pos = result['positions']

        if i > 0:  # comparison to previous result is pointless on first try
            msg = f"relevance-threshold: {relevance_threshold} search {i}: Total: {total}, positions: {pos}"
            pass
            if old_total != total or old_pos != pos:
                failures.append(msg)

        old_total = total
        old_pos = pos

    if len(failures) > 0:
        print("changes from previous searches:")
        for f in failures:
            print(f)
    assert len(failures) == 0
