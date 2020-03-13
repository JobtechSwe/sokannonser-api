Changelog Application Jobsearch
===============================
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
