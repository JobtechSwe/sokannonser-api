import os
import json
import datetime
import requests

from test_cases import test_cases

if os.name == 'nt':
    encoding = 'cp1252'
else:
    encoding = 'utf-8'

# Set these variables
url_dev = os.getenv('URL_DEV', 'https://dev-jobsearch-api.jobtechdev.se/')
api_key_dev = os.getenv('API_KEY_DEV', '')

url_prod = os.getenv('URL_PROD', 'https://jobsearch.api.jobtechdev.se/')
api_key_prod = os.getenv('API_KEY_PROD', ' ')
# -----------------

DEV = (url_dev, api_key_dev, 'DEV')
PROD = (url_prod, api_key_prod, 'PROD')

TARGETS = [DEV, PROD]
OUTPUT_FILE = f"COMPARISON_RESULTS_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
TOLERANCE = 2


def get_total(session, url, api_key, q):
    session.headers.update({'api-key': api_key})
    response = session.get(f"{url}/search", params={'q': q, 'limit': 0})
    response.raise_for_status()
    return json.loads(response.content.decode('utf8'))['total']['value']


def run_all_test_cases(target):
    result = []
    s = requests.Session()
    s.headers.update({'accept': 'application/json'})
    for tc in test_cases:
        result.append(get_total(s, url=target[0], api_key=target[1], q=tc))
    return result


def run_all_test_cases_against_all_targets():
    all_results = []
    for target in TARGETS:
        all_results.append(run_all_test_cases(target))
        print(f"completed all test cases for {target[2]}")
    return all_results


def padded_word(word, length):
    padding_length = length - len(str(word))
    return f"{word}{padding_length * ' '}"


def write_results(all_results):
    print(f"writing results to file: {OUTPUT_FILE}")
    dev_results = all_results[0]
    prod_results = all_results[1]
    diffs = []

    with open(OUTPUT_FILE, mode='w', encoding=encoding) as f:
        header = f"{padded_word('Test Case', 90)} {padded_word('PROD', 20)} {padded_word('DEV', 20)} {padded_word('DIFF PROD - DEV', 20)}\n"
        f.write(header)

        for ix, dev_r in enumerate(dev_results):
            prod_r = prod_results[ix]
            test_case = test_cases[ix]
            test_case = (test_case[:80]) if len(test_case) > 80 else test_case  # truncate very long lines
            msg = f"{padded_word(test_case, 90)} {padded_word(prod_r, 20)} {padded_word(dev_r, 20)} "
            diff = prod_r - dev_r
            if diff != 0:
                msg += f"{diff}"
                diffs.append((msg, diff))
            f.write(f"{padded_word(msg, 40)}\n")
    return diffs


def print_diffs(diffs):
    print()
    if not diffs:
        print("no differences between prod and dev")
    else:
        print(f"printing differences larger than plus-minus {TOLERANCE}")
        print(
            f"{padded_word('Test Case', 90)} {padded_word('PROD', 20)} {padded_word('DEV', 20)} {padded_word('DIFF PROD - DEV', 20)}")
        for d in diffs:
            diff = d[1]
            msg = d[0]
            if diff < -TOLERANCE or diff > TOLERANCE:
                print(msg)


if __name__ == '__main__':
    results = run_all_test_cases_against_all_targets()
    diffs = write_results(results)
    print_diffs(diffs)
