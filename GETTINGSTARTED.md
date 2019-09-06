# Search API for job adds - getting started

The aim of this text is to walk you through what you're seeing in the [Swagger-UI](https://jobsearch.api.jobtechdev.se) to give you a bit of orientation on what can be done with the Job Search API. If you are just looking for a way to fetch all the ads please use our [bulk load API](https://jobstream.api.jobtechdev.se)
The search API is intended for user search not downloading all the job ads. We may invalidate your API Keys if you make excessive amounts of calls that don't fit the intended purpose of this API.

A bad practice typically means searching for every job of every region every fifth minute.
A good practice means making lots of varied calls initiated by real users.

# Table of Contents
* [Authentication](#Authentication)
* [Endpoints](#Endpoints)
* [Results](#Results)
* [Errors](#Errors)
* [Use cases](#Use-cases)


## Short introduction

The endpoints for the ads search API are:
* [search](#Ad-Search) - returning ads matching a search phrase.
* [complete](#Typeahead) - returning common words matching a search phrase. Useful for auto-complete.
* [ad](#Ad) - returning the ad matching an id.
* [logo](#Logo) - returns the logo for an ad.

Easiest way to try out the API is to go to the [swagger page](https://jobsearch.api.jobtechdev.se/).
But first you need a key which you need to authenticate yourself.

## Authentication
For this API, you will need to register your own API key at [www.jobtechdev.se](https://www.jobtechdev.se/)

## Endpoints
Below we only show the URLs. If you prefer the curl command you type it like:

	curl "{URL}" -H "accept: application/json" -H "api-key: {proper_key}"
	
### Ad search 
/search?q={search text}

The search endpoint in the first section will return job ads that are currently open for applications.
The API is meant for searching, we want offer you the possibility to just build your own customized GUI on top of our free text query field "q" in /search like this ...

	https://jobsearch.api.jobtechdev.se/search?q=Flen&offset=0&limit=10
	
This means you don't need to worry about how to build an advanced logic to help the users finding the most relevant ads for, let's say, Flen. The search engine will do this for you.
If you want to narrow down the search result in other ways than the free query offers, you can use the available search filters. Some of the filters need id-keys as input for searching structured data. The id-keys can be found at /taxonomy/search these will help you get sharper hits for structured data. We will always work on improving the hits for free queries hoping you'll have less and less use for filtering.

### Typeahead
/complete?q={typed string}

If you want to help your end users with term suggestions you can use the typeahead function, which will return common terms found in the job ads. This should work great with an auto complete feature in your search box. If you request ...

	https://jobsearch.api.jobtechdev.se/complete?q=stor
... you'll get storkök, storhushåll, storesupport, and storage as they are the most common terms starting with "stor*" in ads.

If you request

	https://jobsearch.api.jobtechdev.se/complete?q=storage%20s

... you'll get sverige, stockholms län, stockholm, svenska, and script since they are the most common terms beginning with "s" for ads that contain the word "storage"

### Ad
/ad/{id} 

This endpoint is used for fetching specific job ads with all available meta data, by their ad ID number. The ID number can be found by doing a search query.

	https://jobsearch.api.jobtechdev.se/ad/8430129

### Logo
/ad/{id}/logo

This endpoint returns the logo for a given ad's id number.

	https://jobsearch.api.jobtechdev.se/ad/8430129/logo

### Jobtech-Taxonomy
If you need help finding the official names for occupations, skills, or geografic place check out or [API for taxonomy](https://www.jobtechdev.se/).

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
| 404 | Missing ad | The ad you requested is not available |
| 429 | Rate limit exceeded | You requested too much during too short time |
| 500 | Internal Server Error | Something wrong on the server side |



## Use cases 
To help you find yuor way forward, here are some example of use cases:
Searching for a particular job titleSearching for a particular job title
Searching only within a specific field of work
* [Searching for a particular job title](#Searching-for-a-particular-job-title)
* [Searching only within a specific field of work](#Searching-only-within-a-specific-field-of-work)
* [Finding jobs near you](#Finding-jobs-near-you)
* [Negative search](#Negative-search)
* [Finding Swedish speaking jobs abroad](#Finding-Swedish-speaking-jobs-abroad)
* [Customise the result set](#Customise-the-result-set)
* [Getting all the jobs since date and time](#Getting-all-the-jobs-since-date-and-time)

#### Searching for a particular job title
The easiest way to get the adds that contain a specific word like a jobtitle is to use a free text query (q) with the _Open-Search_ endpoint. This will give you ads with the specified word in either headline, ad description or place of work.

Request URL

	https://jobsearch.api.jobtechdev.se/search?q=sous-chef&offset=0&limit=10


If you want to be certain that the ad is for a souschef - and not just mentions a souschef - you can use the occupation ID in the field "occupation". If the ad has been registered by the recruiter with the occupation field set to "souschef", the ad will show up in this search. To do this query you use both the _Jobtech-Taxonomy_ endpoint and the _Open-Search_ endpoint. First of all, you need to find the occupation ID for souschef by text searching (q) in _Jobtech Taxonomy_ for the term in the right category (occupation-name).

Request URL

	https://jobsearch.api.jobtechdev.se/search?occupation-name=iugg_Qq9_QHH&offset=0&limit=10


Now you can use the ID in _Open-Search_ to fetch the ads registered with the term souschef in the occupation-name field

Request URL

	https://jobsearch.api.jobtechdev.se/search?occupation=iugg_Qq9_QHH&offset=0&limit=10

This will give a smaller result set with a higher certainty of actually being for a souschef, however the result set will likely miss a few relevant ads since the occupation-name field isn't always set by employers. You should find that a larger set is more useful since there are multiple sorting factors working to show the most relevant hits first. We're also working to always improve the API in regards to unstructured data. The term Souschef has three popular formats when found out in the wild. "Souschef", "sous chef", "sous-chef" but as the API recognise them as synonyms they will fetch the same number of adds. There are a lot of cases like these that we are constantly adding. Our machine learning model also works in favour of the free query.

### Searching only within a specific field of work
Firstly use the _Jobtech-Taxonomy_ endpoint to get the Id for Data/IT (occupation field). I'll make a free text search on the term "IT" narrowing down the search to occupation-field

Request URL

	To be updated http://jobtech-taxonomy-api.dev.services.jtech.se/v0/taxonomy/public/search?q=IT

In the response body you’ll find the conceptId for the term Data/IT. Use this with the search endpoint to define the field in which you want to get all the open-api. So now I want to combine this with my favourite language without all those pesky zoo keeper jobs ruining my search.

Request URL

	To be updated


### Finding jobs near you
You can filter your search on geographical terms picked up from the Taxonomy just the same way you can with occupation-titles and occupation-fields. (Concept_id doesn't work everywhere at the time of writing but you can use the numeral id's, they are very official and way less likely to change as skills and occupations sometimes do)
If i want to search for jobs in Norway i free text query the taxonomy for "Norge"

Request URL

       To be updated https://jobsearch.api.jobtechdev.se/taxonomy/search?offset=0&limit=10&q=norge&show-count=false

And add that parameter id to an empty free text query

Request URL

	https://jobsearch.api.jobtechdev.se/search?country=155&offset=0&limit=10

If I make a query which includes 2 different geographical filters the most local one will be promoted. As in this case where i'm searching for "lärare" using the municipality code for Haparanda and the region code for Norbottens Län. The jobs that are in Haparanda will be the first ones in the result set.

	https://jobsearch.api.jobtechdev.se/search?municipality=2583&q=l%C3%A4rare&offset=0&limit=10


You can also use longitude latitude coordinates and a radius in kilometres if you want.

Request URL

	https://jobsearch.api.jobtechdev.se/search?offset=0&limit=10&position=59.3,17.6&position.radius=10

### Negative search
So this is very simple using our qfield. Lets say i want to find Unix jobs

Request URL

	https://jobsearch.api.jobtechdev.se/search?q=unix&offset=0&limit=10

But i find that i get a lot of jobs expecting me to work with which i dont want. All that's needed is to use the minus symbol and the word i want to exclude

Request URL

	https://jobsearch.api.jobtechdev.se/search?q=unix%20-linux&offset=0&limit=10

### Finding Swedish speaking jobs abroad
Some times a filter can work to broadly and then it's easier to use a negative search to remove specific results you don't want. In this case i'm going to filter out all the jobs in Sweden. Rather than adding a minus Sweden in the q field "-sverige" I'm using the country code and the country field in the search. So first I get the country code for "Sverige" from the taxonomy end point.

Request URL

	To be updated https://jobsearch.api.jobtechdev.se/taxonomy/search?q=Sverige&type=country

And then I use the ID I got as a country code prefixed by a minus symbol.

Request URL

      	https://jobsearch.api.jobtechdev.se/search?country=-199&q=swedish

### Customise the result set
There's a lot of reasons you might want less fields for your search result set. In this case the idea is a map based job search that plots needles where the jobs can be found based on a user search. Everything needed is the GPS coordinates for the needle and the id for the ad so more info can be fetched once the user clicks on the needle.
In the Swagger GUI its possible to use the X-fields to define what fields to include in result set. So this mask will look like this

 	hits{id, workplace_address{coordinates}}

 This will create an extra header displayed in the curl example in Swagger. So this example will look like this

 	curl "https://jobsearch.api.jobtechdev.se/search?q=skogsarbetare&offset=0&limit=10" -H "accept: application/json" -H "api-key: <proper_key>" -H "X-Fields: hits{id, workplace_address{coordinates}}"



### Getting all the jobs since date and time
A very common use case is COLLECT ALL THE ADDS. We don't want you to use the search API for this. It's expensive in terms of band width, CPU cycles and development time and it's not even guaranteed you'll get everything. Instead we'd like you to use our [bulk load API](https://jobstream.api.jobtechdev.se).


