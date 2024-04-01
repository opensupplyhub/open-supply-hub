# Release Notes
All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html). The format is based on the `RELEASE-NOTES-TEMPLATE.md` file.

## Release 1.11.0

## Introduction
* Product name: Open Supply Hub
* Release date: April 20, 2024

### Database changes
#### Migrations:

#### Scheme changes

### Code/API changes
* [OSDEV-923](https://opensupplyhub.atlassian.net/browse/OSDEV-923) [Uptime] Added more logs around API/List uploads & Dedupe Hub match processing
* [OSDEV-606](https://opensupplyhub.atlassian.net/browse/OSDEV-606) Contributor Sort: Allow for ascending sort of contributors on the Map page. The sort_by parameter submits type of sorting order for facilities. Default sorting will be primary by public contributors count descending and secondary by name ascending/descending and contributors count ascending.

### Architecture/Environment changes

### Bugfix

### What's new

## Release 1.10.0

## Introduction
* Product name: Open Supply Hub
* Release date: March 23, 2024

### Database changes
#### Migrations:
* 0141_delete_contributor_webhooks.py - deletes `ContributorWebhook` model
* 0142_introduce_temporary_endpoint_switcher_for_list_uploads.py - This migration introduces a temporary API endpoint switcher for list uploads.

#### Scheme changes
* [OSDEV-893](https://opensupplyhub.atlassian.net/browse/OSDEV-893) - Introduce a temporary API endpoint switcher for list uploads to enable switching to the old list upload API endpoint if the new endpoint affects production uptime.

### Code/API changes
* [OSDEV-832](https://opensupplyhub.atlassian.net/browse/OSDEV-832) API. Provide admins with a way to retrieve a user's call count in real time. Admin can see the report `API requests by user` with the number of successful and unsuccessful requests a user has made up to the current date.
* [OSDEV-831](https://opensupplyhub.atlassian.net/browse/OSDEV-831) - API. Handle Geocode errors w/ system error code when upload facility using endpoint.

### Architecture/Environment changes
* [OSDEV-693](https://opensupplyhub.atlassian.net/browse/OSDEV-693) Implement a GitHub action that applies migrations on given environment. Run migrations for `Test` environment via CLI command.
* [OSDEV-910](https://opensupplyhub.atlassian.net/browse/OSDEV-910) Add separated code quality pipelines for contricleaner, countries, django-api and frontend. After checking, it creates a code coverage report showing each particular app's code coverage. Add separated code quality jobs for code formatters.
* [OSDEV-702](https://opensupplyhub.atlassian.net/browse/OSDEV-702) Integrate a new module named `contricleaner` separately, designed to parse and validate data from various sources such as json, csv, and xls.
Move `countries` to a separate module so that it becomes possible to use both `django` and `contricleaner`.
* [OSDEV-893](https://opensupplyhub.atlassian.net/browse/OSDEV-893) - Implement CSV and XLSX file parser strategies in the ContriCleaner library, and incorporate preliminary cleanup during parsing.
* [OSDEV-915](https://opensupplyhub.atlassian.net/browse/OSDEV-915) Upgrade Kafka tools to version 3.5.2
* [OSDEV-877](https://opensupplyhub.atlassian.net/browse/OSDEV-877) Make migration run as part of "Deploy to AWS" workflow
* [OSDEV-851](https://opensupplyhub.atlassian.net/browse/OSDEV-851) Place 'terraform.tfvar' files to repository and move sensitive info to private repository opensupplyhub/ci-deployment/
* [OSDEV-938](https://opensupplyhub.atlassian.net/browse/OSDEV-938) Move cleanup helper functions to the serializer
* [OSDEV-851](https://opensupplyhub.atlassian.net/browse/OSDEV-851) Place 'terraform.tfvar' files to repository and move sensitive info to private repository opensupplyhub/ci-deployment
* [OSDEV-894](https://opensupplyhub.atlassian.net/browse/OSDEV-894) Implement Contricleaner library into create facility API endpoint (`facilities_view_set.py`)
* [OSDEV-536](https://opensupplyhub.atlassian.net/browse/OSDEV-536) In the Contricleaner library, implement parsing of fields `sector_product_type`, `sector`, and `product_type` based on commas and vertical bars.
* [OSDEV-760](https://opensupplyhub.atlassian.net/browse/OSDEV-760) In the Contricleaner library, implement parsing of fields `facility_type_processing_type`, `facility_type`, and `processing_type` based on commas and vertical bars.
* [OSDEV-893](https://opensupplyhub.atlassian.net/browse/OSDEV-893) - Implement the ContriCleaner parser for parsing facility lists immediately after list upload.

### Bugfix
* [OSDEV-549](https://opensupplyhub.atlassian.net/browse/OSDEV-549) Facility Search. Search button overlaps dropdown items. Dropdown items in search were made not to overlapping with button and containers in `Potential matches table` and `Find facility` search. The `isSideBarSearch` flag has been added to all search components to render properly regarding the place where the select is rendering.
* [OSDEV-943](https://opensupplyhub.atlassian.net/browse/OSDEV-943) Verified badges. The claim/verified icon on profiles is cut off at the bottom. The icons have been fixed and show properly.
* [OSDEV-716](https://opensupplyhub.atlassian.net/browse/OSDEV-716) Search. Lost refresh icon. The refresh icon has been made visible.
* [OSDEV-918](https://opensupplyhub.atlassian.net/browse/OSDEV-918) - ContriBot. New lists are not populating in Monday board and are not sent to slack. Added validation to throw an error for users who upload a facility list with `|` in the description field.
* [OSDEV-644](https://opensupplyhub.atlassian.net/browse/OSDEV-644) Error when trying to delete a facility with only one contributor in case that logic to clear FacilityClaimReviewNote table records missed.

### What's new
*  [OSDEV-861](https://opensupplyhub.atlassian.net/browse/OSDEV-861) API. The `API Notifications` tab has been removed so that users do not get confused about what it is, since the functionality does not exist for them. `Token:` as a header has been added above the API key on the `API` tab.
* [OSDEV-917](https://opensupplyhub.atlassian.net/browse/OSDEV-917) My Account Menu. Update order of the settings tabs. `NON-admin` user sees: My Facility / My Lists / Settings / Logout and `Admin` user sees: Dashboard / My Facility / My Lists / Settings / Logout
* [OSDEV-728](https://opensupplyhub.atlassian.net/browse/OSDEV-728) - Include `sector` data in the response of the `api/facilities/` API endpoint for the GET request, similar to what is provided in the `api/facilities/{id}` API endpoint.
* [OSDEV-802](https://opensupplyhub.atlassian.net/browse/OSDEV-802) - Distinguish API user and contributor id in the error message that pass to the Rollbar.

### Release instructions:
* Update code.
* Apply DB migrations up to the latest one.

## Release 1.9.0

## Introduction
* Product name: Open Supply Hub
* Release date: February 24, 2024

### Database changes
#### Migrations:
* 0135_disable_duplicates_and_lowercase_all_emails.py - implementing all emails to lowercase and disables duplicates
* 0136_remove_indexing_unnecessary_emails.py - This migration replaces the old `index_activity_reports_info` and `index_approved_claim` functions with similar ones that do not index emails.
* 0137_add_renewal_period_field.py - add new field to api_apilimit table & rename existing one.
Updated existing users api_apilimit records renewal_period value.
* 0138_remove_ppe_fields.py - This migration removes the PPE fields from the Facility, FacilityIndex, FacilityListItem, FacilityListItemTemp, HistoricalFacility models.
* 0139_remove_ppe_switch.py - This migration removes the ppe switch.
* 0140_remove_indexing_ppe_fields.py - This migration updates indexing functions to not index PPE fields.

#### Scheme changes
* [OSDEV-835](https://opensupplyhub.atlassian.net/browse/OSDEV-835) - Since the FacilityIndex model is primarily used to store cached facility data and display it publicly via the `/facilities/{id}` API endpoint, only public data can be shown. Therefore, caching emails to the FacilityIndex model was removed from the PostgreSQL indexing functions. All instances where emails are publicly displayed have been removed. The only remaining field is `ppe_contact_email`, but all functionality and code related to PPE will be deleted in this [OSDEV-562](https://opensupplyhub.atlassian.net/browse/OSDEV-562) ticket.
* [OSDEV-562](https://opensupplyhub.atlassian.net/browse/OSDEV-562) - Remove PPE fields (ppe_product_types, ppe_contact_email, ppe_contact_phone, ppe_website, ppe) from the `api_facility`, `api_facilityindex`, `api_facilitylistitem`, `api_facilitylistitemtemp`, `api_historicalfacility`. Remove this fields from indexing processes.

### Code/API changes
* [OSDEV-562](https://opensupplyhub.atlassian.net/browse/OSDEV-562) - Remove code related to PPE (ppe_product_types, ppe_contact_email, ppe_contact_phone, ppe_website, ppe) field from `/src/app`
* [OSDEV-562](https://opensupplyhub.atlassian.net/browse/OSDEV-562) - Remove code related to PPE (ppe_product_types, ppe_contact_email, ppe_contact_phone, ppe_website, ppe) field from `/src/dedupe-hub`
* [OSDEV 562](https://opensupplyhub.atlassian.net/browse/OSDEV-562) Remove code related to PPE (ppe_product_types, ppe_contact_email, ppe_contact_phone, ppe_website, ppe) from `/src/django`

### Architecture/Environment changes
* [OSDEV-829](https://opensupplyhub.atlassian.net/browse/OSDEV-673) Makes `minimum-ratio: 1` It allows to push code with less than 1% diff from main.

### Bugfix
* [OSDEV-848](https://opensupplyhub.atlassian.net/browse/OSDEV-848) When a user tries to create an account with an email that exists in the DB but with a different case of letters, the system returns "An error prevented signing up". Has been fixed to "A user with that email already exists."
* [OSDEV-673](https://opensupplyhub.atlassian.net/browse/OSDEV-673) When a user calls the endpoint `facility/id/history`, instead of a response, receives the error "TypeError: the JSON object must be str, bytes or bytearray, not list", in particular, this happened with the PK20190913BBJ2Y facility. A list with one element (a dictionary) was passed to the function, so an error occurred when trying to index the list with a string. Fixed.

### What's new
* API. Include token and call info on API settings tab.[OSDEV-752](https://opensupplyhub.atlassian.net/browse/OSDEV-752). Users can access a tab called `API` in account settings.From this tab, they can generate/retrieve their token and see their `API call allowance`, `current call count` and their `renewal period`.
* Make login non-case sensitive. [OSDEV-628](https://opensupplyhub.atlassian.net/browse/OSDEV-628). When the user creates an account email saving in lowercase. User  could login with any variations of casing as long as the characters are the same.
* API. Enable token generation based on API permissions in Django. [OSDEV-729](https://opensupplyhub.atlassian.net/browse/OSDEV-729). Updated Settings page to show/hide token tab by user groups. Forbid access to generate token for API if user didn't have permission groups.
* [OSDEV-219](https://opensupplyhub.atlassian.net/browse/OSDEV-219). Data moderator can merge potential match facilities from Confirm / Reject screen.
* [OSDEV-835](https://opensupplyhub.atlassian.net/browse/OSDEV-835) - Remove the display of emails in the `activity_reports` section of the `facilities/{id}` API endpoint, as email information is private.
* [OSDEV-525](https://opensupplyhub.atlassian.net/browse/OSDEV-525). Add Latitude and Longitude labels on facility page.
* API. Add a flag on API Limit page to indicate if package renews monthly or yearly. [OSDEV-781](https://opensupplyhub.atlassian.net/browse/OSDEV-781) Updated logic to support montly & yearly limitation count reset for API calls.

### Release instructions:
* Update code.
* Apply DB migrations up to the latest one.
* Run the index_facilities_new management command.


## Release 1.8.0

## Introduction
* Product name: Open Supply Hub
* Release date: January 27, 2024

### Code/API changes
* [OSDEV-690](https://opensupplyhub.atlassian.net/browse/OSDEV-690) - Correct all existing lint errors to ensure that code quality checks pass successfully via GitHub Actions and can detect new linting errors but not the old ones.
* [OSDEV-719](https://opensupplyhub.atlassian.net/browse/OSDEV-719) Introduce FacilityDownloadSerializerEmbedMode FacilityDownloadSerializer, replace FacilityIndexDownloadSerializer with combination of FacilityDownloadSerializerEmbedMode and FacilityDownloadSerializer
* [OSDEV-732](https://opensupplyhub.atlassian.net/browse/OSDEV-732) Fix issue with circular dependencies between `util.js` and `constants.jsx` modules in React app

### Architecture/Environment changes
* [OSDEV-690](https://opensupplyhub.atlassian.net/browse/OSDEV-690) - Configure running the code quality workflow as part of the continuous integration (CI) for each commit to a pull request. Both frontend (FE) and backend (BE) tests are executed, along with their respective linters. Additionally, `shellcheck` is applied to scripts within the scripts folder.
* [OSDEV-691](https://opensupplyhub.atlassian.net/browse/OSDEV-691) - Implement parallel job running for BE, FE, and bash script code quality checks. Three new scripts were created and can be used to run the same checks during local development to verify BE, FE, and bash scripts in the ./scripts folder.
* [OSDEV-692](https://opensupplyhub.atlassian.net/browse/OSDEV-691) - Implement code coverage checks for the React and Django apps using `barecheck/code-coverage-action` and generated code coverage `lcov` files. For the React app, code coverage is based on Jest tests, and for the Django app, it is based on unittest tests. If code coverage decreases, the job fails, preventing the PR from merging.
* [OSDEV-740](https://opensupplyhub.atlassian.net/browse/OSDEV-740) - Setup module for mocking Redux store (`redux-mock-store"`)
* [OSDEV-733](https://opensupplyhub.atlassian.net/browse/OSDEV-733) - Setup React test library module (`@testing-library`)

### Bugfix
* [OSDEV-718](https://opensupplyhub.atlassian.net/browse/OSDEV-718) - Fixed issue with user profile populating to other components.
* [OSDEV-727](https://opensupplyhub.atlassian.net/browse/OSDEV-720) - Downloading facilities with for Bangladesh is working again [https://opensupplyhub.org/facilities?countries=BD&sectors=Apparel](https://opensupplyhub.org/facilities?countries=BD&sectors=Apparel)

### What's new
* [OSDEV-241](https://opensupplyhub.atlassian.net/browse/OSDEV-241) - Searches with accented characters return results for accented and non accented characters.

### Database changes
#### Migrations:
* 0134_remove_sources_without_contributor -  Remove records from the Source table where the contributor is null and remove all data related to these records

### Release instructions:
* Update code
* Run migration up to 0134


## Release 1.7.3

## Introduction
* Product name: Open Supply Hub
* Release date: January 12, 2024

### Bugfix
* [OSDEV-736](https://opensupplyhub.atlassian.net/browse/OSDEV-736) Removed logic to handle text only match response data as it already removed from matching functionality in Dedupe Hub. Previously it bring an error on response for user when potential match happened.

## Release 1.7.2

## Introduction
* Product name: Open Supply Hub
* Release date: January 09, 2024

### Bugfix
* [OSDEV-721](https://opensupplyhub.atlassian.net/browse/OSDEV-721) Fixed issue with potential match logic when get facility data of match, previously it take facility id from Facility List Item, but it's wrong for Potential Match status as there is always NULL, facility id should be taken from Facility Match record in this case of Potential Match status.

## Release 1.7.1

## Introduction
* Product name: Open Supply Hub
* Release date: December 21, 2023

### Bugfix
* Fixed issue with Facility Upload API error by covered a case when facility object didn't exist (create=false) & updated timeout value while waiting to produce kafka topic message [OSDEV-713](https://opensupplyhub.atlassian.net/browse/OSDEV-713)
* [OSDEV-714](https://opensupplyhub.atlassian.net/browse/OSDEV-714) - Users can now use the map on the search page simultaneously without missing any tiles. Before fixing this issue, if the map requested tiles that weren't cached, one user might not receive all the tiles. With the bug fixed, the tile generation logic can handle multiple requests at the same time, ensuring all users get the tiles they need for the map based on their search requests.

### Code/API changes
* [OSDEV-714](https://opensupplyhub.atlassian.net/browse/OSDEV-714) - `select_for_update` and `get_or_create` have been implemented in the `retrieve_cached_tile` function to ensure that if another thread attempts to `select_for_update()`, it will block at the `get_or_create()` until the first thread's transaction commits. The `get_tile` function, which serves as an API endpoint handler for tile generation, was implemented as an atomic transaction to facilitate the use of `select_for_update()` and maintain the lock until the end of the transaction. This approach helps to prevent crashes from parallel requests attempting to create a cache record with the same primary key, corresponding to the full URL path.
* [OSDEV-711](https://opensupplyhub.atlassian.net/browse/OSDEV-711) - Make JS code related to load testing for tile generation more universal so that they can work with the HAR file provided by the developer. For that, the `ZOOM_HAR_PATH` environment variable was introduced. More test cases for tile generation were added to test the environment close to production, focusing on densely saturated regions with facilities, such as China and India. The README.md file for the load tests was updated to reflect the changes made.

## Release 1.7.0

## Introduction
* Product name: Open Supply Hub
* Release date: December 19, 2023

### Database changes
#### Migrations:
* 0130_introduce_separate_data_gathering_functions_for_the_index_table_columns - This migration:
    - rename `api_facilityindexnew` -> `api_facilityindex`
    - introduces separate data-gathering functions for the `api_facilityindexnew` table columns and makes the `index_facilities` and `index_facilities_by` procedures use them.
    This migration is irreversible.
* 0131_introduce_sql_triggers_instead_of_django_signals - This migration introduces SQL triggers instead of Django signals. The migration is revertable.
* 0132_add_moderation_mode_field - This migration adds the field `is_moderation_mode` to table `api_user`.
* 0133_introduce_tile_caching - This migration creates the TileCache table and the DynamicSetting table. This migration is reversible.

#### Scheme changes
* [OSDEV-622](https://opensupplyhub.atlassian.net/browse/OSDEV-622) - Separate data-gathering functions were created for the `api_facilityindexnew` table columns to collect data independently of the main procedure. The `index_facilities` and `index_facilities_by` procedures were updated to use new separate functions for collecting data for the `api_facilityindexnew` table columns that require long SQL queries.
* [OSDEV-595](https://opensupplyhub.atlassian.net/browse/OSDEV-595) - Rename FacilityIndexNew to FacilityIndex
* [OSDEV-623](https://opensupplyhub.atlassian.net/browse/OSDEV-623), [OSDEV-624](https://opensupplyhub.atlassian.net/browse/OSDEV-624), [OSDEV-638](https://opensupplyhub.atlassian.net/browse/OSDEV-638) - New SQL triggers have been introduced to handle changes in the `api_contributor`, `api_extendedfield`, `api_facility`, `api_facilityclaim`, `api_facilitylistitem`, `api_facilitymatch`, `api_source`, and `api_facilitylist` tables at the database level. This change is essential for the future functionality of DedupeHub, which will communicate directly with the database. All the Django signals have been removed. Additionally, reindexing of the necessary columns of the index table has been transferred to these triggers, eliminating the need for the large SQL procedure previously used in conjunction with Django signals.
* [OSDEV-637](https://opensupplyhub.atlassian.net/browse/OSDEV-637) - Add field `is_moderation_mode` to table `api_user`.
* [OSDEV-687](https://opensupplyhub.atlassian.net/browse/OSDEV-687) - The TileCache table was created to store cached tiles, and the DynamicSetting table was established to dynamically control app settings, specifically the expiration time of cached tiles.

### Code/API changes
* Update copy for "example" entries for List & Description fields & Contributor list page:
    - Update copy of Facility List example to: example: **Your Organization’s Name** Facility List June 2023
    - Update copy of Facility Description example to: example: This is the **Your Organization’s Name** list of suppliers for their retail products valid from Jan 2023 to June 2023
    - Update copy of rejected message to: "This list was rejected and will not be processed."
[OSDEV-640](https://opensupplyhub.atlassian.net/browse/OSDEV-640)
* In the Facility Claim Request form the field 'Preferred method of contact' has been done not mandatory. - [OSDEV-560](https://opensupplyhub.atlassian.net/browse/OSDEV-560)
* The new parameter `is_moderation_mode` has been added to GET and POST requests of the `/user-profile/{ID}/` API endpoint. - [OSDEV-637](https://opensupplyhub.atlassian.net/browse/OSDEV-637)
* [OSDEV-687](https://opensupplyhub.atlassian.net/browse/OSDEV-687) - Implement cache logic for the get_tile view to either use a cached tile or generate a new tile for caching. When a user interacts with the map and makes a new request for a tile, the system checks if the requested tile, identified by its path, is already cached in the database. If the tile is already cached in the TileCache table, the cached tile binary data is retrieved and returned, avoiding the need to regenerate the tile for improved performance. Each cached tile has a default expiration period of 604,800 seconds (7 days). However, the admin can reconfigure this duration in the Django admin panel.
* Delete all Jenkins-related files since Jenkins is no longer in use.
* Move the maintenance page to the project repository, specifically to `src/maintenance`, to track the history of its changes.

### Architecture/Environment changes
* Remove FacilityDownloadSerializer and replace it with FacilityIndexDownloadSerializer
* Add a special Django management command, `install_db_exts`, that will install all the necessary PostgreSQL extensions for the database based on the required DB extensions for the 1.7.0 release.
* Create the `reset_database` Django management command that resets the database and repopulates it with fixture data, including facilities and matches. Update the `scripts/reset_database` shell script to include the call to this command, making it available for local development when it needs to be run inside the failed Django container for the first time. Also, rename shell scripts and affected management commands to enhance readability.

### Bugfix
* Increase amount of facilities downloaded to 100 per red and reduce time per request in 4-5 times
Fix issue with exceeding API requests. [OSDEV-557](https://opensupplyhub.atlassian.net/browse/OSDEV-442)

### What's new
* Updated copy for "example" entries for List & Description fields & Contributor list page
[OSDEV-640](https://opensupplyhub.atlassian.net/browse/OSDEV-640)
* The field 'Preferred method of contact' has been done not mandatory in the Facility Claim Request form. When the user fills this form he/she can skip this field. - [OSDEV-560](https://opensupplyhub.atlassian.net/browse/OSDEV-560)
* Data Moderator Profile. Implement the ability to activate the Merge function on the Facility Search page. - [OSDEV-637](https://opensupplyhub.atlassian.net/browse/OSDEV-637)
* [OSDEV-302](https://opensupplyhub.atlassian.net/browse/OSDEV-302), [OSDEV-667](https://opensupplyhub.atlassian.net/browse/OSDEV-667) - Enable data moderators to trigger merges from the search results screen. Checkboxes were added to the search page right before each item in the search results to allow users to select facilities for merging. A "Merge" button was also implemented to open the Merge modal window, where all the data about the selected facilities is downloaded.
* [OSDEV-684](https://opensupplyhub.atlassian.net/browse/OSDEV-684) Removed Google Translate Plug-In in the system & UI Element

### Release instructions:
* apply migrations up to 0133_introduce_tile_caching
* apply command index_facilities_new


## Release 1.6.1

## Introduction
* Product name: Open Supply Hub
* Release date: November 8, 2023

### Database changes
#### Migrations:
- 0130_facility_index_gin_index - implement indexes for fields on "api_facilityindexnew" table related to tile generation

#### Scheme changes
* indexing fields in api_facilityindexnew
    * contrib_types
    * contributors_id
    * lists

### Architecture/Environment changes
* Reconfigure CPU resources so that every worker uses 2 cores - [OSDEV-657](https://opensupplyhub.atlassian.net/browse/OSDEV-657)
* Add Code Quality pipelines

### Bugfix
* Implement indexing of fields related to tile generation in api_facilityindexnew table [OSDEV-654](https://opensupplyhub.atlassian.net/browse/OSDEV-654)

### Release instructions:
- apply migrations up to 0130_facility_index_gin_index


## Release 1.6.0

## Introduction
* Product name: Open Supply Hub
* Release date: November 4, 2023

### Database changes
#### Migrations:
- 0126_add_tables_a_b_test - add tables api_facilitylistitemtemp & api_facilitymatchtemp for A/B Test purpose
- 0127_search_by_private_contributor_types - add contributor types from non-public lists to api_facilityindexnew table
- 0128_custom_text_implementation - creates custom_text SQL functions and updated index_facilities and index_facilities_by to use it
- 0129_delete_facility_index - removes api_facilityindex table

#### Scheme changes
* introduce fields to api_facility_list_items
    * raw_json:JSON
    * raw_header:Text
* introduce table api_facilitylistitemfield - key-value storage for both mandatory and custom facility list item fields.
* introduce procedure custom_text - evaluates array required for advanced search by custom fields
* update index_facilities and index_facilities_by procedures to evaluate custom_text add custom_text_serach using custom_text from above
* introduce tables api_facilitylistitemtemp & api_facilitymatchtemp as a copy of api_facilitylistitem & api_facilitymatch for A/B Test to store match results
* remove api_facilityindex table

### Code/API changes
* Endpoint /contributor-lists/ has been deprecated
* The new endpoint /contributor-lists-sorted/ has been created: View Facility Lists that are both active and approved filtered by Contributor sorted by creation date and changed response type to list of objects.
- [OSDEV-218](https://opensupplyhub.atlassian.net/browse/OSDEV-218)
* Connect new tables (api_facilitylistitemtemp & api_facilitymatchtemp) to existing parsing & geocoding result storing
* Trigger matching process on Dedupe Hub through Kafka Producer on Django side
- [OSDEV-507](https://opensupplyhub.atlassian.net/browse/OSDEV-507)

### Architecture/Environment changes
* Update rollbar token - [OSDEV-581](https://opensupplyhub.atlassian.net/browse/OSHUB-581)
* Deployed Dedupe Hub standalone service & Kafka event streaming service for A/B Test purpose - [OSDEV-507](https://opensupplyhub.atlassian.net/browse/OSDEV-507)
* Kafka added to infrastructure (AWS MSK) - [OSDEV-428](https://opensupplyhub.atlassian.net/browse/OSDEV-428)
* Dedupe Hub service added to ECS Cluster - [OSDEV-430](https://opensupplyhub.atlassian.net/browse/OSDEV-430)
* Infrastructure environments not depended on python (django app environment) - [OSDEV-424](https://opensupplyhub.atlassian.net/browse/OSDEV-424)
* Reworked algorithm to manage DNS records - [OSDEV-414](https://opensupplyhub.atlassian.net/browse/OSDEV-414)
* Update AWS Terraform provider, move from Azavea repo & upgrade few modules for Terraform - [OSDEV-405](https://opensupplyhub.atlassian.net/browse/OSDEV-405)
* Replaced usage of FacilityIndex model by FacilityIndexNew.
* Removed FacilityIndex model
* Removed function get_custom_text
* Removed function index_custom_text from transactions
* Removed function index_extended_fields from transactions
* Removed function index_facilities from transactions
* Removed function index_sectors from transactions
* Removed get_sector_dict from transactions

### Bugfix
* Make search by non-public contributor types available [OSDEV-307](https://opensupplyhub.atlassian.net/browse/OSDEV-307)
* Make possibility to create embed map configuration for constributors with more than 2500 facilities [OSDEV-585](https://opensupplyhub.atlassian.net/browse/OSDEV-585)
* Make possibility to save data facilities even if they have no stored location [OSDEV-596](https://opensupplyhub.atlassian.net/browse/OSDEV-596)

### What's new
* Update README.md with the most recent information - [OSDEV-580](https://opensupplyhub.atlassian.net/browse/OSHUB-580)
* Update Rollbar's post_server_item tokens - [OSDEV-581](https://opensupplyhub.atlassian.net/browse/OSHUB-581)
* Contributor Lists. Order lists from a contributor by newest to oldest list - [OSDEV-218](https://opensupplyhub.atlassian.net/browse/OSDEV-218)

### Release instructions:
- apply migrations up to 0124_itroduce_raw_json
- execute command fill_raw_json
- apply migrations up to 0129_delete_facility_index
- apply command index_facilities_new
