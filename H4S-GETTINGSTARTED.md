#Search API for job adds - getting started

The aim of this text is to walk you through what you're seeing in the Swagger UI at https://open-api.dev.services.jtech.se/ to give you a bit of orientation on what can be done with the Job Search API's. 

# Table of Contents
1. [Resources](#Resources)
2. [API Key](#API Key)
3. [Examples](#Examples)

##Resources
This API service is divided into two sections.

### 1. Open AF-job ads
The endpoints in the first section will return job ads from Arbetsförmedlingen that are currently open for applications. The ads published in Arbetsförmedlingen are tagged with some meta data like "annonsid", "logotypurl", "yrkesbenamning" and "yrkesid" and the information in the ads is divided into sections with headlines like "annonsrubrik", "annonstext", "arbetstidvaraktighet" and "loneform". The ads may have information in all the fields or some of them.

####Open-Ad-ID
/ad/{id} This endpoint is used for fetching specific job ads with all available meta data, by their ad ID number. The ID number can be found by doing a query with the other endpoint within this section, _Open-Search_.

####Open-Search
/search finds what you want among all the indexed job ads that are currently open. With the possibility to filter by specific parameters like occupation, location, or required skills. Some are these parameters are set using an ID which you find in _Jobtech-Taxonomy_ (see the second headline on the page).

####Complete
/complete This endpoint is meant to help you create autocomplete functions AKA type aheads. The result set will return the most frequent job market terms starting with the letters you put in. It's most easily described using the q field. Put in LÄK and you get läkarsekreterare","läkare","läkemedel" etc. 
If you put in more than one word you get the most common terms for that context for example "läkare L" and you get "linköping","lund" etc


### 2. Jobtech-Taxonomy
This endpoint provides labour market terms and their corresponding unique ID. The ID's are required in some parameters in the /open/search endpoint.

Taxonomy contains terms within different categories. In the drop down list under "filter by type" all available categories are listed.

* Occupations. You can query three levels of occupation terms. The top level is _Occupation Fields_, which are broad areas of labor. The next level is _Occupation Groups_, which narrows the areas down a bit. Each Occupation Group belongs to a specific Occupation Field - its "parent". The third and final level is _Occupation Name_, which is individual occupations. Each Occupation Name also has a "parent" Occupation Group.
* Skills. These terms are often used in job ads and describes what a person knows or can do related to their job.
* Language. In this category most human languages (a.k.a. Natural languages) are listed.
* Geographic places (Country, Region, Municipality). Most languages in the world are listed in the category _Country_. The next level, _Regions_, are regions with unique [NUTS 3 Codes](https://ec.europa.eu/eurostat/web/nuts/background "Eurostats NUTS") in accordance with EU. In Sweden, the regions are similar to "Län". Each Region has a "parent" in the Country level. The third level of geographic places is the _Municipality_ level. This is the Swedish "kommuner". Each Municipality has a "parent" in the Region level.
* Wage type. This category contains descriptions of different forms of payment, like fixed monthly salary and commission.
* Employment type. This lists different employment types, like open-api during the summer, or work on demand.
* Driving license. This contains all different driver's license categories in Sweden, and their description.
* Worktime extent. This contains terms like full time job and part time job.
* Sun education _fields_. These three categories describes different fields of education. The top level, _Sun Education Field 1_, contains the broad descriptions of education areas. The next level _Sun Education Field 2_ narrows the fields down a bit. _Sun Education Field 3_ contains specific education programs or trainings. Each concept in level 3 has a "parent" in level 2, and each level 2 concept has a level 1 "parent".
* Sun education _levels_. The three categories describes different levels of formal education in Sweden. _Sun Education Level 1_ is the top category and contains broad descriptions of education levels. The next level is _Sun Education Field 2_ describes more specific levels or generic degrees. _Sun Education Field 3_ contains specific degrees from Swedish formal education. Each concept in level 3 has a "parent" in level 2, and each level 2 concept has a level 1 "parent".


##API key
For all API's, you will need to register your own API key at www.jobtechdev.se

##Examples 

####Searching for a particular job title
The easiest way to get the adds that contain a specific word is to use a free text query (q) with the _Open-Search_ endpoint. This will give you ads with the specified word in either headline, ad description or place of work.

Request URL

	https://open-api.dev.services.jtech.se/search?q=sous-chef&offset=0&limit=10


If you want to be certain that the ad is for a souschef - and not just mentions a souschef - you can use the occupation ID in the field "occupation". If the ad has been registered by the recruiter with the occupation field set to "souschef", the ad will show up in this search. To do this query you use both the _Jobtech-Taxonomy_ endpoint and the _Open-Search_ endpoint. First of all, you need to find the occupation ID for souschef by text searching (q) in _Jobtech Taxonomy_ for the term in the right category (occupation-name).

Request URL

	https://open-api.dev.services.jtech.se/search?occupation-name=iugg_Qq9_QHH&offset=0&limit=10


Now you can use the ID in _Open-Search_ to fetch the ads registered with the term souschef in the occupation-name field

Request URL

	https://open-api.dev.services.jtech.se/open/search?occupation=iugg_Qq9_QHH&offset=0&limit=10

This will give a smaller result set with a higher certainty of actually being for a souschef, however the result set will likely miss a few relevant ads since the occupation-name field isn't always set by employers. You should find that a larger set is more useful since there are multiple sorting factors working to show the most relevant hits first. We're also working to always improve the API in regards to unstructured data. The term Souschef has three popular formats when found out in the wild. "Souschef", "sous chef", "sous-chef" but as the API recognise them as synonyms they will fetch the same number of adds. There are a lot of cases like these that we are constantly adding. Our machine learning model also works in favour of the free query, it can to a pretty high degree distinguish between competences asked for by the employer and words just mentioned in the ad.

###Searching only within a specific field of work
Firstly use the _Jobtech-Taxonomy_ endpoint to get the Id for Data/IT (occupation field). I'll make a free text search on the term "IT" narrowing down the search to occupation-field

Request URL

	https://open-api.dev.services.jtech.se/taxonomy/search?offset=0&limit=10&q=it&type=occupation-field&show-count=false

	
In the respone body you’ll find the conceptId for the term Data/IT. Use this with the search endpoint to define the field in which you want to get all the open-api. So now I want to combine this with my favourite language with out all those pesky zoo keeper jobs ruining my search.

Request URL

	https://open-api.dev.services.jtech.se/search?occupation-field=apaJ_2ja_LuF&q=python%20Malm%C3%B6&offset=0&limit=10


###Finding jobs near you
You can filter your search on geographical terms picked up from the Taxonomy just the same way you can with occupation-titles and occupation-fields. (Concept_id doesn't work everywhere at the time of writing but you can use the numeral id's, they are very official and way less likely to change as skills and occupations sometimes do) 
If i want to search for jobs in Norway i free text query the taxonomy for "Norge"

Request URL
	
	https://open-api.dev.services.jtech.se/taxonomy/search?offset=0&limit=10&q=norge&show-count=false

And add that parameter id to an empty free text query
	
Request URL

	https://open-api.dev.services.jtech.se/search?country=155&offset=0&limit=10
	
If I make a query which includes 2 different geographical filters the most local one will be promoted. As in this case where i'm searching for "lärare" using the municipality code for Haparanda and the region code for Norbottens Län. The jobs that are in Haparanda will be the first ones in the result set.

	https://open-api.dev.services.jtech.se/search?municipality=2583&q=l%C3%A4rare&offset=0&limit=10


You can also use longitude latitude coordinates and a radius in kilometers if you want. 

Request URL
	
	https://open-api.dev.services.jtech.se/search?offset=0&limit=10&position=59.3,17.6&position.radius=10


###Getting all the jobs since date and time 
A very common use case is COLLECT ALL THE ADDS. We don't want you to use the search API for this. Instead we'd like you to use our bulk load API. Find out more at jobtechdev.se/doc/api/jobs 

#TODO 
Good example of what to use 
qfields for
statistics for
Auto complete
	

	
	
