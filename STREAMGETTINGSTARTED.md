# Stream API for job ads - getting started

The aim of this text is to walk you through what you're seeing in the [Swagger-UI](https://jobstream.api.jobtechdev.se) to give you can download all of the job ads we have. This is much better than using the search API to download all content.

# Table of Contents
* [Authentication](#Authentication)
* [Endpoints](#Endpoints)
* [Results](#Results)
* [Errors](#Errors)



## Short introduction

The endpoints for the ads search API are:

* [Stream](#Stream) - returning all active ads that have been updated after a given moment.

Easiest way to try out the API is to go to the [swagger page](https://jobstream.api.jobtechdev.se/).
But first you need a key which you need to authenticate yourself.

## Authentication
For this API, you will need to register to get your own API key at [apirequest.jobtechdev.se](https://apirequest.jobtechdev.se)

## Endpoints
Below we only show the URLs. If you prefer the curl command, you type it like:

	curl "{URL}" -H "accept: application/json" -H "api-key: {proper_key}"
	
### Stream 

/stream?{date and occupation}
e.g.:
/stream?date=2020-04-06T15%3A12%3A15&occupation=kock



The stream endpoint in the first section will return job ads that are currently open for applications. Great if you like to rebase your data.

	https://jobstream.api.jobtechdev.se/stream
	
If you only want to get the updates from a certain time point you add it in the format YYYY-MM-DDTHH:MM:SS, for example 2019-06-11T10:00:00. Rate limit is one request per minute.

  	https://jobstream.api.jobtechdev.se/stream?date=2019-10-03T10%3A00%3A00

If you’re looking for more advanced search options, please check our [JobSearch API](https://jobtechdev.se/devguide/apis/jobsearch.html).

## Results
The results of your queries will be in [JSON](https://en.wikipedia.org/wiki/JSON) format. We won't attempt to explain this attribute by attribute in this document. Instead we've decided to try to include this in the data model which you can find in our [Swagger GUI](https://jobsearch.api.jobtechdev.se).

Successful queries will have a response code of 200 and give you a result set that consists of:
1. Some meta data about your search such as number of hits and the time it took to execute the query and 
2. The ads that matched your search. 

## Errors
Unsuccessful queries will have a response code of:

| HTTP Status code | Reason | Explanation |
| ------------- | ------------- | -------------|
| 400 | Bad Request | Something wrong in the query |
| 401 | Unauthorized | You are not using a valid API key |
| 429 | Rate limit exceeded | You requested too much during too short time |
| 500 | Internal Server Error | Something wrong on the server side |

