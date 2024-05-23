# Release Notes
All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html). The format is based on the `RELEASE-NOTES-TEMPLATE.md` file.

## Release 1.13.0

## Introduction
* Product name: Open Supply Hub
* Release date: June 01, 2024

### Database changes
#### Migrations:
* *Describe migrations here.*

#### Scheme changes
* *Describe scheme changes here.*

### Code/API changes
* [OSDEV-994](https://opensupplyhub.atlassian.net/browse/OSDEV-994) API. Update to pass all merge events to user based on contrib id. A non-admin API user makes:
- a GET call to /moderation-events/merge/
and receives information about merges that have occurred for all contributors.
- a GET call to /moderation-events/merge/?contributors=<id_number_x>&contributors=<id_number_y>&contributors=<id_number_z>
and receives information about merges that have occurred for the contributors with the specified IDs.

### Architecture/Environment changes
* [OSDEV-1003](https://opensupplyhub.atlassian.net/browse/OSDEV-1003) - Added automatic building for the Logstash Docker image in the `Deploy to AWS` workflow. Refactored the `Deploy to AWS` workflow to remove redundant setting values for `build-args` of the `docker/build-push-action` action in cases where the values are not used.

### Bugfix
* [OSDEV-1056](https://opensupplyhub.atlassian.net/browse/OSDEV-1056) - Refactor OS Hub member's email anonymization.
* [OSDEV-1022](https://opensupplyhub.atlassian.net/browse/OSDEV-1022) - Fix updating facility claim for user. Bring the format of extended field values to the same format as for List / API upload during processing. This has been done because extending fields processing is happening both for uploading and claim update.

### What's new
* [OSDEV-1049](https://opensupplyhub.atlassian.net/browse/OSDEV-1049) Update Release protocol.
* [OSDEV-922](https://opensupplyhub.atlassian.net/browse/OSDEV-922) Consent Message. Update wording of consent opt in message on Open Supply Hub. A user who verifies Open Supply Hub for the first time can see the updated message.

### Release instructions:
* Update code.

## Release 1.12.0

## Introduction
* Product name: Open Supply Hub
* Release date: May 18, 2024

### Database changes
#### Migrations:
* 0143_create_facility_claim_attachment_table.py - create api_facilityclaimattachments table to store claimant attachments per facility claim
* 0144_remove_unnecessary_columns_from_facility_claim.py - This migration replaces the old `index_approved_claim` function with a similar one that does not index the `preferred_contact_method` field. Additionally, the migration removes `email` and `preferred_contact_method` from the `FacilityClaim` model and the respective history table.

#### Scheme changes
* [OSDEV-931](https://opensupplyhub.atlassian.net/browse/OSDEV-931) - Since `email` and `preferred_contact_method` are no longer necessary for the claim form, they have been removed from the `FacilityClaim` model and the respective history table. Additionally, the old `index_approved_claim` function has been replaced with a similar one that does not index the `preferred_contact_method` field.

### Code/API changes
* [OSDEV-1021](https://opensupplyhub.atlassian.net/browse/OSDEV-1021) Update the release protocol. The release protocol has been updated with the recent changes. Has been added the section about reloading DedupeHub and QA notification.
* [OSDEV-997](https://opensupplyhub.atlassian.net/browse/OSDEV-997) - A new method, `message_claimant`, was added to the `FacilityClaimViewSet` for handling a POST request on the url-path `message-claimant` for messages to the claimant.
Mail templates for the message to the claimant and the claims team signature were also added.

### Architecture/Environment changes
* [OSDEV-897](https://opensupplyhub.atlassian.net/browse/OSDEV-897) FE(React) app. An appropriate local Docker environment is configured for the application. A local Docker environment has been created for the React application. Renamed the `app` folder to `react` to be clearer in the project. Replaced name in the code base. Removed unnecessary commands.
* [OSDEV-862](https://opensupplyhub.atlassian.net/browse/OSDEV-862) Fix `DB - Save Anonymized DB` / `DB - Apply Anonymized DB` workflows:
  - run actions on self-hosted runners to eliminate `lack of storage` issue that happens on github's runners.
  - use the `Test` environment for  `DB - Save Anonymized DB` action
* [OSDEV-989](https://opensupplyhub.atlassian.net/browse/OSDEV-989) - The Strategy pattern was utilized to consolidate the processing of new facilities received from both API requests and list uploads. The code responsible for executing this processing was refactored, and new classes were implemented:
    * ProcessingFacility - abstract class for facility processing
    * ProcessingFacilityList - class to process a facility list
    * ProcessingFacilityAPI - class to process a facility from an API request
    * ProcessingFacilityExecutor - class defines which interface to execute for the processing of a facility
* Resource allocation has been optimized for the Test environment. The number of ECS tasks in the Test environment has been reduced from 4 to 2, while maintaining system stability.
* [OSDEV-870](https://opensupplyhub.atlassian.net/browse/OSDEV-870) - In `docker-compose` for the `api-app`  added dependency that helps to fix connection with the database during tests pipelines for Dedupe-Hub:
* [OSDEV-1001](https://opensupplyhub.atlassian.net/browse/OSDEV-1001) - Deploy OpenSearch service to OS Hub infrastructure.
```
database:
    condition: service_healthy
```
* [OSDEV-1024](https://opensupplyhub.atlassian.net/browse/OSDEV-1024) - Dedupe Hub. Revise service configurations and refine gazetteer retraining. Remove option `--reload` & decrease number of workers in Dedupe Hub service configuration. Refactor initial rebuilding of gazetteer.
* [OSDEV-885](https://opensupplyhub.atlassian.net/browse/OSDEV-885) - Implement option to reset database for `Dev`, `Test` and `Pre-prod` environmet to `Deploy to AWS` pipleine
* [OSDEV-1002](https://opensupplyhub.atlassian.net/browse/OSDEV-1002) - The following changes have been done:
    * Prepared initial AWS infrastructure via Terraform for the Logstash service, including configuring AWS EFS storage to save the pointer of the last run for the jdbc plugin. Essentially, after deploying updated Terraform code to an environment, ECS task definition, ECR repository, ECS service, along with EFS storage, will be set up for Logstash to function.
    * Moved the PoC solution of the Logstash + Elasticsearch setup to the repository to avoid losing it. Further work is needed as the solution requires development and is not functioning smoothly.
* In response to recent stability observations of the staging environment, resource allocation has been optimized by reducing the number of ECS tasks from 8 to 6 for the Django app instances, thus maintaining system stability.


### Bugfix
* [OSDEV-870](https://opensupplyhub.atlassian.net/browse/OSDEV-870) - The returning confirm/reject URLs were fixed when a facility has been matched. Changes were made to the Dedupe-Hub to prevent adding rows with empty fields to the `api_facilitymatch` and `api_facilitymatchtemp` tables when the count of matches is more than one.
* [OSDEV-744](https://opensupplyhub.atlassian.net/browse/OSDEV-744) - API. When user want to confirm/reject potential_match it didn't found a match through `id`, was fixed by provided valid `id` from `api_facilitymatch` table.
* [OSDEV-1052](https://opensupplyhub.atlassian.net/browse/OSDEV-1052) - Replace data@opensupplyhub by claims@opensupplyhub in the Frontend

### What's new
* [OSDEV-975](https://opensupplyhub.atlassian.net/browse/OSDEV-975) Reporting. Number of facilities with at least one extended field.`Facilities with Extended Field Data` report has been rewritten from Django ORM to SQL to optimize and speed up time of the report generation. Added two columns `With At Least 1 Extended Field` and `Sector`.
* [OSDEV-945](https://opensupplyhub.atlassian.net/browse/OSDEV-945) - Facility Claim. Update text of claim link on profile to "I want to claim this production location".
* [OSDEV-745](https://opensupplyhub.atlassian.net/browse/OSDEV-745) - New "Portuguese" translated resources option added to international menu.
* [OSDEV-944](https://opensupplyhub.atlassian.net/browse/OSDEV-944) - Facility claims. Short-term new screen for claim documentation.
* [OSDEV-931](https://opensupplyhub.atlassian.net/browse/OSDEV-931) - The following features have been implemented:
    * Made the Email field in the claim form uneditable, setting the claimer's email as the default value for this field.
    * Removed the _Preferred method of contact_ field from both the claim form and the claim details page in the admin dashboard.
    * Implemented redirecting a user to the claim page after navigating to the login page via the CTA link on the claim page for unauthorized users and successful login.
* [OSDEV-997](https://opensupplyhub.atlassian.net/browse/OSDEV-997) - Facility Claims. A new button, 'Message Claimant' has been added to the update status controls on the Facility Claim Details page. After successfully sending a message, the message text is recorded in the Claim Review Notes.

### Release instructions:
* Update code.
* Apply DB migrations up to the latest one.
* Run the index_facilities_new management command.


## Release 1.11.0

## Introduction
* Product name: Open Supply Hub
* Release date: April 20, 2024

### Code/API changes
* [OSDEV-923](https://opensupplyhub.atlassian.net/browse/OSDEV-923) [Uptime] Added more logs around API/List uploads & Dedupe Hub match processing
* [OSDEV-606](https://opensupplyhub.atlassian.net/browse/OSDEV-606) Contributor Sort: Allow for ascending sort of contributors on the Map page. The sort_by parameter submits type of sorting order for facilities. Default sorting will be primary by public contributors count descending and secondary by name ascending/descending and contributors count ascending.

### Architecture/Environment changes
* [OSDEV-990](https://opensupplyhub.atlassian.net/browse/OSDEV-990) - Implement a ContriCleaner facade class to simplify interaction with client code. With this change, the client code only needs to instantiate the ContriCleaner class, pass the input data, and then call the `process_data` method without the need to define strategies or other details. This abstraction helps streamline the process and encapsulate complexity.
* [OSDEV-991](https://opensupplyhub.atlassian.net/browse/OSDEV-991) - Implement a chain of pre-validation and serialization handlers in the ContriCleaner to streamline data processing. Additionally, refactor the CompositeRowSerializer to set up leaf serializers using a specialized method, ensuring loose coupling between the CompositeRowSerializer and leaf serializers. Lastly, separate serialization and validation tasks from parsing in the ContriCleaner library for improved modularity and maintainability.
* [OSDEV-1000](https://opensupplyhub.atlassian.net/browse/OSDEV-1000) - A new class `ProcessingFacility` was created that will be responsible for managing the processing of new facilities from both API requests and list uploads. The functionality of processing a new facility received from an API request, which was previously in `facilities_view_set.py`, has been moved to `processing_facility.py`.
* [OSDEV-1007](https://opensupplyhub.atlassian.net/browse/OSDEV-1007) - The functionality of processing a new facility received from list uploads, which was previously in `facility_list_view_set.py`, has been moved to `create_facility.py`.
* [OSDEV-927](https://opensupplyhub.atlassian.net/browse/OSDEV-927) - Reduce resources allocated for bastions to t3.nano.
* [OSDEV-805](https://opensupplyhub.atlassian.net/browse/OSDEV-805) - Make Environment and project tag to be applied to all resources by defaul.
* [OSDEV-862](https://opensupplyhub.atlassian.net/browse/OSDEV-862) - Add `Save Anonymized DB` and `Apply Anonymized DB` actions that provde possibility to save anonymized dump to S3 bucket and then resotre Test or Pre-Prod environment from dump stored on S3.
* [OSDEV-859](https://opensupplyhub.atlassian.net/browse/OSDEV-859) - Creates task-definitation for scheduled task that
  * creates temporary postgresdb instance from latest production snaphsot in the `test` AWS account
  * run anonymization query
  * saves anonymized snapshot and removes the instance
* In response to recent stability observations, resource allocation has been optimized, reducing the number of ECS tasks in both production and pre-production environments from 16 to 12, maintaining system stability.

### Bugfix
* [OSDEV-996](https://opensupplyhub.atlassian.net/browse/OSDEV-996) The default sorting order for embedded maps was broken (changed to Descending by # Contributors). The default sorting order for embedded maps has been fixed (changed it back to Ascending by Name).
* [OSDEV-857](https://opensupplyhub.atlassian.net/browse/OSDEV-857) [Bug] Pre-prod isn't deleted by the 'terraform destroy' script. Command for destroying repositories on AWS pre-prod has been added.
* [OSDEV-888](https://opensupplyhub.atlassian.net/browse/OSDEV-888) - Facility Profile. An error occurs when trying to open a facility from the Status Reports page. The error occurred due to activity reports with the status `pending` containing fields with `null` values and these values pass to the `format_date` function as an argument. Modified the `get_activity_reports` method in the `FacilityIndexDetailsSerializer` to prevent passing a falsy `date` argument into the `format_date` function.
* [OSDEV-984](https://opensupplyhub.atlassian.net/browse/OSDEV-984) - Facility list upload. Header validation is failing, even though all the required columns and data are filled. Prepared basic implementation for ContriCleaner to validate headers (required fields) on early stage.
* [OSDEV-660](https://opensupplyhub.atlassian.net/browse/OSDEV-660) - Remove punctuation issues with duplicated commas and double quotes while facility list uploading.
* [OSDEV-986](https://opensupplyhub.atlassian.net/browse/OSDEV-986) - Fix the population of the custom data points uploaded via lists. Ensure that the full list header is saved in the database, and that the raw data for each facility list item is saved as a string of strings, with each value separated by a comma. This way, it helps maintain backward compatibility with the functionality responsible for displaying custom data points on the embedded maps. Also, revert to the previous default logic, which saves the sector as `Unspecified` when sector, sector_product_type, or product_type have empty values.
* [OSDEV-966](https://opensupplyhub.atlassian.net/browse/OSDEV-966) - Character limit validation has been implemented in the ContriCleaner library for name, address, and sector values. It enforces a maximum length of 200 characters for both the name and address values, and restricts sector values to 50 characters each. This fix addresses the issue where user uploads containing such invalid data caused requests to fail with unexpected errors.

### What's new
* [OSDEV-974](https://opensupplyhub.atlassian.net/browse/OSDEV-974) Reporting. Contributor type by %. Admin sees in the report data for the percent of data contributors on the platform by type (this should be in percent format with two decimal places shown), only accounts that have contributed data, the data should be ordered by most recent to oldest month and display mid-month values.
* [OSDEV-912](https://opensupplyhub.atlassian.net/browse/OSDEV-912) Facility Claim. Disable editing of name and address. The Facility name (English language) & Address fields of the claim details page have been removed and cannot be edited by the claimant.
* [OSDEV-571](https://opensupplyhub.atlassian.net/browse/OSDEV-571) Claimed Facility Details. Make the "Sector" field a dropdown instead of free text field. The `Sector` field became a dropdown that is pre-populated with the platform’s sector list from Django.
* [OSDEV-962](https://opensupplyhub.atlassian.net/browse/OSDEV-962) Update Release protocol. The Release protocol has been updated after the automatization of manual processes such as creating a release branch, restoring DB, deploy to AWS.
* [OSDEV-972](https://opensupplyhub.atlassian.net/browse/OSDEV-972) Reporting. Updating "Facility Uploads" report. Joined one table from two reports and added columns.New table with such columns:
`month`, `Total # of list uploads` in a given month (these are uploads that come from external contributors, NOT OS Hub team members), `# of public list uploads` in a given month (these are uploads that come from OS Hub team members AND have “[Public List]” in the contributor name), `Total facility listItems` uploaded in a given month, `# of Facilities` from Public Lists, `Total Facilities w/ status = new facility`, `# Public List Facilities w/ status = new facility`. Data is ordered from most recent to oldest
* [OSDEV-913](https://opensupplyhub.atlassian.net/browse/OSDEV-913) Claim. Updated the submitted claim auto-reply message for email template.
* [OSDEV-914](https://opensupplyhub.atlassian.net/browse/OSDEV-914) Claim. Updated the approved claim auto-reply message for email template

### Release instructions:
* Update code.


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
