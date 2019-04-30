#Search API for job adds - getting started

The aim of this text is to walk you through what you're seeing in the Swagger UI at https://{URL} to give you a bit of orientation on what can be done with the Job Search API's. 

Not a fan of documentation? No problem. Just use API key "apa" and go crazy.

##Resources
This API service is divided into four sections.

###Open-API
The endpoints in the first section will return job ads from Arbetsförmedlingen that are currently open for applications. 

####/open/ad/{id}
This endpoint is used for fetching specific job adds by their ad ID number. The ID number can be found by doing a query with the other endpoint within this section, _/open/search_. The resulting JSON file will contain the following fields:
* "platsannons"
  * "annons":
    * "annonsid":
    * "platsannonsUrl":
    * "annonsrubrik":
    * "annonstext":
    * "yrkesbenamning":
    * "yrkesid":
    * "publiceraddatum":
    * "antal_platser":
    * "kommunnamn":
    * "kommunkod":
    * "antalplatserVisa":
    * "anstallningstyp":
  * "villkor":
    * "varaktighet":
    * "arbetstid":
    * "arbetstidvaraktighet":
    * "lonetyp":
    * "loneform":
  * "ansokan":
    * "referens":
    * "webbplats":
    * "sista_ansokningsdag":
    * "ovrigt_om_ansokan":
  * "arbetsplats":
    * "arbetsplatsnamn":
    * "postnummer":
    * "postadress":
    * "postort":
    * "postland":
    * "land":
    * "besoksadress":
    * "logotypurl":
    * "hemsida":
    * "kontaktpersonlista":
      * "kontaktpersondata":
        * [...]
  * "krav":
    * {}

The second endpoint, _/open/search_, searches all job ads that are currently open for application, with the possibility to specify specific parameters, for example occupation, location, or required skills. Some are these parameters are set using an ID which you find in _Jobtech Taxonomy_ (the fourth headline on the page). The resulting JSON file will contain the following fields:
* "antal_platsannonser":
*  "statistik":
   * "typ":
   *  "poster":
* "platsannonser"
   * ["annons":
     * "annonsid":
     * "annons_url":
     * "annonsrubrik":
     * "annonstext":
     * "yrkesbenamning":
     * "yrkesid":
     * "publiceraddatum":
     * "antal_platser":
     * "kommunkod":
   * "villkor":
     * "varaktighet":
     * "arbetstid":
     * "lonetyp":
     * "loneform":
   * "ansokan":
     * "referens":
     * "sista_ansokningsdag":
   * "arbetsplats": 
     * "arbetsplatsnamn":
     * "postnummer":
     * "postadress":
     * "postort":
     * "hemsida":
   * "krav": 
     * {}]

###AF-job ads
This endpoint is mainly made for Arbetsförmedlingen's internal systems and will not be further described in this document.

###All job ads
TBC


###Jobtech Taxonomy
This endpoint provides labour market terms and their corresponding unique ID. The ID's are required in some parameters in the /open/search endpoint.

The Taxonomy contains terms related to different categories. In the drop down list under "filter by type" all available categories are listed.

* Occupations. You can query three levels of occupation terms. The top level is _Occupation Fields_, which are broad areas of labor. The next level is _Occupation Groups_, which narrows the areas down a bit. Each Occupation Group belongs to a specific Occupation Field - it's "parent". The third and final level is _Occupation Name_, which is individual occupations. Each Occupation Name also has a "parent" Occupation Group.
* Skills. These terms are often used in job ads and describes what a person knows or can do related to their job.
* Language. In this category most human languages (a.k.a. Natural languages) are listed.
* Geographic places (Country, County, Municipality). Most languages in the world are listed in the category _Country_. The next level, _Counties_, are regions with unique "NUTS Codes" in accordance with EU listings. In Sweden, the counties are similar to "Län". Each Countiy has a "parent" in the Country level. The third level of geographic places is the _Municipality_ level. This is the Swedish "kommuner". Each Municipality has a "parent" in the County level.
* Wage type. This category contains descriptions of different forms of payment, like fixed monthly salary and commission.
* Employment type. This lists different employment types, like jobs during the summer, or work on demand.
* Driving license. This contains all different driver's license categories in Sweden, and their description.
* Worktime extent. This contains terms like full time job and part time job.
* Sun education _fields_. These three categories describes different fields of education. The top level, _Sun Education Field 1_, contains the broad descriptions of education areas. The next level _Sun Education Field 2_ narrows the fields down a bit. _Sun Education Field 3_ contains specific education programs or trainings. Each concept in level 3 has a "parent" in level 2, and each level 2 concept has a level 1 "parent".
* Sun education _levels_. The three categories describes different levels of formal education in Sweden. _Sun Education Level 1_ is the top category and contains broad descriptions of education levels. The next level is _Sun Education Field 2_ describes more specific levels or generic degrees. _Sun Education Field 3_ contains specific degrees from Swedish formal education. Each concept in level 3 has a "parent" in level 2, and each level 2 concept has a level 1 "parent".


