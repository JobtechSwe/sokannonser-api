Changelog Application Jobsearch
===============================
# 1.16.0
* Fix multi word /complete spelling bug
* Set DEFAULT_FREETEXT_BOOL_METHOD to 'or'
* Add "abroad" field

# 1.15.0
* Add occupation-collection filter parameter to search
* Remove flags 'x-feature-allow-empty-typeahead', 'x-feature-include-synonyms-typeahead', 'x-feature-spellcheck-typeahead', 'x-feature-suggest-extra-word' and set behavior as if they were set to 'True'
* Fix bug in complete that gave geographical suggestions that were not relevant

# 1.14.1
* Enable "false negative" (i.e. free text search in ad text). 
  Toggled by new x-feature parameter where disabled is default.

# 1.14.0
* Use new version of jae elasticsearch index (i.e. v-2.0.1.210) for Ontology dictionary. 
  This is dependent on calling the new enrichment endpoint from the elastic importer, that should correspond.
* Add two new fields for filtering on the jobstream endpoint; occupation concept id and location concept id.

# 1.13.2
* Fix max score bug
* Add slack client

# 1.13.1
* Set APM log level

# 1.13.0
* Add snapshot endpoint to Jobstream. To download all the currently published ads for bootstraping scenarios.
* Add locations to the stats feature in Jobsearch
* Add updated-before-date to Jobstream so its possible to set a time span for ad events to stream
* Fix removed ads ID data type inconsistency 
* Add test cases

# 1.12.1
* Add limit to complete endpoint

# 1.12.0
* Allow empty space for autocomplete endpoint
* Phrase search searches in both description.text and headline

# 1.11.1
* Add concept Id to aggregation

## 1.11.0
* Suggest extra word
* Add taxonomy description
* Fix spell check extra space problem

## 1.10.0
* Auto complete & spell check

## 1.9.0
* Add one field called unspecified sweden workplace

## 1.8.1
* Fixes bug that searched several fields for identified occupations.

## 1.8.0
* Bug fixes
* Adds concept ID for municipality, region and country in workplace_address
* Changes behaviour in search for locations. Any locations are now treated as boolean OR query.
* Adds "phrase searching". Use quotes to search the ad text for specific phrases.
* Adds feature toggle to disable query analysis in favour of simpler freetext search.
* Adds spellchecking typeahead feature toggle.
* Add prefix and postfix wildcard ('*') to search for partial words in ad text.

## 1.7.2
* Comma treated as delimiter in freetext queries
* Fixes a bug that caused the employer field to be queried when it shouldn't
* Fixes a bug in taxonomy-search where some labels couldn't be searched
* Only display logo_url if available

## 1.7.1
* Fix for terms containing hash/# in typeahead
* Changed relevance sort order to have descending publication date as secondary

## 1.7.0
* Adds ML enriched locations to typeahead
* Fixes a bug that wouldn't display number of ads for municipalities and regions in taxonomy search.
* Adds header x-feature-include-synonyms-typeahead for choosing if enriched synonyms should be included in typeahead.

## 1.6.0
* Introduces new lowercase type for request parsing
* Fixes a bug in context-unaware typeahead
* Fixes plus/minus-searches in employer
* Adds header x-feature-freetext-bool-method for choosing search method for unclassified freetext words.  
* Adds header x-feature-allow-empty-typeahead, enabling empty queries in typeahead. 
* Adds ML-enriched searches for location

## 1.5.1
* Bugfix reverting freetextsearch for locations in ad descriptions.

## 1.5.0
* Search-contextual switch for typeahead
* Fixes an issue with taxonomy search

## 1.4.3
* Buggfixes for freetext search and location.

## 1.4.2
* Buggfixes and documentation updates

## 1.4.1
* New endpoint for fetching company logo file

## 1.4.0
* New webpage url field in job ad
* New logo url field in job ad
* Language added as filter in taxonomy search

## 1.3.0
* New parameter: relevance-threshold
* Introduces new field: score
* Location searches in headline instead of description text
* Adds secondary sorting on relevance for all sort options

## 1.2.0
* Parameter published-after now supports number of minutes as parameter
* Location search in ad description requires exact phrase
* Employer name is no longer default in typeahead
* Ad loading now accepts alternate id
* Queries now once again supports alternate locations in query
* Typeahead rework to include all variants of query string
* Fixes a bug in typeahead where location would be removed from choices
* Fixes a bug in typeahead for capitalized searchwords
* Fixes a bug in typeahead for '<' and '>'

## 1.1.0
* Adds ability to search for IDs in Jobtech Taxonomy.
* More comprehensive typeahead functionality which includes bigrams and complete phrase.
* Compensates for timezone offset in date filter    
* Proper response model in swagger.json
* Freetext matches in headline always qualifies as a hit
* Narrows results for freetext query when using 'unknown words' instead of widening.
* Makes freetext search more accurate when searching headlines.

## 1.0.0
* Initial release
