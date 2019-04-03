#Search API for job adds - getting started

The aim of this text is to walk you through what you're seeing in the Swagger UI at https://jobs.dev.services.jtech.se/ to give you a bit of orientation on what can be done with the Job Search API's. 

##Resources
This API service is divided into four sections.

### 1. Open-API
The endpoints in the first section will return job ads from Arbetsförmedlingen that are currently open for applications. The ads published in Arbetsförmedlingen are tagged with some meta data like "annonsid", "logotypurl", "yrkesbenamning" and "yrkesid" and the information in the ads is divided into sections with headlines like "annonsrubrik", "annonstext", "arbetstidvaraktighet" and "loneform". The ads might have information in all the fields or some of them.

####Open-Ad-ID
This endpoint is used for fetching specific job ads with all available meta data, by their ad ID number. The ID number can be found by doing a query with the other endpoint within this section, _Open-Search_.

####Open-Search
The second endpoint searches all job ads that are currently open for application, with the possibility to filter by specific parameters like occupation, location, or required skills. Some are these parameters are set using an ID which you find in _Jobtech-Taxonomy_ (see the fourth headline on the page).

### 2. AF-Job-Ads
This endpoint is mainly made for Arbetsförmedlingen's internal systems and will not be further described in this documentation.

### 3. All-Job-Ads
PLEASE NOTICE These endpoints can be used for Hack 4 Sweden but will be deprecated some time later this spring or summer. We hope to be able to bring back this functionality later on. 

This data-set tries to bring you a complete set of current job adds from any source in Sweden. Since the sources of these adds are webpages

### 4. Jobtech-Taxonomy
This endpoint provides labour market terms and their corresponding unique ID. The ID's are required in some parameters in the /open/search endpoint.

Taxonomy contains terms within different categories. In the drop down list under "filter by type" all available categories are listed.

