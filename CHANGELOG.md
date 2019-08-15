Changelog Application Jobsearch
===============================

## 1.4.0
* New webpage url field in job ad
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
