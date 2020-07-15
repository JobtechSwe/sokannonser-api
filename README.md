# Sök Annonser API
This repository contains code for both JobSearch and JobStream APIs.

## Requirements
* Python 3.7+
* Access to a host or server running Elasticsearch

## Environment variables

The application is entirely configured using environment variables. 

Default values are provided with the listing.

### Application configuration

    ES_HOST=127.0.0.1

Specifies which elastic search host to use for searching.

    ES_PORT=9200
   
Port number to use for elastic search

    ES_INDEX=platsannons-read
    
Specifies which index to search published ads from (JobSearch)

    ES_HISTORICAL_ADS_INDEX
    
Specifies which index to search historical ads from (JobSearch with x-feature-historical-ads)

    ES_USER
    
Sets username for elastic search (no default value)

    ES_PWD
    
Sets password for elastic search (no default value)

    ES_STREAM_INDEX=platsannons-stream
    
Specifies which index to stream ads from (JobStream)

    ES_TAX_INDEX=taxonomy
    
Specifies which index contains taxonomy information.

    ES_SYSTEM_INDEX=apikeys
    
Specifies which index contains api keys.

### Flask

    FLASK_APP

The name of the application. Set to "sokannonser" for JobSearch or "bulkloader" for JobStream.

    FLASK_ENV
    
Set to "development" for development. 

### APM and debug settings

In order to use APM, the following environment variables must be set.

    APM_SERVICE_NAME
    APM_SERVICE_URL
    APM_SECRET
    APM_LOG_LEVEL
    
## Installation and running

To start up the application, set the appropriate environment variables as described above. 
Then run the following commands.

    $ pip install -r requirements.txt
    $ export FLASK_APP=sokannonser
    $ export FLASK_ENV=development
    $ flask run

Go to http://127.0.0.1:5000 to access the swagger API

## Test

### Run unit test

    $ python3 -m pytest -svv -m unit tests/unit_tests
    
### Köra integrationstester    

When running integration tests, an actual application is started,
so you need to specify environment variables for elastic search in order for it to run properly.

    $ python3 -m pytest -svv -ra -m integration tests/integration_tests

    
### Test coverage
    
https://pytest-cov.readthedocs.io/en/latest/

    $ python3 -m pytest -svv -ra -m unit --cov=. tests/unit_tests


## Using Docker
TBW
