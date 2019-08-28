## Result set

 ### Meta data for your search request
When making a search request the resulting response will start with some meta-info about your result

 #### "total": 
"value": Total Number of ads matching your search

 "positions": Total number of  vaccancies for your search

 "query_time_in_millis": How long did the actuals search take

 "result_time_in_millis": How long did  the total roundtrip take

 "stats": {},

 "freetext_concepts": {},

 "hits": Placeholder for zero to * ads



 ### Object data
Then comes the actual ads 

 "id": The ID you can use in Open-AD-ID Endpoint

  !!! PB vill ha men vill externa? "external_id":

 "relevance":

 "headline": The headline of the ad

 "application_deadline": Last possible day to apply for the job,

 "number_of_vacancies": number of vacancies for this ad

 #### "description": 
"text": The text body of the ad 

 "company_information": Usually null

 "needs": Usually null

 "requirements": Usually null

 "conditions": Full time, part time, until further notice etc

 #### "employment_type": {

 "concept_id": Stable ID for label

 "label": One out of these four "Vanlig anställning", "Sommarjobb / feriejobb", "Arbete utomlands", "Behovsanställning"

 "legacy_ams_taxonomy_id": Legacy id for label


 #### "salary_type": 
"concept_id": Stable ID for label

 "label": "Fast månads- vecko- eller timlön",

 "legacy_ams_taxonomy_id":Legacy id for label

 #### "duration": 
"concept_id": Stable ID for label

 "label": Duration of the employment

 "legacy_ams_taxonomy_id": Legacy id for label

 #### "working_hours_type":
"concept_id": Stable ID for label

 "label": Full time, part time 

 "legacy_ams_taxonomy_id": Legacy id for label


 #### "scope_of_work": {
"min": Minimum percentage of full time

 "max": Maximum percentage of full time

 #### "access": 
"access": When will the applicant start

 #### "employer": {
"phone_number": Phone number of employer

 "email": Email of employer

 "url": Employer website

 "organization_number": The employers swedish organization number typically given by Bolagsverket

 "name": The name of the employer

 "workplace": Where the job is, this field makes most sense with larger employer oranisations

 #### "application_details": 

 "information": information about how to apply

 "reference": reference person with the employer for application

 "email": email adress to apply to

 "via_af": if application should be made through AF

 "url": adress if application should be made via a website

 "other": other information about how to apply


 #### Top level
"experience_required": boolean if experience required or not

 "access_to_own_car": boolean if applicant need to have a car to apply

 "driving_license_required": boolean if you need to hold a drivers license or not

 #### "driving_license": 

 "concept_id": Stable ID for label

 "label": the label value of the drivers license required b, c, d etc

 ##### "occupation": {
"concept_id": Stable ID for label, recommended to use for long term stability

 "label": name of the occupation

 "legacy_ams_taxonomy_id": Legacy id for label

 #### "occupation_group": {
"concept_id": Stable ID for label

 "label": what group of jobs does the occupation belong to

 "legacy_ams_taxonomy_id": Legacy id for label


 #### "occupation_field": {
"concept_id": Stable ID for label

 "label": What field of work does the occupation belong to. A field is the closest we get to define a businies as in "the IT business2

 "legacy_ams_taxonomy_id": Legacy id for label


 #### "workplace_address": {
"municipality_code": 4 digit kommun-code as defined by Skatteverket
"municipality_concept_id":Stable ID for label
"municipality": Kommun
"region_code": 2 digit code for the län
"region": Län
"country_code": 1-3 digit country code
"country": Country
"street_address": street address for the job
"postcode": 5 digit post code
"city": City where the place of work is 
"coordinates": longitud, latitud if you end up in the indian ocean switch places

 #### "must_have": {
"skills": []
"concept_id": Stable ID for label

 "label": The name of a skill            

 "weight": Weights for must_have are normally 10

 "legacy_ams_taxonomy_id": Legacy id for label

 "languages": []
"concept_id": Stable ID for label

 "label": The name of a language            

 "weight": Weights for must_have are normally 10

 "legacy_ams_taxonomy_id": Legacy id for label

 "work_experiences": []

 "concept_id": Stable ID for label

 "label": The sought after experience            

 "weight": Weights for must_have are normally 10

 "legacy_ams_taxonomy_id": Legacy id for label

 #### "nice_to have":
"skills": []

 "concept_id": Stable ID for label

 "label": The sought after skill            

 "weight": Weights for must_have are normally 10

 "legacy_ams_taxonomy_id": Legacy id for label

 "languages":[]

 "concept_id": Stable ID for label

 "label": The sought after language            

 "weight": Weights for must_have are below 10

 "legacy_ams_taxonomy_id": Legacy id for label

 "work_experiences": []

 "concept_id": Stable ID for label

 "label": The name of a experience            

 "weight": Weights for must_have are normally 10

 "legacy_ams_taxonomy_id": Legacy id for label


 "publication_date": When was the ad published

 "last_publication_date": When the ad will be unpublished

 "removed": Boolean if the add unpublished or not which can occur before the last publication date

 "removed_date": When was the add removed

 "source_type": Where did the add come from

 "timestamp": This timestamps is mostly for troubleshooting



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