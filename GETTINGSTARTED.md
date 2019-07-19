# Search API for job adds - getting started

The aim of this text is to walk you through what you're seeing in the Swagger UI at [open-API](https://open-api.dev.services.jtech.se/ "open API") to give you a bit of orientation on what can be done with the Job Search API. If you are just looking for a way to fetch all the ads please use our [bulk-API](https://bulk-api.dev.services.jtech.se "bulk API")
This API is intended for user search not downloading all the job ads. We may invalidate your API Keys if you make excessive amounts of calls that that don't fit the intended purpose of this API.

A bad practice typically means searching for every job of every region every five minutes.
A good practice means making lots of varied calls initiated by a real user.



# Table of Contents
[Short version](#Short-version)

[Resources](#Resources)

[API Key](#API-Key)

[Examples](#Examples)

## Short version
The API is meant for searching, we want you to be able to just build your own customised GUI on top of our free text query field q in /search like this...

	/search?q=Flen&offset=0&limit=100
...and not have to worry about the users finding the most relevant ads, search engine should do this for you.
If you want to narrow down the search result, use the available search filters. Some of the filters needs id-keys as input for searching structured data. The id-keys can be found at /taxonomy/search these will help you get sharper hits for structured data. We will always work on improving the hits for free queries hoping you'll see less and less use for filtering.

If you want to help your end users with term suggestions you can use the typeahead function, which will return common terms found in the job ads. This should work great with an auto complete feature in your search box. If i request

	/complete?q=stor
I get storkök, storhushåll, storesupport, storage. As they are the most common terms starting with "stor*" in ads.
If I request

	/complete?q=storage%20s

I get sverige, stockholms län, stockholm, svenska, script. Since they are the most common terms beginning with S for ads that contain the word Storage 	


## API key
For this API, you will need to register your own API key at www.jobtechdev.se

## Resources
This API service is divided into two major sections.

### 1. Open AF-job ads
The endpoints in the first section will return job ads from Arbetsförmedlingen that are currently open for applications. The ads published in Arbetsförmedlingen are tagged with some meta data like "id", "logotypurl" for the ad and "label" and "concept_id" for the occupation. The information in the ads is divided into sections with headlines like "headline", "description", "employer" and "salary_type". The ads may have information in all the fields or some of them.

#### Open-Ad-ID
/ad/{id} This endpoint is used for fetching specific job ads with all available meta data, by their ad ID number. The ID number can be found by doing a query with the other endpoint within this section, _Open-Search_.

#### Open-Search
/search finds what you want among all the indexed job ads that are currently open. With the possibility to filter by specific parameters like occupation, location, or required skills. Some are these parameters are set using an ID which you find in _Jobtech-Taxonomy_ (see the second headline on the page).


#### Complete
/complete This endpoint is meant to help you create autocomplete functions AKA type aheads. The result set will return the most frequent job market terms starting with the letters you put in. It's most easily understood by trying it out using the free query field q. If input is LÄK you will get "läkarsekreterare","läkare","läkemedel" etc.
If you put in more than one word you get the most common terms for that context for example "läkare L" and you get "linköping","lund" etc


### Jobtech-Taxonomy
This endpoint provides labour market terms and their corresponding unique ID. The ID's are required in some parameters in the /search endpoint.

Taxonomy contains terms within different categories. In the drop down list under "filter by type" all available categories are listed.

* Occupations. You can query three levels of occupation terms. The top level is _Occupation Fields_, which are broad areas of labor. The next level is _Occupation Groups_, which narrows the areas down a bit. Each Occupation Group belongs to a specific Occupation Field - its "parent". The third and final level is _Occupation Name_, which is individual occupations. Each Occupation Name also has a "parent" Occupation Group.
* Skills. These terms are often used in job ads and describes what a person knows or can do related to their job.
* Language. In this category most human languages (a.k.a. Natural languages) are listed.
* Geographic places (Country, Region, Municipality). Most languages in the world are listed in the category _Country_. The next level, _Regions_, are regions with unique [NUTS 3 Codes](https://ec.europa.eu/eurostat/web/nuts/background "Eurostats NUTS") in accordance with EU. In Sweden, the regions are similar to "Län". Each Region has a "parent" in the Country level. The third level of geographic places is the _Municipality_ level. This is the Swedish "kommuner". Each Municipality has a "parent" in the Region level.
* Wage type. This category contains descriptions of different forms of payment, like fixed monthly salary and commission.
* Employment type. This lists different employment types, like season jobs during the summer, or work on demand.
* Driving license. This contains all different driver's license categories in Sweden, and their description.
* Worktime extent. This contains terms like full time job and part time job.
* Sun education _fields_. These three categories describes different fields of education. The top level, _Sun Education Field 1_, contains the broad descriptions of education areas. The next level _Sun Education Field 2_ narrows the fields down a bit. _Sun Education Field 3_ contains specific education programs or trainings. Each concept in level 3 has a "parent" in level 2, and each level 2 concept has a level 1 "parent".
* Sun education _levels_. The three categories describes different levels of formal education in Sweden. _Sun Education Level 1_ is the top category and contains broad descriptions of education levels. The next level is _Sun Education Field 2_ describes more specific levels or generic degrees. _Sun Education Field 3_ contains specific degrees from Swedish formal education. Each concept in level 3 has a "parent" in level 2, and each level 2 concept has a level 1 "parent".


## Results

### Meta data for your search request
When making a search request the resulting response will start with some meta-info about your result.
Selected result's fields can be shown with a help of X-Fields request header. For exapmle

      curl "[open-API]/search?published-after=60&limit=10" -H "X-Fields: total,hits{id,headline,publication_date}"

#### "total":
"value": total Number of ads matching your search

"positions": total number of vacancies for your search

"query_time_in_millis": how long did the actuals search take

"result_time_in_millis": how long did the total roundtrip take

"stats": {},

"freetext_concepts": {},

"hits": placeholder for zero to * ads

### Object data
Then comes the actual ads

"id": the ID you can use in Open-AD-ID Endpoint

"headline": the headline of the ad

"application_deadline": last possible day to apply for the job,

"number_of_vacancies": number of vacancies for this ad

#### "description":
"text": the text body of the ad

"company_information": usually null

"needs": usually null

"requirements": usually null

"conditions": full time, part time, until further notice etc

#### "employment_type":
"concept_id": stable ID for label

"label": one out of these four "Vanlig anställning", "Sommarjobb / feriejobb", "Arbete utomlands", "Behovsanställning"

"legacy_ams_taxonomy_id": legacy id for label


#### "salary_type":
"concept_id": stable ID for label

"label": "Fast månads- vecko- eller timlön"

"legacy_ams_taxonomy_id": legacy id for label

#### "duration":
"concept_id": Stable ID for label

"label": duration of the employment

"legacy_ams_taxonomy_id": legacy id for label

#### "working_hours_type":
"concept_id": stable ID for label

"label": full time, part time

"legacy_ams_taxonomy_id": legacy id for label

#### "scope_of_work":
"min": minimum percentage of full time

"max": maximum percentage of full time

"access": when will the applicant start

#### "employer":
"phone_number": phone number of employer

"email": email of employer

"url": website of employer

"organization_number": the employers Swedish organisation number typically given by Bolagsverket

"name": the name of the employer

"workplace": where the job is, this field makes most sense with larger employer organisations

#### "application_details":

"information": information about how to apply

"reference": reference person with the employer for application

"email": email address to apply to

"via_af": if application should be made through AF

"url": address if application should be made via a website

"other": other information about how to apply


#### Top level
"experience_required": boolean if experience required or not

"access_to_own_car": boolean if applicant need to have a car to apply

"driving_license_required": boolean if you need to hold a drivers license or not

#### "driving_license":
"concept_id": stable ID for label

"label": the label value of the drivers license required b, c, d etc

##### "occupation":
"concept_id": stable ID for label, recommended to use for long term stability

"label": name of the occupation

"legacy_ams_taxonomy_id": legacy id for label

#### "occupation_group":
"concept_id": stable ID for label

"label": what group of jobs does the occupation belong to

"legacy_ams_taxonomy_id": legacy id for label

#### "occupation_field":
"concept_id": stable ID for label

"label": field of work the occupation belong to. A field is the closest we get to define a business as in "the IT business"

"legacy_ams_taxonomy_id": legacy id for label


#### "workplace_address": {
"municipality_code": 4 digit kommun-code as defined by Skatteverket
"municipality_concept_id": stable ID for label
"municipality": kommun
"region_code": 2 digit code for the län
"region": län
"country_code": 1-3 digit country code
"country": country
"street_address": street address for the job
"postcode": 5 digit post code
"city": city where the place of work is
"coordinates": longitud, latitud if you end up in the Indian ocean - switch places

#### "must_have": {
"skills": []
"concept_id": stable ID for label

"label": the name of a skill

"weight": weights for must_have are normally 10

"legacy_ams_taxonomy_id": legacy id for label

"languages": []
"concept_id": stable ID for label

"label": the name of a language            

"weight": weights for must_have are normally 10

"legacy_ams_taxonomy_id": legacy id for label

"work_experiences": []

"concept_id": stable ID for label

"label": the sought after experience            

"weight": weights for must_have are normally 10

"legacy_ams_taxonomy_id": legacy id for label

#### "nice_to have":
"skills": []

"concept_id": stable ID for label

"label": the sought after skill            

"weight": weights for must_have are normally 10

"legacy_ams_taxonomy_id": legacy id for label

"languages":[]

"concept_id": stable ID for label

"label": the sought after language            

"weight": weights for must_have are below 10

"legacy_ams_taxonomy_id": legacy id for label

"work_experiences": []

"concept_id": stable ID for label

"label": the name of a experience            

"weight": weights for must_have are normally 10

"legacy_ams_taxonomy_id": legacy id for label

"publication_date": when the ad was published

"last_publication_date": when the ad will be unpublished

"removed": boolean if the add unpublished or not, which can occur before the last publication date

"removed_date": when was the add removed

"source_type": where did the add come from

"timestamp": this timestamps is mostly for troubleshooting


## Examples

#### Searching for a particular job title
The easiest way to get the adds that contain a specific word like a jobtitle is to use a free text query (q) with the _Open-Search_ endpoint. This will give you ads with the specified word in either headline, ad description or place of work.

Request URL

	/search?q=sous-chef&offset=0&limit=10


If you want to be certain that the ad is for a souschef - and not just mentions a souschef - you can use the occupation ID in the field "occupation". If the ad has been registered by the recruiter with the occupation field set to "souschef", the ad will show up in this search. To do this query you use both the _Jobtech-Taxonomy_ endpoint and the _Open-Search_ endpoint. First of all, you need to find the occupation ID for souschef by text searching (q) in _Jobtech Taxonomy_ for the term in the right category (occupation-name).

Request URL

	/search?occupation-name=iugg_Qq9_QHH&offset=0&limit=10


Now you can use the ID in _Open-Search_ to fetch the ads registered with the term souschef in the occupation-name field

Request URL

	/search?occupation=iugg_Qq9_QHH&offset=0&limit=10

This will give a smaller result set with a higher certainty of actually being for a souschef, however the result set will likely miss a few relevant ads since the occupation-name field isn't always set by employers. You should find that a larger set is more useful since there are multiple sorting factors working to show the most relevant hits first. We're also working to always improve the API in regards to unstructured data. The term Souschef has three popular formats when found out in the wild. "Souschef", "sous chef", "sous-chef" but as the API recognise them as synonyms they will fetch the same number of adds. There are a lot of cases like these that we are constantly adding. Our machine learning model also works in favour of the free query.

### Searching only within a specific field of work
Firstly use the _Jobtech-Taxonomy_ endpoint to get the Id for Data/IT (occupation field). I'll make a free text search on the term "IT" narrowing down the search to occupation-field

Request URL

	/taxonomy/search?offset=0&limit=10&q=it&type=occupation-field&show-count=false

In the response body you’ll find the conceptId for the term Data/IT. Use this with the search endpoint to define the field in which you want to get all the open-api. So now I want to combine this with my favourite language with out all those pesky zoo keeper jobs ruining my search.

Request URL

	/search?occupation-field=apaJ_2ja_LuF&q=python%20Malm%C3%B6&offset=0&limit=10


### Finding jobs near you
You can filter your search on geographical terms picked up from the Taxonomy just the same way you can with occupation-titles and occupation-fields. (Concept_id doesn't work everywhere at the time of writing but you can use the numeral id's, they are very official and way less likely to change as skills and occupations sometimes do)
If i want to search for jobs in Norway i free text query the taxonomy for "Norge"

Request URL

       /taxonomy/search?offset=0&limit=10&q=norge&show-count=false

And add that parameter id to an empty free text query

Request URL

	/search?country=155&offset=0&limit=10

If I make a query which includes 2 different geographical filters the most local one will be promoted. As in this case where i'm searching for "lärare" using the municipality code for Haparanda and the region code for Norbottens Län. The jobs that are in Haparanda will be the first ones in the result set.

	/search?municipality=2583&q=l%C3%A4rare&offset=0&limit=10


You can also use longitude latitude coordinates and a radius in kilometres if you want.

Request URL

	/search?offset=0&limit=10&position=59.3,17.6&position.radius=10

### Negative search
So this is very simple using our qfield. Lets say i want to find Unix jobs

Request URL

	/search?q=unix&offset=0&limit=10

But I find that I get a lot of jobs expecting me to work with which I don't want. All that's needed is to use the minus symbol and the word I want to exclude

Request URL

	/search?q=unix%20-linux&offset=0&limit=10

### Finding swedish speak jobs abroad
Some times a filter can work to broadly and then it's easier to use a negative search to remove specific results you don't want. In this case i'm going to filter out all the jobs in Sweden. Rather than adding a minus Sweden in the q field "-sverige" I'm using the country code and the country field in the search. So first I get the country code for "Sverige" from the taxonomy end point.

Request URL

	/taxonomy/search?q=Sverige&type=country

And then I use the ID I got as a country code prefixed by a minus symbol.

Request URL

      /search?country=-199&q=swedish


### Getting all the jobs since date and time
A very common use case is COLLECT ALL THE ADDS. We don't want you to use the search API for this. It's expensive in terms of band width, CPU cycles and development time and it's not even guaranteed you'll get everything. Instead we'd like you to use our bulk load API. Find out more at https://jobtechdev.se/api/jobs

# TODO in order of importance

Successful queries
Auto complete - long version?
Errors
Contact Information
Good example of what to use
	qfields
	statistics
Optional fields
Null fields