* Occupations. You can query three levels of occupation terms. The top level is _Occupation Fields_, which are broad areas of labor. The next level is _Occupation Groups_, which narrows the areas down a bit. Each Occupation Group belongs to a specific Occupation Field - it's "parent". The third and final level is _Occupation Name_, which is individual occupations. Each Occupation Name also has a "parent" Occupation Group.
* Skills. These terms are often used in job ads and describes what a person knows or can do related to their job.
* Language. In this category most human languages (a.k.a. Natural languages) are listed.
* Geographic places (Country, Region, Municipality). Most languages in the world are listed in the category _Country_. The next level, _Regions_, are regions with unique [NUTS 3 Codes](https://ec.europa.eu/eurostat/web/nuts/background "Eurostats NUTS") in accordance with EU. In Sweden, the regions are similar to "Län". Each Region has a "parent" in the Country level. The third level of geographic places is the _Municipality_ level. This is the Swedish "kommuner". Each Municipality has a "parent" in the Region level.
* Wage type. This category contains descriptions of different forms of payment, like fixed monthly salary and commission.
* Employment type. This lists different employment types, like jobs during the summer, or work on demand.
* Driving license. This contains all different driver's license categories in Sweden, and their description.
* Worktime extent. This contains terms like full time job and part time job.
* Sun education _fields_. These three categories describes different fields of education. The top level, _Sun Education Field 1_, contains the broad descriptions of education areas. The next level _Sun Education Field 2_ narrows the fields down a bit. _Sun Education Field 3_ contains specific education programs or trainings. Each concept in level 3 has a "parent" in level 2, and each level 2 concept has a level 1 "parent".
* Sun education _levels_. The three categories describes different levels of formal education in Sweden. _Sun Education Level 1_ is the top category and contains broad descriptions of education levels. The next level is _Sun Education Field 2_ describes more specific levels or generic degrees. _Sun Education Field 3_ contains specific degrees from Swedish formal education. Each concept in level 3 has a "parent" in level 2, and each level 2 concept has a level 1 "parent".


##API key
For all API's, use the key "apa".

##Examples 

###Getting all the adds for souschefs
The easiest way to get the adds that contain a specific word is to use a free text query (q) with the _Open-Search_ endpoint. This will give you ads with the specified word in either headline, ad description or place of work.

Request URL

	https://jobs.dev.services.jtech.se/open/search?q=souschef&offset=0&limit=10

If you want to be more certain that the ad is for a souschef - and not just mentions a souschef - you can use the occupation ID in the field "occupation". If the ad has been registered by the recruiter with the occupation field set to "souschef", the ad will show up in this search. To do this query you use both the _Jobtech-Taxonomy_ endpoint and the _Open-Search_ endpoint. First of all, you need to find the occupation ID for souschef by text searching (q) in _Jobtech Taxonomy_ for the term in the right category (occupation-name).

Request URL

	https://jobs.dev.services.jtech.se/vf/search?offset=0&limit=10&q=souschef&type=occupation-name&show-count=false

Now you can use the ID in _Open-Search_ to fetch the ads registered with the term souschef in the occupation field

Request URL

	https://jobs.dev.services.jtech.se/open/search?occupation=iugg_Qq9_QHH&offset=0&limit=10

This will give a smaller result set with a higher certainty of actually being for souschef jobs, however the result set will likely miss a few relevant ads since the occupation field isn't always set by recruiters. You might find that a larger set is more useful since there are multiple sorting factors working to show the most relevant hits first anyway.

###Getting all the jobs in the IT industry 
Firstly use the _Jobtech-Taxonomy_ endpoint to get the Id for Data/IT (occupation field). 
TO BE CONTINUED!

Request URL

	https://jobs.dev.services.jtech.se/vf/search?offset=0&limit=10&type=occupation-field&show-count=false
	
	
In the respone body you’ll find the conceptId for the term Data/IT. Use this with the search endpoint to define the field in which you want to get all the jobs.

Request URL

	https://jobs.dev.services.jtech.se/open/search?field=apaJ_2ja_LuF&offset=0&limit=10

###Getting all the jobs as a pre school teacher in Luleå and Norrbottens län
Use the taxonomy search to get the conceptId for the term förskollärare. This can be done with a free text text query where you’ll also see other terms than occupation titles

Request URL

	https://jobs.dev.services.jtech.se/vf/search?offset=0&limit=10&q=f%C3%B6rskoll%C3%A4rare&show-count=false

Or use a narrowed down search where you filter competences and groupings of occupations titles that also relate to the search term förskollärare

Request URL
	
	https://jobs.dev.services.jtech.se/vf/search?offset=0&limit=10&q=f%C3%B6rskoll%C3%A4rare&type=occupation-name&show-count=false

Getting the id of Luleå can be done the same way, with or without filtering for Municipality (kommun)
Request URL

	https://jobs.dev.services.jtech.se/vf/search?offset=0&limit=10&q=Lule%C3%A5&show-count=false
	https://jobs.dev.services.jtech.se/vf/search?offset=0&limit=10&q=Lule%C3%A5&type=municipality&show-count=false


So now we got the conceptId for Luleå and Förskollärare we can combine them

Request URL

	https://jobs.dev.services.jtech.se/open/search?occupation=3oGcRGX83S&municipality=51WRN_Mtjk&offset=0&limit=10

Not a whole lot of adds? Lets expand the search with Norrbottens län. When using both the municipality AND the region. The more local one - municipality will be prioritised in the sorting order.
To get the conceptId for Norbottens län search for it in the Jobtech taxonomy endpoint

Request URL

	xxx

Now we add this as well to our search for relevant job adds

Request URL

	https://jobs.dev.services.jtech.se/open/search?occupation=rUcW_z9R_Qsv&municipality=2580&region=9hXe_F4g_eTG&offset=0&limit=10

Hopefully a few more hits this time. 

###Getting all the jobs since date and time - demonstrating how to use offset
A very common use case is COLLECT ALL THE ADDS. Typically an automated proccess with a set frequence. We want all the adds so lets max out the result set limit to 100

Request URL

	https://jobs.dev.services.jtech.se/open/search?published-after=2019-02-14T13%3A13%3A13&offset=0&limit=100
	
In my case the first row of the response says "antal_platsannonser": 168, while I got just 100 adds.
how do i get the next 68? I use the ofset like this and fetch the last 68 adds.

Request URL 

	https://jobs.dev.services.jtech.se/open/search?published-after=2019-02-14T13%3A13%3A13&offset=100&limit=100


#TODO 
Good example of how to use position
Good example of what to use qfields for	

	
	
