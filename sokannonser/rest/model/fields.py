from sokannonser.repository import taxonomy

# QUERYFIELDS
ID = 'id'
EXTERNAL_ID = 'external_id'
AD_URL = 'webpage_url'
LOGO_URL = 'logo_url'
HEADLINE = 'headline'
APPLICATION_DEADLINE = 'application_deadline'
NUMBER_OF_VACANCIES = 'number_of_vacancies'
DESCRIPTION_TEXT = 'description.text'
DESCRIPTION_COMPANY_INFORMATION = 'description.company_information'
DESCRIPTION_NEEDS = 'description.needs'
DESCRIPTION_REQUIREMENTS = 'description.requirements'
DESCRIPTION_CONDITIONS = 'description.conditions'
WORKPLACE_ID = 'workplace_id'
EMPLOYMENT_TYPE = 'employment_type'
SALARY_TYPE = 'salary_type'
SALARY_DESCRIPTON = 'salary_description'
DURATION = 'duration'
WORKING_HOURS_TYPE = 'working_hours_type'
SCOPE_OF_WORK_MIN = 'scope_of_work.min'
SCOPE_OF_WORK_MAX = 'scope_of_work.max'
ACCESS = 'access'
EMPLOYER_ID = 'employer.id'
EMPLOYER_PHONE_NUMBER = 'employer.phone_number'
EMPLOYER_EMAIL = 'employer.email'
EMPLOYER_URL = 'employer.url'
EMPLOYER_ORGANIZATION_NUMBER = 'employer.organization_number'
EMPLOYER_NAME = 'employer.name'
EMPLOYER_WORKPLACE = 'employer.workplace'
APPLICATION_DETAILS_INFORMATION = 'application_details.information'
APPLICATION_DETAILS_REFERENCE = 'application_details.reference'
APPLICATION_DETAILS_EMAIL = 'application_details.email'
APPLICATION_DETAILS_VIA_AF = 'application_details.via_af'
APPLICATION_DETAILS_URL = 'application_details.url'
APPLICATION_DETAILS_OTHER = 'application_details.other'
EXPERIENCE_REQUIRED = 'experience_required'
ACCESS_TO_OWN_CAR = 'access_to_own_car'
DRIVING_LICENCE_REQUIRED = 'driving_license_required'
DRIVING_LICENCE = 'driving_license'
OCCUPATION = 'occupation'
OCCUPATION_GROUP = 'occupation_group'
OCCUPATION_FIELD = 'occupation_field'
CONCEPT_ID = 'concept_id'
LABEL = 'label'
LEGACY_AMS_TAXONOMY_ID = 'legacy_ams_taxonomy_id'
WORKPLACE_ADDRESS_MUNICIPALITY_CODE = 'workplace_address.municipality_code'
WORKPLACE_ADDRESS_MUNICIPALITY_CONCEPT_ID = 'workplace_address.municipality_concept_id'
WORKPLACE_ADDRESS_MUNICIPALITY = 'workplace_address.municipality'
WORKPLACE_ADDRESS_REGION_CODE = 'workplace_address.region_code'
WORKPLACE_ADDRESS_REGION_CONCEPT_ID = 'workplace_address.region_concept_id'
WORKPLACE_ADDRESS_REGION = 'workplace_address.region'
WORKPLACE_ADDRESS_COUNTRY_CODE = 'workplace_address.country_code'
WORKPLACE_ADDRESS_COUNTRY_CONCEPT_ID = 'workplace_address.country_concept_id'
WORKPLACE_ADDRESS_COUNTRY = 'workplace_address.country'
WORKPLACE_ADDRESS_STREET_ADDRESS = 'workplace_address.street_address'
WORKPLACE_ADDRESS_POSTCODE = 'workplace_address.postcode'
WORKPLACE_ADDRESS_CITY = 'workplace_address.city'
WORKPLACE_ADDRESS_COORDINATES = 'workplace_address.coordinates'
MUST_HAVE_SKILLS = 'must_have.skills'
MUST_HAVE_LANGUAGES = 'must_have.languages'
MUST_HAVE_WORK_EXPERIENCES = 'must_have.work_experiences'
NICE_TO_HAVE_SKILLS = 'nice_to_have.skills'
NICE_TO_HAVE_LANGUAGES = 'nice_to_have.languages'
NICE_TO_HAVE_WORK_EXPERIENCES = 'nice_to_have.work_experiences'
PUBLICATION_DATE = 'publication_date'
LAST_PUBLICATION_DATE = 'last_publication_date'
REMOVED = 'removed'
REMOVED_DATE = 'removed_date'
SOURCE_TYPE = 'source_type'

KEYWORDS_ENRICHED = 'keywords.enriched'
KEYWORDS_ENRICHED_SYNONYMS = 'keywords.enriched_synonyms'
KEYWORDS_EXTRACTED = 'keywords.extracted'

sort_options = {
    'relevance': ["_score", {ID: "asc"}],
    'pubdate-desc': [{PUBLICATION_DATE: "desc"}, "_score", {ID: "asc"}],
    'pubdate-asc':  [{PUBLICATION_DATE: "asc"}, "_score",  {ID: "asc"}],
    'applydate-desc': [{APPLICATION_DEADLINE: "desc"}, "_score", {ID: "asc"}],
    'applydate-asc': [{APPLICATION_DEADLINE: "asc"}, "_score", {ID: "asc"}],
    'updated': [{"timestamp": "desc"}, "_score", {ID: "asc"}],
}
stats_options = {
    taxonomy.OCCUPATION: "%s.%s.keyword" % (OCCUPATION, LEGACY_AMS_TAXONOMY_ID),
    taxonomy.GROUP: "%s.%s.keyword" % (OCCUPATION_GROUP, LEGACY_AMS_TAXONOMY_ID),
    taxonomy.FIELD: "%s.%s.keyword" % (OCCUPATION_FIELD, LEGACY_AMS_TAXONOMY_ID),
    taxonomy.SKILL: "%s.%s.keyword" % (MUST_HAVE_SKILLS, LEGACY_AMS_TAXONOMY_ID),
}
