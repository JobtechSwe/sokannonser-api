#Search API for job adds - getting started

The aim of this text is to walk you through what you're seeing in the Swagger UI so you can get a bit of orientation on what can be done with the SOKANNONSER API. 

This service for open job adds consists of three endpoints. One meant for searching for job adds and one meant for fetching job adds by ID. The third endpoint provides labour market terms and their corresponding unique ID’s. For some fields these keys are required and the endpoint JOBTECH TAXONOMY API is an easy way to look them up.

##Examples 

###Getting all the jobs in the geographical area Dalarnas län
Use the Jobtech Taxonomy endpoint to make a free text query for Dalarnas Län

Request URL

	https://jobs.dev.services.jtech.se/vf/search?offset=0&limit=10&q=dalarnas%20l%C3%A4n&show-count=false


Or you can use the Jobtech Taxonomy endpoint to list county codes

Request URL

	https://jobs.dev.services.jtech.se/vf/search?offset=0&limit=10&type=county&show-count=false

The result set will contain the concepId for Dalarnas län, 2Hi6JUUemM, which you can now use for the region field in a request with the search endpoint. The result set also contains "id": "20", which is the BLABLABLA id for Dalarnas län. For geographical terms these work as well as the conceptId's if you are one of those people who have them memorized :)

Request URL 	

	https://jobs.dev.services.jtech.se/open/search?region=oDpK_oZ2_WYt&offset=0&limit=10
	https://jobs.dev.services.jtech.se/open/search?region=20&offset=0&limit=10




###Getting all the adds for the occupation souschef

The easiest way to get the adds that contain a specific word is to use a free text query 

Request URL

	https://jobs.dev.services.jtech.se/open/search?q=souschef&offset=0&limit=10

You can also use the field occupation with the conceptId for the term souschef. Firstly look up the ID for souschef.  

Request URL

	https://jobs.dev.services.jtech.se/vf/search?offset=0&limit=10&q=souschef&type=occupation-name&show-count=false

Now you can fetch all the adds that have "yrkesbenamning": "Souschef" 

Request URL

	https://jobs.dev.services.jtech.se/open/search?occupation=iugg_Qq9_QHH&offset=0&limit=10

Adds that have been registered by the employer so that the field occupation is set will now have the value “yrkesbenamning”:”Souschef” in the response JSON. This will give a smaller result set with a higher certainty of actually being for souschef jobs, however the result set will likely miss a few relevant adds where it hasn't been set. Hopefully you will find that the larger set is the more usable since there are multiple sorting factors working to put the least relevant adds at the end of the result set.



###Getting all the jobs in the IT industry 

Firstly use the jobtech Taxonomy endpoint to get the conceptId to find the occupation field you’re looking for. We'll list all the occupations fields since there arent that many.

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

Not a whole lot of adds? Lets expand the search with Norrbottens län. When using both the municipality AND the county. The more local one - municipality will be prioritised in the sorting order.
To get the conceptId for Norbottens län search for it in the Jobtech taxonomy endpoint

Request URL

	https://jobs.dev.services.jtech.se/vf/search?offset=0&limit=10&q=norrbottens%20l%C3%A4n&type=county&show-count=false

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

	
	
