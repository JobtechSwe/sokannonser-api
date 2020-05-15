#!/bin/bash
# This script will run tests with test coverage option
# reports will be created in test_reports/
#
# args:
# 1: api-key
# 2: one of the three test types below
# all = unit tests and integration tests
# integration = integration tests
# unit = unit tests

if [ $# -ne 2 ]; then
    echo "Error: Two arguments needed: api-key and test type [ all | unit | integration ]"
    exit 1
fi

test_type=$2
export TEST_API_KEY=$1

if [ "$test_type" = "all" ]; then
  test_to_run=''
fi
if [ "$test_type" = "unit" ]; then
  test_to_run="unit_tests"
fi

if [ "$test_type" = "integration" ]; then
  test_to_run="integration_tests"
fi

echo "starting "$test_type "tests"

pytest --html=test_reports/$test_type/report/$test_type.html --cov=. --cov-config=tests/.coveragerc --cov-report html:test_reports/$test_type/coverage_$test_to_run tests/$test_to_run

export test_api_key=narwhal
pytest --html=test_reports/search_dev/report.html tests/integration_tests/search