##API key
For all API's, use the key "apa".

##Examples 

###Getting all the adds for the occupation souschef
The easiest way to get the ads that contain a specific word is to use a free text query 

Request URL

	https://{URL}/open/search?q=souschef&offset=0&limit=10

You can also use the field occupation with the conceptId for the term souschef. Firstly look up the ID for souschef.  

Request URL

	https://{URL}/taxonomy/search?offset=0&limit=10&q=souschef&type=occupation-name&show-count=false

Now you can fetch all the adds that have "yrkesbenamning": "Souschef" 

Request URL

	https://{URL}/open/search?occupation=iugg_Qq9_QHH&offset=0&limit=10

Adds that have been registered by the employer so that the field occupation is set will now have the value “yrkesbenamning”:”Souschef” in the response JSON. This will give a smaller result set with a higher certainty of actually being for souschef jobs, however the result set will likely miss a few relevant adds where it hasn't been set. Hopefully you will find that the larger set is the more usable since there are multiple sorting factors working to put the least relevant adds at the end of the result set.

###Getting all the jobs in the IT industry 
Firstly use the jobtech Taxonomy endpoint to get the conceptId to find the occupation field you’re looking for. We'll list all the occupations fields since there arent that many.

Request URL

	https://{URL}/taxonomy/search?offset=0&limit=10&type=occupation-field&show-count=false
	
	
In the respone body you’ll find the conceptId for the term Data/IT. Use this with the search endpoint to define the field in which you want to get all the jobs.

Request URL

		https://{URL}/open/search?field=apaJ_2ja_LuF&offset=0&limit=10

###Getting all the jobs as a pre school teacher in Luleå and Norrbottens län
Use the taxonomy search to get the conceptId for the term förskollärare. This can be done with a free text text query where you’ll also see other terms than occupation titles

Request URL

	https://{URL}/taxonomy/search?offset=0&limit=10&q=f%C3%B6rskoll%C3%A4rare&show-count=false

Or use a narrowed down search where you filter competences and groupings of occupations titles that also relate to the search term förskollärare

Request URL
	
	https://{URL}/taxonomy/search?offset=0&limit=10&q=f%C3%B6rskoll%C3%A4rare&type=occupation-name&show-count=false

Getting the id of Luleå can be done the same way, with or without filtering for Municipality (kommun)
Request URL

	https://{URL}/taxonomy/search?offset=0&limit=10&q=Lule%C3%A5&show-count=false
	https://{URL}/taxonomy/search?offset=0&limit=10&q=Lule%C3%A5&type=municipality&show-count=false


So now we got the conceptId for Luleå and Förskollärare we can combine them

Request URL

	https://{URL}/open/search?occupation=3oGcRGX83S&municipality=51WRN_Mtjk&offset=0&limit=10

Not a whole lot of adds? Lets expand the search with Norrbottens län. When using both the municipality AND the county. The more local one - municipality will be prioritised in the sorting order.
To get the conceptId for Norbottens län search for it in the Jobtech taxonomy endpoint

Request URL

	https://{URL}/taxonomy/search?offset=0&limit=10&q=norrbottens%20l%C3%A4n&type=county&show-count=false

Now we add this as well to our search for relevant job adds

Request URL

	https://{URL}/open/search?occupation=rUcW_z9R_Qsv&municipality=2580&region=9hXe_F4g_eTG&offset=0&limit=10

Hopefully a few more hits this time. 

###Getting all the jobs since date and time - demonstrating how to use offset
A very common use case is COLLECT ALL THE ADDS. Typically an automated proccess with a set frequence. We want all the adds so lets max out the result set limit to 100

Request URL

	https://{URL}/open/search?published-after=2019-02-14T13%3A13%3A13&offset=0&limit=100
	
In my case the first row of the response says "antal_platsannonser": 168, while I got just 100 adds.
how do i get the next 68? I use the ofset like this and fetch the last 68 adds.

Request URL 

	https://{URL}/open/search?published-after=2019-02-14T13%3A13%3A13&offset=100&limit=100


#TODO 
Good example of how to use position
Good example of what to use qfields for	

	
	
