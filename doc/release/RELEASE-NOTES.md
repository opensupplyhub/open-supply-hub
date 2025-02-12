# Release Notes
All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html). The format is based on the `RELEASE-NOTES-TEMPLATE.md` file.

## Release 2.0.0

## Introduction
* Product name: Open Supply Hub
* Release date: February 22, 2025

### Database changes
* [OSDEV-1662](https://opensupplyhub.atlassian.net/browse/OSDEV-1662) - Added a new field, `action_perform_by`, to the `api_moderationevent` table so we can handle and store moderation actions user data.

#### Migrations:
* 0166_add_moderationevent_action_perform_by.py - This migration added a new field, `action_perform_by`, to the existing table `api_moderationevent`.

#### Schema changes
* *Describe schema changes here.*

### Code/API changes
* [OSDEV-1577](https://opensupplyhub.atlassian.net/browse/OSDEV-1577) - Added geo-bounding box query support to the GET `/api/v1/production-locations/` endpoint. To filter production locations whose geopoints fall within the bounding box, it is necessary to specify valid values for the parameters `geo_bounding_box[top]`, `geo_bounding_box[left]`, `geo_bounding_box[bottom]`, and `geo_bounding_box[right]`. 

    The validation rules are as follows:
    * All coordinates of the geo-boundary box (top, left, bottom, right) must be provided.
    * All values must be integers.
    * The top and bottom coordinates must be between -90 and 90.
    * The left and right coordinates must be between -180 and 180.
    * The top must be greater than the bottom.
    * The right must be greater than the left.
* [OSDEV-1662](https://opensupplyhub.atlassian.net/browse/OSDEV-1662) - Updated Logstash mapping configuration to handle the new `action_perform_by` field for OpenSearch.

### Architecture/Environment changes
* [OSDEV-1515](https://opensupplyhub.atlassian.net/browse/OSDEV-1515) - Removed `rds_allow_major_version_upgrade` and `rds_apply_immediately` from the environment tfvars files (e.g., terraform-production.tfvars) to set them to `false` again, as the default values in `/deployment/terraform/variables.tf` are `false`. This is necessary to prevent unintended PostgreSQL major version upgrades since the target PostgreSQL 16.3 version has been reached. 
* [OSDEV-899](https://opensupplyhub.atlassian.net/browse/OSDEV-899) - With this task, we split the Django container into two components: FE (React) and BE (Django). Requests to the frontend (React) will be processed by the CDN (CloudFront), while requests to the API will be redirected to the Django container. This approach will allow for more efficient use of ECS cluster computing resources and improve frontend performance.

    The following endpoints will be redirected to the Django container:
    * tile/*
    * api/*
    * /api-auth/*
    * /api-token-auth/*
    * /api-feature-flags/*
    * /web/environment.js
    * /admin/*
    * /health-check/*
    * /rest-auth/*
    * /user-login/*
    * /user-logout/*
    * /user-signup/*
    * /user-profile/*
    * /user-api-info/*
    * /admin
    * /static/admin/*
    * /static/django_extensions/*
    * /static/drf-yasg/*
    * /static/gis/*
    * /static/rest_framework/*
    * /static/static/*
    * /static/staticfiles.json

    All other traffic will be redirected to the React application.

### Bugfix
* [OSDEV-1695](https://opensupplyhub.atlassian.net/browse/OSDEV-1695) - [SLC] Enabled the claim button for updated production locations when a moderation event has a pending status. Disabled claim button explicitly if production location has pending claim status.

### What's new
* [OSDEV-1662](https://opensupplyhub.atlassian.net/browse/OSDEV-1662) - Added a new field, `action_perform_by`, to the moderation event. This data appears on the Contribution Record page when a moderator perform any actions like `APPROVED` or `REJECTED`.

### Release instructions:
* Ensure that the following commands are included in the `post_deployment` command:
    * `migrate`
    * `reindex_database`
* Run `[Release] Deploy` pipeline for the target environment with the flag `Clear the custom OpenSearch indexes and templates` set to true - to update the index mapping for the `moderation-events` index after adding the new field `action_perform_by`. The `production-locations` will also be affected since it will clean all of our custom indexes and templates within the OpenSearch cluster.


## Release 1.29.0

## Introduction
* Product name: Open Supply Hub
* Release date: February 8, 2025

### Database changes
* [OSDEV-1515](https://opensupplyhub.atlassian.net/browse/OSDEV-1515) - Upgraded the PostgreSQL version from 13 to 16 for the database used in local development, DB anonymization, DB restore setup, and environments in the AWS cloud. Additionally, the pg_trgm extension has been upgraded to version 1.6 based on the available extension version for PostgreSQL 16.3 in AWS RDS. For more information, see [Extensions supported for RDS for PostgreSQL 16](https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-extensions.html#postgresql-extensions-16x).
* [OSDEV-1558](https://opensupplyhub.atlassian.net/browse/OSDEV-1558) - Added a new field, `action_type`, to the `api_moderationevent` table so we can handle and store moderation actions.

#### Migrations:
* 0163_refresh_pg_statistic_and_upgrade_postgres_extensions.py - Updated the SQL script within the migration that upgrades the DB extension versions to handle previously failure cases when a higher version is available for upgrade or when the extension is not installed. This is primarily useful for local development or DB resets in the Development environment, where migrations are applied from scratch, one by one. This fix will not negatively affect other environments, as the migration has already been applied and will not be reapplied. Additionally, the changes are backward compatible.
* 0164_refresh_pg_statistic_and_upgrade_postgres_extensions_after_db_upgrade_to_postgres_16.py - This migration refreshes the `pg_statistic` table after the upgrade to PostgreSQL 16 and upgrades the pg_trgm extension to version 1.6. The SQL script within the migration that upgrades the DB extension versions handles previously failure cases where a higher version is available for upgrade or where the extension is not installed.
* 0165_add_moderationevent_action_type.py - This migration added a new field, `action_type`, to the existing table `api_moderationevent`.

### Code/API changes
* [OSDEV-1581](https://opensupplyhub.atlassian.net/browse/OSDEV-1581) - Added support for Geohex grid aggregation to the GET `/api/v1/production-locations/` endpoint. To receive the Geohex grid aggregation list in the response, it is necessary to pass the `aggregation` parameter with a value of `geohex_grid` and optionally specify `geohex_grid_precision` with an integer between 0 and 15. If `geohex_grid_precision` is not defined, the default value of 5 will be used.
* [OSDEV-1558](https://opensupplyhub.atlassian.net/browse/OSDEV-1558) - Updated Logstash mapping configuration to handle the new `action_type` field for OpenSearch.

### Bugfix
* Some of the resources related to the Development AWS environment still have the `stg` prefix, which can be confusing since we also have a Staging environment with the same prefix. To clarify the resource names, including the database instance, the prefix has been updated from `stg` to `dev` for the development environment.

### What's new
* [OSDEV-1374](https://opensupplyhub.atlassian.net/browse/OSDEV-1374) - Implemented integration for the `Search results` page to show results of searching by name and address (`/contribute/production-location/search`):
    - Connected GET `v1/production-locations`.
    - Routing between pages `Production Location Search`,`Search returned no results`, `Production Location Information`, `Search results`, and `I don't see my Location` pop-up is configured.
    - Max result limit set to 100.
* [OSDEV-1365](https://opensupplyhub.atlassian.net/browse/OSDEV-1365) - SLC: Integrate collecting contribution data page.
* [OSDEV-1370](https://opensupplyhub.atlassian.net/browse/OSDEV-1370) - SLC: Connect Backend API submission with "Thank for Submitting" screen
    - Integrated `POST /v1/production-locations/` in `/contribute/production-location/info/` page.
    - Integrated `PATCH /v1/production-locations/` in `/contribute/production-location/{os_id}/info/` page.
    - Production location info page is now rendered using two routes: /contribute/production-location/info/ and /contribute/production-location/{os_id}/info/. First route for creating new production location, second is for updating existing one.
    - Implemented error popup on error response for `PATCH | POST /v1/production-locations/`.
    - Implemented error popup on error response for `GET /v1/moderation-events/{moderation_id}`.
    - Integrated "Thank for Submitting" modal dialog. When popup is appeared, path parameter `{moderation-id}` will be attached to `/contribute/production-location/{os_id}/info/` or `/contribute/production-location/info/`.
    - Implemented temporary saving of moderation events in local storage for a seamless user experience.
    - Created separate mobile and desktop layouts for "Thank for Submitting" modal dialog.
    - Created link to claim from "Thank for Submitting" modal dialog only if production location is available for claim and moderation event is not pending.
    - Implemented serializing and validation production location fields before passing to the "Thank for Submitting" modal dialog.
    - Refactored routing between search results page and production location info page. Search parameters are now stored in the Redux state, so the 'Go Back' button in production location info page will lead to the previous search.
* [OSDEV-1558](https://opensupplyhub.atlassian.net/browse/OSDEV-1558) - Added a new field, `action_type`, to the moderation event. This data appears on the Contribution Record page when a moderator creates a new location or matches it to an existing one.

### Release instructions:
* Ensure that the following commands are included in the `post_deployment` command:
    * `migrate`
    * `reindex_database`
* Run `[Release] Deploy` pipeline for the target environment with the flag `Clear the custom OpenSearch indexes and templates` set to true - to update the index mapping for the `moderation-events` index after adding the new field `action_type`. The `production-locations` will also be affected since it will clean all of our custom indexes and templates within the OpenSearch cluster.
* This release will upgrade PostgreSQL from version 13 to version 16.
    * The upgrade will be performed automatically by Terrafrom and AWS, but some steps need to be completed **before** and **after** the upgrade. Please refer to [the Confluence article](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/640155649/PostgreSQL+database+upgrade+from+version+13+to+version+16) for detailed instructions.
    * Steps to be completed before the upgrade are marked with the statement: "**This should be done before deploying the upgraded database.**". Post-upgrade tasks can be found under the [After the PostgreSQL major version upgrade](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/640155649/PostgreSQL+database+upgrade+from+version+13+to+version+16#After-the-PostgreSQL-major-version-upgrade) section.
    * In case of an unsuccessful release along with the database upgrade, follow the instructions under the [Guide for rolling back the PostgreSQL major version upgrade](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/640155649/PostgreSQL+database+upgrade+from+version+13+to+version+16#Guide-for-rolling-back-the-PostgreSQL-major-version-upgrade) section.


## Release 1.28.1

## Introduction
* Product name: Open Supply Hub
* Release date: January 31, 2025

### Bugfix
* [OSDEV-1626](https://opensupplyhub.atlassian.net/browse/OSDEV-1626) - Temporarily hid the new contribution page `Add Location Data` and re-enabled the old navigation to the `List Upload` page via the `/contribute` path.


## Release 1.28.0

## Introduction
* Product name: Open Supply Hub
* Release date: January 25, 2025

### Database changes
* [OSDEV-1514](https://opensupplyhub.atlassian.net/browse/OSDEV-1514) - Upgraded the PostgreSQL version from 12 to 13 for the database used in local development, DB anonymization, DB restore setup, and environments in the AWS cloud. Additionally, the postgis and pg_trgm extensions have been upgraded to versions 3.4.2 and 1.5, respectively, based on the available extension versions for PostgreSQL 13.15 in AWS RDS. For more information, see [Extensions supported for RDS for PostgreSQL 13](https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-extensions.html#postgresql-extensions-13x). Allowed major version upgrades and activated the `apply immediately` flag to perform the PostgreSQL major version upgrade in AWS.

#### Migrations:
* 0163_refresh_pg_statistic_and_upgrade_postgres_extensions.py - This migration refreshes the `pg_statistic` table after the upgrade to PostgreSQL 13 and upgrades the postgis and pg_trgm extensions to versions 3.4.2 and 1.5, respectively.

### Code/API changes
* [OSDEV-1514](https://opensupplyhub.atlassian.net/browse/OSDEV-1514) - Corrected spelling mistakes in the `src/anon-tools/do_dump.sh` file and in the name of the folder `database_anonymizer_sheduled_task`. Removed the unused `src/anon-tools/anon.sql` file and the redundant `src/anon-tools/initdb.sql` file. Removed commented-out code in the `src/anon-tools/Dockerfile.dump` and `deployment/terraform/database_anonymizer_scheduled_task/docker/database_anonymizer.py` files.
* [OSDEV-1523](https://opensupplyhub.atlassian.net/browse/OSDEV-1523) - Updated `export_csv.py` to enable uploading to Google Drive and implemented cursor-based pagination for the export.

### Architecture/Environment changes
* [OSDEV-1514](https://opensupplyhub.atlassian.net/browse/OSDEV-1514) - Introduced `rds_allow_major_version_upgrade` and `rds_apply_immediately` Terraform variables to enable or disable major version upgrades and the `apply immediately` flag, depending on the environment.
* [OSDEV-1523](https://opensupplyhub.atlassian.net/browse/OSDEV-1523) - Added a new batch job that triggers the export_csv.py command on the first day of each month to upload bulk data of production locations to Google Drive.

### What's new
* [OSDEV-40](https://opensupplyhub.atlassian.net/browse/OSDEV-40) - Created new page for `/contribute` to choose between multiple & single location upload. Replaced current multiple list upload to `/contribute/multiple-locations`. Changed `Upload Data` to `Add Data` text.
* [OSDEV-1117](https://opensupplyhub.atlassian.net/browse/OSDEV-1117) - Implemented integration of Contribution Record Page (`/dashboard/moderation-queue/contribution-record/{moderation_id}`):
    - Connected GET `api/v1/moderation-events/{moderation_id}/`.
    - Connected GET `api/v1/production-locations?name={productionLocationName}&country={countryCode}&address={address}` to get potential matches using OpenSearch engine.
    - Connected PATCH `/v1/moderation-events/{moderation_id}/` (for Reject button).
    - Connected POST `/v1/moderation-events/{moderation_id}/production-locations/` (for Create New Location button).
    - Connected PATCH `/v1/moderation-events/{moderation_id}/production-locations/{os_id}/` (for Confirm potential match button).
    - UI improvements:
        - Added a toast component to display notifications during moderation event updates.
        - Introduced a backdrop to prevent accidental clicks on other buttons during the update process.
    - Applied Django Signal for moderation-events OpenSearch index.
* [OSDEV-1524](https://opensupplyhub.atlassian.net/browse/OSDEV-1524) - Updated salutations in automated emails to ensure a consistent and professional experience of communication from OS Hub.
* [OSDEV-1129](https://opensupplyhub.atlassian.net/browse/OSDEV-1129) - The UI for the results page for name and address search was implemented. It includes the following screens:
    * Successful Search: If the search is successful, the results screen displays a list of production locations. Each item includes the following information about the production location: name, OS ID, address, and country name. Users can either select a specific production location or press the "I don’t see my Location" button, which triggers a confirmation dialog window.
    * Confirmation Dialog Window: In this window, users can confirm that no correct location was found using the provided search parameters. They can either proceed to create a new production location or return to the search.
    * Unsuccessful Search: If the search is unsuccessful, an explanation is provided along with two options: return to the search or add a new production location.
* [OSDEV-1579](https://opensupplyhub.atlassian.net/browse/OSDEV-1579) - Updated the API limit automated email to remove an outdated link referring to OAR and improve the languate for clarity. With this update the contributor will be informed of the correct process to follow if they have reached their API calls limit.

### Release instructions:
* Ensure that the following commands are included in the `post_deployment` command:
    * `migrate`
    * `reindex_database`
* This release will upgrade PostgreSQL from version 12 to version 13.
    * The upgrade will be performed automatically by Terrafrom and AWS, but some steps need to be completed **before** and **after** the upgrade. Please refer to [the Confluence article](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/620134402/PostgreSQL+database+upgrade+from+version+12+to+version+13) for detailed instructions.
    * Steps to be completed before the upgrade are marked with the statement: "**This should be done before deploying the upgraded database.**". Post-upgrade tasks can be found under the [After the PostgreSQL major version upgrade](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/620134402/PostgreSQL+database+upgrade+from+version+12+to+version+13#After-the-PostgreSQL-major-version-upgrade) section.
    * In case of an unsuccessful release along with the database upgrade, follow the instructions under the [Guide for rolling back the PostgreSQL major version upgrade](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/620134402/PostgreSQL+database+upgrade+from+version+12+to+version+13#Guide-for-rolling-back-the-PostgreSQL-major-version-upgrade) section.


## Release 1.27.0

## Introduction
* Product name: Open Supply Hub
* Release date: January 11, 2025

### Database changes
#### Migrations:

#### Schema changes

### Code/API changes
* [OSDEV-1409](https://opensupplyhub.atlassian.net/browse/OSDEV-1409) - Introduced a new PATCH `/api/v1/moderation-events/{moderation_id}/production-locations/{os_id}/` endpoint. This endpoint allows the creation of a new contribution for an existing production location based on the provided moderation event.
* [OSDEV-1336](https://opensupplyhub.atlassian.net/browse/OSDEV-1336) - Introduced a new PATCH `/api/v1/production-locations/{os_id}/` endpoint based on the API v1 specification. This endpoint allows the creation of a new moderation event for updating the production location with the given details. Basically, the endpoint can be used to contribute to an existing location.
* [OSDEV-1336](https://opensupplyhub.atlassian.net/browse/OSDEV-1336) - Dynamic mapping for the new fields in the `moderation-events` index has been disabled for those that don't have an explicit mapping defined. This change helps avoid indexing conflicts, such as when a field is initially indexed with one data type (e.g., long), but later an entry with a different data type for the same field is indexed, causing the entire entry to fail indexing. After this change, fields with an explicit mapping will be indexed, while other fields will not be indexed or searchable, but will still be displayed in the document.

### Architecture/Environment changes

### Bugfix
* [OSDEV-1492](https://opensupplyhub.atlassian.net/browse/OSDEV-1492) - Fixed an issue where invalid manually entered dates were not validated on the UI, resulting in API errors with message “The request query is invalid.” on `Moderation Queue` page. Invalid dates are now trimmed and properly handled.
* [OSDEV-1493](https://opensupplyhub.atlassian.net/browse/OSDEV-1493) - Fixed an issue where the backend sorts countries not by `name` but by their `alpha-2 codes` in `GET /api/v1/moderation-events/` endpoint.
* [OSDEV-1532](https://opensupplyhub.atlassian.net/browse/OSDEV-1532) - Fixed the date range picker on the `Moderation Queue` page. A Data Moderator can change the Before date even if an Error message is displayed.
* [OSDEV-1533](https://opensupplyhub.atlassian.net/browse/OSDEV-1533) - The presentation of the `Moderation Decision Date` in the `Moderation Queue` table has been corrected. If the "status_change_date" is missing in the object, it now displays as "N/A".
* [OSDEV-1196](https://opensupplyhub.atlassian.net/browse/OSDEV-1196) - The `?sort_by=contributors_desc` query parameter is only appended to URLs on the `/facilities` page and is excluded from all other pages. The error caused by the property type that occurred during local test execution has been resolved.
* [OSDEV-1397](https://opensupplyhub.atlassian.net/browse/OSDEV-1397) - GET `/api/parent-companies/` request has been removed from the Open Supply Hub page and ClaimFacility component. Parent Company Select is a regular input field that allows the creation of multiple parent company names for filter on this page.
* [OSDEV-1556](https://opensupplyhub.atlassian.net/browse/OSDEV-1556) - Fixed validation of `os_id` for PATCH `/api/v1/moderation-events/{moderation_id}/production-locations/{os_id}/` endpoint.
* [OSDEV-1563](https://opensupplyhub.atlassian.net/browse/OSDEV-1563) - Fixed updating of the moderation decision date after moderation event approval.

### What's new
* [OSDEV-1376](https://opensupplyhub.atlassian.net/browse/OSDEV-1376) - Updated automated emails for closure reports (report_result) to remove the term "Rejected" for an improved user experience. Added link to Closure Policy and instructions for submitting a Reopening Report to make the process easier to understand for users.
* [OSDEV-1383](https://opensupplyhub.atlassian.net/browse/OSDEV-1383) - Edited text of the automated email that notifies a contributor when one of their facilities has been claimed. The new text provides more information to the contributor to understand the claim process and how they can encourage more of their facilities to claim their profile.
* [OSDEV-1474](https://opensupplyhub.atlassian.net/browse/OSDEV-1474) - Added contributor type value to response of `/api/contributors/` endpoint.
* [OSDEV-1130](https://opensupplyhub.atlassian.net/browse/OSDEV-1130) A new page, `Production Location Information`, has been implemented. It includes the following inputs:
    * Required and pre-fillable fields:
        - Name
        - Address
        - Country
    * Additional information section: Fields for optional contributions from the owner or manager of the production location, including sector(s), product type(s), location type(s), processing type(s), number of workers, and parent company.
The page also features `Go Back` and `Submit` buttons for navigation and form submission.

### Release instructions:
* Ensure that the following commands are included in the `post_deployment` command:
    * `migrate`
    * `reindex_database`
* Run `[Release] Deploy` pipeline for the target environment with the flag `Clear the custom OpenSearch indexes and templates` set to true - to refresh the index mappings for the `moderation-events` index after disabling dynamic mapping for the new fields that don't have an explicit mapping defined. The `production-locations` will also be affected since it will clean all of our custom indexes and templates within the OpenSearch cluster


## Release 1.26.0

## Introduction
* Product name: Open Supply Hub
* Release date: December 14, 2024

### Database changes
#### Migrations:
* 0162_update_moderationevent_table_fields.py - This migration updates the ModerationEvent table and its constraints.

#### Schema changes
* [OSDEV-1158](https://opensupplyhub.atlassian.net/browse/OSDEV-1158) - The following updates to the ModerationEvent table have been made:
    1. Set `uuid` as the primary key.
    2. Make `geocode_result` field optional. It can be blank if lat and lng
    have been provided by user.
    3. Remove redundant `blank=False` and `null=False` constraints, as these are
    the default values for model fields in Django and do not need to be
    explicitly set.
    4. Make `contributor` field non-nullable, as the field should not be left
    empty. It is required to have information about the contributor.
    5. Allow `claim` field to be blank. This change reflects the fact that
    a moderation event may not always be related to a claim, so the field can
    be left empty.

### Code/API changes
* [OSDEV-1453](https://opensupplyhub.atlassian.net/browse/OSDEV-1453) - The `detail` keyword instead of `message` has been applied in error response objects for V1 endpoints.
* [OSDEV-1346](https://opensupplyhub.atlassian.net/browse/OSDEV-1346) - Disabled null values from the response of the OpenSearch. Disabled possible null `os_id`, `claim_id` and `source` from `PATCH /api/v1/moderation-events/{moderation_id}/` response.
* [OSDEV-1410](https://opensupplyhub.atlassian.net/browse/OSDEV-1410) - Introduced a new POST `/api/v1/moderation-events/{moderation_id}/production-locations/` endpoint
* [OSDEV-1449](https://opensupplyhub.atlassian.net/browse/OSDEV-1449) - **Breaking changes** to the following endpoints:
  - GET `v1/moderation-events/`
  - GET `v1/production-locations/`

  **Changes include:**
  - Refactored `sort_by` parameter to improve sorting functionality.
  - Split `search_after` parameter into `search_after_value` and `search_after_id` for better pagination control.

* [OSDEV-1158](https://opensupplyhub.atlassian.net/browse/OSDEV-1158) - The following features and improvements have been made:
    1. Introduced a new POST `/api/v1/production-locations/` endpoint based on the API v1 specification. This endpoint allows the creation of a new moderation event for the production location creation with the given details.
    2. Removed redundant redefinition of paths via the `as_view` method for all the v1 API endpoints since they are already defined via `DefaultRouter`.
* [OSDEV-1468](https://opensupplyhub.atlassian.net/browse/OSDEV-1468) - Limit the `page` parameter to `100` for the GET `/api/facilities/` endpoint. This will help prevent system downtimes, as larger pages (OFFSET) make it harder for the database to retrieve data, especially considering the large amount of data we have.

### Architecture/Environment changes
* [OSDEV-1170](https://opensupplyhub.atlassian.net/browse/OSDEV-1170) - Added the ability to automatically create a dump from the latest shared snapshot of the anonymized database from Production environment for use in the Test and Pre-Prod environments.
* In light of recent instances(on 12/03/2024 UTC and 12/04/2024 UTC) where the current RDS disk storage space limit was reached in Production, the RDS storage size has been increased to `256 GB` in the Production, Test, and Pre-prod environments to accommodate the processing of larger volumes of data. The configurations for the Test and Pre-prod environments have also been updated to maintain parity with the Production environment.
* Right-sized the resources for Django containers across all environments and the RDS instance in the Production and Preprod environments. This will result in a savings of approximately $2,481. The following changes have been made:
    - Production:
        - RDS instance type was changed from `db.m6in.8xlarge` to `db.m6in.4xlarge`.
        - ECS tasks for Django containers: the number was reduced from `12` to `10`, and memory was reduced from `8GB` to `4GB`.
    - Preprod:
        - RDS instance type was changed from `db.m6in.8xlarge` to `db.m6in.4xlarge`.
        - ECS tasks for Django containers: the number was reduced from `12` to `10`, and memory was reduced from `8GB` to `4GB`.
        - These changes were made to maintain parity with the Production environment, as it is a copy of that environment.
    - Staging:
        - ECS tasks for Django containers: memory was reduced from `8GB` to `2GB`.
    - Test:
        - ECS tasks for Django containers: memory was reduced from `8GB` to `4GB`.
    - Development:
        - ECS tasks for Django containers: memory was reduced from `8GB` to `1GB`, and CPU was reduced from `1 vCPU` to `0.5 vCPU`.

### Bugfix
* [OSDEV-1388](https://opensupplyhub.atlassian.net/browse/OSDEV-1388) - The waiter from boto3 cannot wait more than half an hour so we replaced it with our own.
* It was found that clearing OpenSearch indexes didn’t work properly because the templates weren’t cleared. After updating the index mappings within the index template files, the index template remained unchanged because only the indexes were deleted during deployment, not both the indexes and their templates. This caused conflicts and prevented developers' updates from being applied to the OpenSearch indexes.
This issue has been fixed by adding additional requests to delete the appropriate index templates to the `clear_opensearch.sh.tpl` script, which is triggered when clearing OpenSearch during deployment to any environment.
* [OSDEV-1482](https://opensupplyhub.atlassian.net/browse/OSDEV-1482) - The `GET api/v1/moderation-events/{moderation_id}` endpoint returns a single response instead of an array containing one item.
* [OSDEV-1511](https://opensupplyhub.atlassian.net/browse/OSDEV-1511) - Updated google maps api version to 3.57 for ReactLeafletGoogleLayer component (3.51 not supported).

### What's new
* [OSDEV-1132](https://opensupplyhub.atlassian.net/browse/OSDEV-1132) - Added FE for the "thanks for submitting" screen when user submits production location's data.
* [OSDEV-1373](https://opensupplyhub.atlassian.net/browse/OSDEV-1373) - The tab `Search by Name and Address.` on the Production Location Search screen has been implemented. There are three required properties (name, address, country). The "Search" button becomes clickable after filling out inputs, creates a link with parameters, and allows users to proceed to the results screen.
* [OSDEV-1175](https://opensupplyhub.atlassian.net/browse/OSDEV-1175) - New Moderation Queue Page was integrated with `GET api/v1/moderation-events/` endpoint that include pagination, sorting and filtering.

### Release instructions:
* Ensure that the following commands are included in the `post_deployment` command:
    * `migrate`
    * `reindex_database`
* Run `[Release] Deploy` pipeline for the target environment with the flag `Clear the custom OpenSearch indexes and templates` set to true - to refresh the index mappings for the `production-locations` and `moderation-events` indexes after fixing the process of clearing the custom OpenSearch indexes. It will clean all of our custom indexes and templates within the OpenSearch cluster.


## Release 1.25.0

## Introduction
* Product name: Open Supply Hub
* Release date: November 30, 2024

### Database changes
#### Migrations:
* 0159_alter_status_of_moderation_events_table.py - This migration alters status of api_moderationevent table.
* 0160_allow_null_parsing_errors_in_facilitylist.py - This migration allows empty parsing_errors in api_facilitylist.
* 0161_create_disable_list_uploading_switch.py - This migration creates disable_list_uploading switch in the Django admin panel and record in the waffle_switch table.

#### Schema changes
* [OSDEV-1346](https://opensupplyhub.atlassian.net/browse/OSDEV-1346) - Alter status options for api_moderationevent table.
* [OSDEV-1411](https://opensupplyhub.atlassian.net/browse/OSDEV-1411) - Allows empty parsing_errors in api_facilitylist.

### Code/API changes
* [OSDEV-1346](https://opensupplyhub.atlassian.net/browse/OSDEV-1346) - Create GET request for `v1/moderation-events` endpoint.
* [OSDEV-1429](https://opensupplyhub.atlassian.net/browse/OSDEV-1429) - The list upload switcher has been created to disable the `Submit` button on the List Contribute page through the Switch page in the Django admin panel during the release process. Implemented a check on the list upload endpoint.
* [OSDEV-1332](https://opensupplyhub.atlassian.net/browse/OSDEV-1332) - Introduced new `PATCH api/v1/moderation-events/{moderation_id}` endpoint
to modify moderation event `status`.
* [OSDEV-1347](https://opensupplyhub.atlassian.net/browse/OSDEV-1347) - Create GET request for `v1/moderation-events/{moderation_id}` endpoint.
* Update `/v1/production-locations/{os_id}` endpoint to return a single object instead of multiple objects. Also, add unit tests for the `ProductionLocationsViewSet`.
* The RDS instance has been upgraded as follows: for `production` and `preprod`, it is now `db.m6in.8xlarge`, and for `test`, it has been upgraded to `db.t3.xlarge`.
* [OSDEV-1467](https://opensupplyhub.atlassian.net/browse/OSDEV-1467) - Implemented disabling endpoint `POST /api/facilities/` during the release process. It is raising an error message with status code 503.

### Architecture/Environment changes
* Increased the memory for the Dedupe Hub instance from 8GB to 12GB in the `production` and `pre-prod` environments to reduce the risk of container overload and minimize the need for reindexing in the future.

### Bugfix
* [OSDEV-1448](https://opensupplyhub.atlassian.net/browse/OSDEV-1448) - The map on the production location’s profile and the production location marker have been fixed. Improved the handling of SQL query parameters for better execution accuracy.
* [OSDEV-1411](https://opensupplyhub.atlassian.net/browse/OSDEV-1411) - Django Admin: Fixed an issue when updating the facility list with an empty array in the `parsing errors` field.

### Release instructions:
* Ensure that the following commands are included in the `post_deployment` command:
    * `migrate`
    * `reindex_database`


## Release 1.24.0

## Introduction
* Product name: Open Supply Hub
* Release date: November 16, 2024

### Code/API changes
* [OSDEV-1335](https://opensupplyhub.atlassian.net/browse/OSDEV-1335) - Explicitly set the number of shards and the number of replicas for the "production locations" and "moderation events" OpenSearch indexes. Based on the OpenSearch documentation, a storage size of 10–30 GB is preferred for workloads that prioritize low search latency. Additionally, having too many small shards can unnecessarily exhaust memory by storing excessive metadata. Currently, the "production locations" index utilizes 651.9 MB, including replicas, while the "moderation events" index is empty. This indicates that one shard and one replica should be sufficient for the "production locations" and "moderation events" indexes.
* Moved all the files related to the OpenSearch service to the existing `src/django/api/services/opensearch` folder within the `api` app of the Django application. This should make it easier to navigate through the files and clarify the location of all OpenSearch service-related files in one place within the `api` app in Django.

### Architecture/Environment changes
* The OpenSearch version has been increased to 2.15.
* [OSDEV-1335](https://opensupplyhub.atlassian.net/browse/OSDEV-1335) - The new "moderation events" Logstash pipeline has been configured and implemented to collect moderation event data from the current PostgreSQL database and save it to OpenSearch. This setup allows for fast searches on the moderation events data.
* [OSDEV-1387](https://opensupplyhub.atlassian.net/browse/OSDEV-1387) - The SQL query for generating tiles from PostgreSQL+PostGIS has been reimplemented to avoid using the JOIN + GROUP BY clause. This change reduces the number of subqueries and their asymptotic complexity. Additionally, an option to set an upper limit on facility counts in the 'count' clause has been introduced, capped at 100, which doubles the query's performance. Throttling has been removed for tile generation endpoints.
* [OSDEV-1171](https://opensupplyhub.atlassian.net/browse/OSDEV-1171) - RDS instances for `staging` and `test` have beed decreased to `db.t3.large`
* Playwright has been introduced as the main framework for end-to-end testing:
    * Added a new Playwright testing service to the Docker configuration
    * Implemented initial test cases to verify core functionality
    * Integrated Playwright tests into the CI pipeline via GitHub Actions
    * Added necessary configuration files and dependencies for the e2e testing project
* The RDS instance for `production` has been upgraded to `db.m6in.4xlarge` and configured to operate in a single Availability Zone.

### Bugfix
* [OSDEV-1335](https://opensupplyhub.atlassian.net/browse/OSDEV-1335) - Fixed the assertion in the test for the `country.rb` filter of the "production locations" Logstash pipeline. The main issue was with the evaluation of statements in the Ruby block. Since only the last statement is evaluated in a Ruby block, all the checks were grouped into one chain of logical statements and returned as a `result` variable at the end.

### What's new
* [OSDEV-1116](https://opensupplyhub.atlassian.net/browse/OSDEV-1116) - A new Contribution Record Page has been developed to enable quick identification and moderation of contributions. This page includes two main sections: Moderation Event Data and Potential Matches, along with a set of buttons designed to facilitate the moderation process.
* [OSDEV-1120](https://opensupplyhub.atlassian.net/browse/OSDEV-1120) - A new Moderation Queue Dashboard page has been introduced, featuring three essential components:
    * Moderation Events Table: Allows users to view and manage moderation events more effectively.
    * Filtering Options: Multiple filter fields enable users to customize the displayed events based on different criteria, making it easier to find specific events.
    * Download Excel Button: Provides the ability to export the list of displayed moderation events as an XLSX file for offline analysis and record-keeping.

### Release instructions:
* The following steps should be completed while deploying to Staging or Production:
    1. Run the `[Release] Deploy` pipeline for these environments with the flag 'Clear OpenSearch indexes' set to true. This will allow Logstash to refill OpenSearch since the OpenSearch instance will be recreated due to the version increase. It is also necessary due to changes in the OpenSearch index settings.
    2. Open the triggered `Deploy to AWS` workflow and ensure that the `apply` job is completed. **Right after** finishing the `apply` job, follow these instructions, which should be the last steps in setting up the recreated OpenSearch instance:
        - Copy the ARN of the `terraform_ci` user from the AWS IAM console.
            - Navigate to the AWS console's search input, type "IAM", and open the IAM console.
            - In the IAM console, find and click on the "Users" tab.
            - In the list of available users, locate the `terraform_ci` user, click on it, and on that page, you will find its ARN.
        - After copying this value, go to the AWS OpenSearch console in the same way you accessed the IAM console.
        - Open the available domains and locate the domain for the corresponding environment. Open it, then navigate to the security configuration and click "Edit".
        - Find the section titled "Fine-grained access control", and under this section, you will find an "IAM ARN" input field. Paste the copied ARN into this field and save the changes. It may take several minutes to apply. Make sure that the "Configuration change status" field has green status.
    3. Then, return to the running `Deploy to AWS` workflow and ensure that the logs for `clear_opensearch` job do not contain errors related to access for deleting the OpenSearch index or lock files in EFS storage. In case of **an access error**, simply rerun the `Deploy to AWS` workflow manually from the appropriate release Git tag.


## Release 1.23.0

## Introduction
* Product name: Open Supply Hub
* Release date: November 02, 2024

### Database changes
#### Migrations:
* 0158_create_moderation_events_table.py - This migration creates api_moderationevent table for Moderation Queue.

#### Schema changes
* [OSDEV-1229](https://opensupplyhub.atlassian.net/browse/OSDEV-1229) - Created Moderation Events Postgres table to track moderation events in the database.

### Code/API changes
* Throttling has been introduced for tiles/* endpoints, limiting requests to 300 per minute.
* [OSDEV-1328](https://opensupplyhub.atlassian.net/browse/OSDEV-1328) The OpenSearch tokenizer has been changed to `lowercase` to get better search results when querying the GET /v1/production-locations/ endpoint.

### Architecture/Environment changes
* Resource allocation has been optimized for the staging environment. The number of ECS tasks for the Django app has been reduced from 6 to 4, while maintaining system stability.

### Release instructions:
* Ensure that the following commands are included in the `post_deployment` command:
    * `migrate`
* Run `[Release] Deploy` pipeline for an existing environment with the flag 'Clear OpenSearch indexes' set to true - to let the tokenizer parse full text into words with new configurations.


## Release 1.22.0

## Introduction
* Product name: Open Supply Hub
* Release date: October 19, 2024

### Database changes
#### Migrations:
* 0156_introduce_list_level_parsing_errors - This migration introduces the parsing_errors field for the FacilityList model to collect list-level and internal errors logged during the background parsing of the list.
* 0157_delete_endpoint_switcher_for_list_uploads - This migration deletes the `use_old_upload_list_endpoint` switcher that was necessary to toggle between the old and new list upload endpoints.

#### Schema changes
* [OSDEV-1039](https://opensupplyhub.atlassian.net/browse/OSDEV-1039) - Since the `use_old_upload_list_endpoint` switcher is no longer necessary for the list upload, it has been deleted from the DB. Additionally, the `parsing_errors` field has been added to the FacilityList model.

### Code/API changes
* [OSDEV-1102](https://opensupplyhub.atlassian.net/browse/OSDEV-1102) - API. Propagate production location updates to OpenSearch data source via refreshing `updated_at` field in `api_facility` table. Triggered updated_at field in such actions: transfer to alternate facility, claim facility, approve, reject and deny claim, claim details, merge facilities, match facility (promote, split).
* [OSDEV-1039](https://opensupplyhub.atlassian.net/browse/OSDEV-1039) - Deleted the `facility_list_items.json` fixture from the Django app since it is no longer needed, having been replaced with real CSV files. Additionally, other important changes have been implemented in the Django app and deployment:
    * Adjusted all code that used the `facility_list_items.json` fixture and removed the unused matching logic from the Django app, as it is no longer necessary and was connected to that fixture.
    * Updated the reset database step in the `restore_database` job of the Deploy to AWS GitHub workflow to upload CSV location list files to S3 for parsing during the DB reset.

### Architecture/Environment changes
* [OSDEV-1325](https://opensupplyhub.atlassian.net/browse/OSDEV-1325)
  * __Deploy to AWS__ pipeline will init from __[Release] Deploy__ pipeline and get deployment parameters, such as cleaning OpenSearch indexes, by trigger.
* [OSDEV-1372](https://opensupplyhub.atlassian.net/browse/OSDEV-1372)
  * Changed the base image in the Django app Dockerfile to use a Debian 11 instead of Debian 10 as the PostgreSQL 13 repository support for Debian 10 has been ended.
  * Always build a docker image for the amd64 platform so that the image in the local environment fully corresponds to the one in production.
* [OSDEV-1172](https://opensupplyhub.atlassian.net/browse/OSDEV-1172)
  * Added the ability to restore a database from a snapshot.
* [OSDEV-1388](https://opensupplyhub.atlassian.net/browse/OSDEV-1388)
  * Increased timeout to wait for copying anonymized shared snapshot.

### Bugfix
* Fixed a bug related to environment variable management:
    * Removed the `py_environment` Terraform variable, as it appeared to be a duplicate of the `environment` variable.
    * Passed the correct environment values to the ECS task definition for the Django containers in all environments, especially in the Preprod and Development environments, to avoid misunderstandings and incorrect interpretations of the values previously passed via `py_environment`.
    * Introduced a *Local* environment specifically for local development to avoid duplicating variable values with the AWS-hosted *Development* environment.
* [OSDEV-1039](https://opensupplyhub.atlassian.net/browse/OSDEV-1039) - Made the list parsing asynchronous and increased the list upload limit to 10,000 facilities per list to reduce manual work for moderators when they split large lists into smaller ones. The following architectural and code changes have been made:
    1. Renamed the previously copied `api/facility-lists/createlist` POST endpoint to the `api/facility-lists` POST endpoint. Deleted the old implementation of the `api/facility-lists` POST endpoint along with the `use_old_upload_list_endpoint` switcher that was necessary to toggle between the old and new list upload endpoints.
    2. Removed the triggering of ContriCleaner from the `api/facility-lists` POST endpoint and moved it to the async parse AWS batch job to reduce the load on the endpoint. Introduced a `parsing_errors` field for the FacilityList model to collect list-level and internal errors logged during the background parsing of the list.
    3. Established a connection between the EC2 instance within the AWS batch job and the S3 bucket where all the uploaded list files are saved. This is necessary because the parse job retrieves a particular list from the S3 bucket via Django.
    4. Deleted redundant code from the previous implementation of the list item parsing.
    5. Adjusted Django, ContriCleaner, and integration tests. Regarding integration tests, the `facility_list_items.json` fixture was converted to concrete CSV lists, which were connected to the `facility_lists.json` fixture to upload them to the DB while creating the test DB for the integration tests. This is necessary because the parsing function that triggers ContriCleaner can only work with real files, not facility list items as it did previously.
    6. Refactored the ContributeForm component in the front-end app.
    7. The list page has been adjusted to work with asynchronous parsing, and a new dialog window has been added to notify users about the list parsing process, indicating that they need to wait.
    8. Introduced a UI to display list parsing errors on the list page after the page refresh.

### What's new
* [OSDEV-1127](https://opensupplyhub.atlassian.net/browse/OSDEV-1127) - It was implemented the Production Location Search screen that has two tabs: "Search by OS ID" and "Search by Name and Address." Each tab adds a query parameter (`?tab=os-id` and `?tab=name-address`) to the URL when active, allowing for redirection to the selected tab. On the "Search by OS ID" tab, users see an input field where they can enter an OS ID. After entering the full OS ID (15 characters), the "Search By ID" button becomes clickable, allowing users to proceed to the results screen. There are two possible outcomes:
    * Successful Search: If the search is successful, the results screen displays information about the production location, including its name, OS ID, previous OS ID (If they exist), address, and country name. Users can then choose to either return to the search by name and address or add data and claim the location.
    * Unsuccessful Search: If the search is unsuccessful, an explanation is provided, along with two options: return to the search by name and address or search for another OS ID.

    Each results screen also includes a "Back to ID search" button at the top.

### Release instructions:
* Before deploying to an existing environment, clear OpenSearch to ensure it can receive any missed changes and properly start the update process.
* Ensure that the `migrate` command is included in the `post_deployment` command.


## Release 1.21.0

## Introduction
* Product name: Open Supply Hub
* Release date: September 21, 2024

### Code/API changes
* [OSDEV-1126](https://opensupplyhub.atlassian.net/browse/OSDEV-1126) - Added the `historical_os_id` field to the response from the `v1/production-locations` endpoint if the searched production location contains this data. Modified the search query for `os_id` so that the search is conducted in both the `os_id` and `historical_os_id` fields in the OpenSearch production-locations index.
To make this possible, the `sync_production_locations.sql` script, which generates data for the production-locations index, was modified to include the selection of `historical_os_id_value` from the `api_facilityalias` table.
Additionally, a `historical_os_id` filter was added to the `sync_production_locations.conf`, ensuring that the `historical_os_id` is included in the index document only when the `historical_os_id_value` is not empty.

### Architecture/Environment changes
* [OSDEV-1177](https://opensupplyhub.atlassian.net/browse/OSDEV-1177)
  * Improved OpenSearch indexes cleanup step in the `Deploy to AWS` and `DB - Apply Anonymized DB` pipelines to use script templates so that changes can be made in one place rather than in each pipeline separately
  * Stop/start Logstash and clearing OpenSearch indexes moved to separate jobs of `Deploy to AWS` and `DB - Apply Anonymized DB` pipelines.
  * Stop/start Logstash and clearing OpenSearch indexes now runs on ubuntu-latest runner.
  * The automated deployment to AWS after creating tags for `sandbox` and `production` was temporarily prevented (until the implementation of [OSDEV-1325](https://opensupplyhub.atlassian.net/browse/OSDEV-1325)).

### Bugfix
* [OSDEV-1177](https://opensupplyhub.atlassian.net/browse/OSDEV-1177) - The following changes have been made:
    * Removed the if clause in the DB. Apply the Anonymized DB workflow to activate stopping Logstash.
    * Corrected grammar mistakes in the description of the job steps for stopping Logstash and clearing OpenSearch for the `DB - Apply Anonymized DB` and `Deploy to AWS` GitHub workflows.

### What's new
* [OSDEV-1225](https://opensupplyhub.atlassian.net/browse/OSDEV-1225) - The auto email responses for `Approved` and `Rejected` statuses have been updated to improve user experience. A user receives an email updating them on the status of their list and the next steps they need to take.

### Release instructions:
* Ensure that the following commands are included in the `post_deployment` command:
    * `migrate`
* After running the `Release [Deploy]` workflow for both the `sandbox` and `production` environments, the responsible person must manually run the `Deploy to AWS` workflow, ensuring that the `Clear OpenSearch indexes` option is checked for each environment.
Note: This instruction updates item 3 of the ['Release to Production and Sandbox'](https://github.com/opensupplyhub/open-supply-hub/blob/main/doc/release/RELEASE-PROTOCOL.md#release-to-production-and-sandbox) section of the RELEASE-PROTOCOL.


## Release 1.20.0

## Introduction
* Product name: Open Supply Hub
* Release date: September 7, 2024

### Database changes
#### Migrations:
* 0155_remove_verification_method_column_from_facility_claim - This migration replaces the old `index_approved_claim` function with a new one that does not index the `verification_method` and `phone_number` fields. Additionally, it removes the `verification_method` and `phone_number` fields from the FacilityClaim model and the respective history table.

#### Schema changes
* [OSDEV-1092](https://opensupplyhub.atlassian.net/browse/OSDEV-1092) - Since the `verification_method` and `phone_number` fields are no longer necessary for the claim form and aren't used anywhere in the codebase, they have been deleted from the FacilityClaim model and the respective history table.

### Code/API changes
* [OSDEV-1045](https://opensupplyhub.atlassian.net/browse/OSDEV-1045) - Added flag `highlightBackground` to the DashboardFacilityCard component to highlight background for claimed facilities only on the Merge moderation screen. Added the `get_is_claimed` method to the `FacilityIndexDetailsSerializer` that returns a boolean value depending on whether the facility has an approved claim or not.
* [OSDEV-1167](https://opensupplyhub.atlassian.net/browse/OSDEV-1167) - Search. Update field names in Open Search. The following parameter/field names in the API schema for GET api/v1/production-locations has been changed:
    - `name_local` -> `local_name`
    - `url` -> `business_url`
    - `lon` -> `lng`
* [OSDEV-1025](https://opensupplyhub.atlassian.net/browse/OSDEV-1025) - Added the `get_is_claimed` method to the `FacilityMatchSerializer` that returns a boolean value depending on whether the matched facility has an approved claim or not.
* [OSDEV-1092](https://opensupplyhub.atlassian.net/browse/OSDEV-1092) - Modified the serialized output of the `FacilityClaimDetailsSerializer`:
    * Removed the `verification_method` and `phone_number` fields.
    * Added `facility_website`, `sector`, `facility_workers_count`, and `facility_name_native_language`.
* [OSDEV-1101](https://opensupplyhub.atlassian.net/browse/OSDEV-1101) - API v1/production-locations. Extend the country object to include alpha-3 code, numeric code, and country name.

### Architecture/Environment changes
* [OSDEV-1153](https://opensupplyhub.atlassian.net/browse/OSDEV-1153) - Created integration tests for the OpenSearch and for new `/api/v1/production-locations/` API endpoint.
* [OSDEV-1177](https://opensupplyhub.atlassian.net/browse/OSDEV-1177) - Implemented clearing OpenSearch and stopping Logstash during Postgres DB restore/reset in pre-prod/test/dev environments to freshly populate OpenSearch with data from the restored or reset Postgres DB.

### What's new
* [OSDEV-1045](https://opensupplyhub.atlassian.net/browse/OSDEV-1045) - The color of the facility panel for claimed facilities in the Merge moderation screen has been changed to green.
* [OSDEV-1025](https://opensupplyhub.atlassian.net/browse/OSDEV-1025) - Added the claim badge to the facility details on the C/R moderation screen when the facility has an approved claim.
* [OSDEV-1092](https://opensupplyhub.atlassian.net/browse/OSDEV-1092) - On the Facility Claims Details page, fields have been updated to show only those that could be uploaded as part of the claim form:
    * Removed deprecated fields: Phone Number, Company Name, Facility Parent Company / Supplier Group, Facility Description, and Verification Method.
    * Added new fields: Sector(s), Production Location's Website, Number of Workers, and Local Language Name.
    * Renamed fields:
        * 'Facility' to 'Location Name',
        * 'Claim Contributor' to 'Claimant Account',
        * 'Job Title' to 'Claimant Title',
        * 'Email' to 'Account Email',
        * 'Website' to 'Claimant's Website',
        * 'LinkedIn Profile' to 'Production Location's LinkedIn'.

### Release instructions:
* Before deploying to an existing environment, manually delete the related EFS storage, OpenSearch domain, and stop all tasks of the Logstash service in the appropriate ECS cluster. This is necessary to apply the new mapping for the production-locations OpenSearch index.

* Ensure that the following commands are included in the `post_deployment` command:
    * `migrate`
    * `index_facilities_new`


## Release 1.19.0

## Introduction
* Product name: Open Supply Hub
* Release date: August 24, 2024

### Code/API changes
* [OSDEV-1006](https://opensupplyhub.atlassian.net/browse/OSDEV-1006) - Create new "api/v1/production-locations" endpoint.
* [OSDEV-633](https://opensupplyhub.atlassian.net/browse/OSDEV-633) - Modified the `sectors` endpoint to return either a list of sectors or sectors grouped by their sector groups, depending on the query parameters passed to the request. Possible parameters include:
    * `embed` (optional): If present, returns a flat list of sectors submitted by a specific contributor.
    * `contributor` (optional): If embed is provided, this parameter must be included to filter sectors submitted by a specific contributor.
    * `grouped` (optional): If present, returns sectors grouped by their sector groups.
* [OSDEV-1184](https://opensupplyhub.atlassian.net/browse/OSDEV-1184) - Handle validation errors for size, sort_by and order_by parameters of "api/v1/production-locations" endpoint.
* [OSDEV-982](https://opensupplyhub.atlassian.net/browse/OSDEV-982) - Search, API. Add OS ID query parameter to v1/production-locations. Implement "api/v1/production-locations/{os_id}" endpoint.
* [OSDEV-1103](https://opensupplyhub.atlassian.net/browse/OSDEV-1103) - Enabled accent-insensitive search for `name` and `address` fields of production location by designing the index mapping to do ASCII folding for search tokens. Additionally, there were changed query_type for the `name` and `name_local` fields from `terms` to `match`.

### Architecture/Environment changes
* [OSDEV-1165](https://opensupplyhub.atlassian.net/browse/OSDEV-1165) - Updated the release protocol to include information about quick fixes and how to perform them. Additionally, updated the GitFlow diagram to visually depict this process.
* Updated the `RELEASE-PROTOCOL.md` file to include information about OpenSearch and Logstash, stating that their functionality should also be checked after deployment.
* [OSDEV-1169](https://opensupplyhub.atlassian.net/browse/OSDEV-1169) - Activated deployment database-anonymizer to production.
* [OSDEV-1197](https://opensupplyhub.atlassian.net/browse/OSDEV-1197) - Upgrade Kafka tools to version 3.8.0

### Bugfix
* [OSDEV-1048](https://opensupplyhub.atlassian.net/browse/OSDEV-1048) - Fixed error "User Cannot read properties of undefined (reading 'length')".
* [OSDEV-1180](https://opensupplyhub.atlassian.net/browse/OSDEV-1180) - Introduced a 10,000-download limit check on the api/facilities-downloads API endpoint to prevent non-API users from downloading more than 10,000 production locations.
* [OSDEV-1178](https://opensupplyhub.atlassian.net/browse/OSDEV-1178) - Added null check for claimStatuses array that fixes JS error on Dashboard/Facility Claims page.

### What's new
* [OSDEV-633](https://opensupplyhub.atlassian.net/browse/OSDEV-633) - Added a nested select to the Sectors filter. The main selection is the group name of related sectors. By pressing the header, a user can select all related sectors from this group. To view the list of related sectors, it's necessary to press the "carrot" icon next to the group heading. This action allows a user to choose a single sector from the grouped list. Additionally, entering text into the search filter displays only the filtered sectors within the opened groups.

### Release instructions:
* Before deploying to an existing environment, manually delete the related EFS storage, OpenSearch domain, and stop all tasks of the Logstash service in the appropriate ECS cluster. This is necessary to apply the new mapping for the production-locations OpenSearch index.


## Release 1.18.0

## Introduction
* Product name: Open Supply Hub
* Release date: August 10, 2024

### Database changes
#### Migrations:
* 0152_delete_tilecache_and_dynamicsetting - removed unused `api_tilecache` and `api_dynamicsetting` tables.
* 0153_add_sector_group_table - creates the `SectorGroup` model and populates it with the sector groups names.
* 0154_associate_sectors_with_groups - associates sectors with sector groups.

#### Schema changes
* [OSDEV-1142](https://opensupplyhub.atlassian.net/browse/OSDEV-1142) - Technical Debt. Remove unused `api_tilecache` and `api_dynamicsetting` tables. Migration has been created, removed related data in the code base.
* [OSDEV-360](https://opensupplyhub.atlassian.net/browse/OSDEV-360) - The following changes have been implemented:
    * A new table, `api_sectorgroup`, has been introduced and populated with sector group names.
    * A new field named `groups` has been added to the `Sector` model to establish a many-to-many relationship between the `api_sector` and the `api_sectorgroup` tables.

### Code/API changes
* [OSDEV-1005](https://opensupplyhub.atlassian.net/browse/OSDEV-1005) - Disconnect location deletion propagation to the OpenSearch cluster while the Django tests are running, as it is outside the scope of Django unit testing.

### Architecture/Environment changes
* [OSDEV-1005](https://opensupplyhub.atlassian.net/browse/OSDEV-1005) - Enable deployment of the Logstash and OpenSearch infra to AWS environments.
* [OSDEV-1156](https://opensupplyhub.atlassian.net/browse/OSDEV-1156) - The following changes have been made:
    * Defined memory and CPU configurations for Logstash and instance types for OpenSearch in each AWS environment. The memory and CPU configurations for Logstash have been set uniformly across all environments. After an investigation, it was found that the minimally sufficient requirements are 0.25 CPU and 2 GB of memory for proper Logstash operation, even with the production database. [This documentation](https://www.elastic.co/guide/en/logstash/current/jvm-settings.html) about JVM settings in the Logstash app was used to determine the appropriate resource settings. Regarding OpenSearch, the least powerful instance type was used for the Dev, Staging, and Test environments since high OpenSearch performance is not required there. For the Prod and Pre-prod environments, the minimally recommended general-purpose instance type, `m6g.large.search`, was selected. Research showed that it can process document deletions in 0.04 seconds, which is relatively fast compared to the 0.1-0.2 seconds on the `t3.small.search` instance type used for Dev, Staging, and Test. This decision was based on [this AWS Blog article](https://aws.amazon.com/blogs/aws-cloud-financial-management/better-together-graviton-2-and-gp3-with-amazon-opensearch-service/).
    * The OpenSearch instance type was parameterized.
    * The JVM direct memory consumption in the Logstash app was decreased to 512 MB to fit into two gigabytes of memory, which is the maximum available for 0.25 CPU. Total memory usage was calculated based on the formula in [this section](https://www.elastic.co/guide/en/logstash/current/jvm-settings.html#memory-size-calculation) of the Logstash JVM settings documentation.
* Updated the OpenSearch domain name to the environment-dependent Terraform (TF) local variable in the resources of the OpenSearch access policy. Utilized the `aws_opensearch_domain_policy` resource since the `access_policies` parameter on `aws_opensearch_domain` does not validate the policy correctly after its updates. See [the discussion on GitHub](https://github.com/hashicorp/terraform-provider-aws/issues/26433).

### Bugfix
* Ensure that the OpenSearch domain name is unique for each environment to avoid conflicts when provisioning domains across different environments.
* [OSDEV-1176](https://opensupplyhub.atlassian.net/browse/OSDEV-1176) - Fixed a spelling mistake in the label for the password field on the LogIn page. After the fix, the label reads "Password".
* [OSDEV-1178](https://opensupplyhub.atlassian.net/browse/OSDEV-1178) - Fixed error "Something went wrong" error after clicking on Dashboard -> View Facility Claims.

### What's new
* [OSDEV-1144](https://opensupplyhub.atlassian.net/browse/OSDEV-1144) - Claims emails. Updated text for approval, revocation, and denial emails.
* [OSDEV-360](https://opensupplyhub.atlassian.net/browse/OSDEV-360) - On the admin dashboard, functionality has been added to allow Admins to add, remove, or modify sector groups. In the `Sectors` tab, Admins can now adjust the related sector groups for each sector. Each sector must be associated with at least one group.
* [OSDEV-1005](https://opensupplyhub.atlassian.net/browse/OSDEV-1005) - Implement the propagation of production location deletions from the PostgreSQL database to the OpenSearch cluster. After this fix, the locations that were deleted will be excluded from the response of the `v1/production-location` GET API endpoint.

### Release instructions:
* Ensure that the following commands are included in the `post_deployment` command:
    * `migrate`


## Release 1.17.0

## Introduction
* Product name: Open Supply Hub
* Release date: July 27, 2024

### Database changes
#### Migrations:
* 0151_replace_index_number_of_workers - replace function `index_number_of_workers` to use one source of truth for both`number_of_workers` & `extended_fields`.

### Bugfix
* [OSDEV-1145](https://opensupplyhub.atlassian.net/browse/OSDEV-1145) - Error message appearing as red dot with no context. Error display has been fixed. Simplified displaying logic of errors. Changed error property type.
* [OSDEV-576](https://opensupplyhub.atlassian.net/browse/OSDEV-576) - Implemented one source of truth to Search query source & Production Location Details page source for field `number_of_workers`.
* [OSDEV-1146](https://opensupplyhub.atlassian.net/browse/OSDEV-1146) - Fixed issue with missed header & data for Claim Decision column while downloaded Facility Claims data in xlsx format.

### What's new
* [OSDEV-1090](https://opensupplyhub.atlassian.net/browse/OSDEV-1090) - Claims. Remove extra product type field on Claimed Facility Details page.
* [OSDEV-273](https://opensupplyhub.atlassian.net/browse/OSDEV-273) - Facility Claims. Implement filtering by Country and Status. Set 'pending' claim status as a default filter.
* [OSDEV-1083](https://opensupplyhub.atlassian.net/browse/OSDEV-1083) - Implemented a 'toggle password visibility' feature in the login, registration, reset password and user profile forms.
* The legacy `_template` API endpoint was disabled via the configuration file in favor of the new `_index_template` API endpoint, since the composable index template is used for OpenSearch. The `legacy_template` was set to `false` to start using the defined composable index template in the `production_locations.json` file. This change is necessary to avoid omitting the `production_locations.json` index template for the `production-locations` index defined in the Logstash app and to enforce the OpenSearch cluster to use the explicit mapping for the `production-locations` index.

### Release instructions:
* Ensure that the following commands are included in the `post_deployment` command:
    * `migrate`
    * `index_facilities_new`


## Release 1.16.0

## Introduction
* Product name: Open Supply Hub
* Release date: July 13, 2024

### Code/API changes
* [OSDEV-1100](https://opensupplyhub.atlassian.net/browse/OSDEV-1100) - Replaced all mentions of "facility" and "facilities" with the new production location naming in the Logstash app. Renamed `location` field in the production locations index to `coordinates`.
* [OSDEV-705](https://opensupplyhub.atlassian.net/browse/OSDEV-705) - Created an additional `RowCoordinatesSerializer` in the ContriCleaner to handle coordinate values ("lat" and "lng"). Moved the conversion of "lat" and "lng" into float point numbers from `FacilityListViewSet` to this serializer.
* Introduced a general format for all Python logs by updating the Django `LOGGING` constant. Disabled propagation for the `django` logger to the `root` logger to avoid log duplication. Removed unnecessary calls to the `basicConfig` method since only the configuration defined in the `LOGGING` constant in the settings.py file is considered valid by the current Django app.

### Bugfix
* [OSDEV-705](https://opensupplyhub.atlassian.net/browse/OSDEV-705) - Fixed the error “could not convert string to float” that occurred when a list contained columns for “lat” and “lng” and only some of the rows in these columns had data. As a result, rows are processed regardless of whether the values for “lat” and “lng” are present and valid, invalid, or empty.

### What's new
* [OSDEV-981](https://opensupplyhub.atlassian.net/browse/OSDEV-981) Reporting. History of contributor uploads. Created a new report with details about the contributor:
    * including name, ID, contributor type;
    * first upload, including date of the first upload and time since the first upload in days;
    * most recent (or “last”) upload, including date of the last upload and time since the last upload in days;
    * total (or “lifetime”) uploads and a calculation for uploads per year (= lifetime uploads = total uploads / (current year - first upload year); if “first upload year” = “current year”, then use 1 in denominator). This data is ordered based on the “date of last upload” column so that contributors who have recently contributed data are at the top of the report.
* [OSDEV-1105](https://opensupplyhub.atlassian.net/browse/OSDEV-1105) - Contribution. Allow commas in list name and update error message.
* [OSDEV-272](https://opensupplyhub.atlassian.net/browse/OSDEV-272) - Facility Claims Page. Implement ascending/descending and alphabetic sort on FE. Applied proper sorting for lower case/upper case/accented strings.
* [OSDEV-1036](https://opensupplyhub.atlassian.net/browse/OSDEV-1036) - Claims. Add a sortable "claim decision" column to claims admin page.
* [OSDEV-1053](https://opensupplyhub.atlassian.net/browse/OSDEV-1053) - Updated email notification about the claim submission.


## Release 1.15.0

## Introduction
* Product name: Open Supply Hub
* Release date: June 29, 2024

### Database changes
#### Migrations:
* 0150_introduce_function_formatting_number_to_percent - adds add_percent_to_number to DB and drop
drop_calc_column_func.

### Code/API changes
* [OSDEV-1004](https://opensupplyhub.atlassian.net/browse/OSDEV-1004) - The following changes have been made to the Logstash and OpenSearch services:
    * Prepared the SQL script to collect all the necessary data for the `v1/facilities` API endpoint according to the new API specification. Agreed upon and established a prioritization scale for gathering data related to the name, address, sector, parent_company, product_type, facility_type, processing_type, number_of_workers and location fields as follows:
        * Data from the approved claim.
        * Promoted matches (considered as promoted facility list items).
        * The most recently contributed data.
    * For the country field, the same prioritization scale has been utilized except for 'Data from the approved claims' because the claimant cannot update the country in any way.
    * Introduced a new set of Ruby scripts to filter and reorganize the incoming data at the Logstash app level, avoiding complex database queries that could lead to high database load.
    * Updated the `facilities` index template for OpenSearch to define how new fields within the facility documents are stored and indexed by OpenSearch.
    * Set up the main Logstash pipeline to run every 15 minutes.
    * Introduced ingress and egress rules for the Opensearch and Logstash.
    * Parameterized database credentials for the logstash configs input.
    * Parameterized OpenSearch domain for the logstash configs output.
    * Specified the ARN of an IAM role to be used as the master user for the OpenSearch domain.
    * Set EFS access point permissions for logstash:root user.
    * Utilized environment variables to disable authentication for OpenSearch during local development, as the authentication isn't necessary.

    All changes have been made to meet the API specification requirements for `v1/facilities` API endpoint as closely as possible.

### Architecture/Environment changes
* For the job `clean_ecr_repositories` of Destroy Environment action, it was added a new line to the script responsible for deleting ECR repositories, specifically targeting the `opensupplyhub-logstash` repository.
* The `reindex_database` and `index_facilities_new` commands have been removed from the `post_deployment` command.

### Bugfix
* [OSDEV-1098](https://opensupplyhub.atlassian.net/browse/OSDEV-1098) Reporting. A columns values in the report "Contributor type by %" are not cumulative. The SQL for the report has been rewritten in such a way that first calculates the monthly counts, then computes the cumulative counts for each month, and finally applies the add_percent_to_number function to get the desired percentages. This gives us the accumulated values for each month.

### What's new
* [OSDEV-1071](https://opensupplyhub.atlassian.net/browse/OSDEV-1071)  Replaced the term "facility" with "production location" in the claims banners
* [OSDEV-933](https://opensupplyhub.atlassian.net/browse/OSDEV-933) Facility Claims. Add "what is claims" screen. `What is claims` page with radio buttons has been added that explains more about the claim. Updated title and link text for not logged in user who wants to claim a production location.
* [OSDEV-1088](https://opensupplyhub.atlassian.net/browse/OSDEV-1088) - Collecting users' public IP addresses in the Rollbar error tracker has been disabled to meet GDPR compliance.

### Release instructions:
* Update code.


## Release 1.14.0

## Introduction
* Product name: Open Supply Hub
* Release date: June 15, 2024

### Database changes
#### Migrations:
* 0146_add_facility_workers_count_new_field_to_facilityclaim - adds the facility_workers_count_new field to the FacilityClaim model.
* 0147_copy_facility_workers_count_to_facility_workers_count_new - copies the data from the facility_workers_count field to the facility_workers_count_new field.
* 0148_remove_facility_workers_count_field_from_facilityclaim - removes the facility_workers_count field from the FacilityClaim model.
* 0149_rename_facility_workers_count_new_to_facility_workers_count - renames the facility_workers_count_new field to facility_workers_count.

#### Schema changes
* [OSDEV-1084](https://opensupplyhub.atlassian.net/browse/OSDEV-1084) - To enable adding a range for the number of workers during the claiming process, the type of the `facility_workers_count` field in the `FacilityClaim` table was changed from `IntegerField` to `CharField`.

### Architecture/Environment changes
* [OSDEV-1069](https://opensupplyhub.atlassian.net/browse/OSDEV-1069) - The following changes have been made:
    * Changed the Postgres Docker image for the database to use the official one and make the local database setup platform-agnostic, so it doesn't depend on the processor architecture.
    * Built the PostGIS program from source and installed it to avoid LLVM-related errors inside the database Docker container during local development.
* [OSDEV-1072](https://opensupplyhub.atlassian.net/browse/OSDEV-1072) - The following changes have been made:
    * Added building database-anonymizer container to the pipeline.
    * Pushing the database-anonymizer container to the repo is turned off until the database anonymizing scheduled task will be deployed to the production.
* [OSDEV-1089](https://opensupplyhub.atlassian.net/browse/OSDEV-1089) Change format gunicurn logs not pass IP address to AWS CloudWatch.
* Added command `reindex_database`
* [OSDEV-1075](https://opensupplyhub.atlassian.net/browse/OSDEV-1075) - The following changes have been made:
    * All resources created via batch job will be tagged
* [OSDEV-1089](https://opensupplyhub.atlassian.net/browse/OSDEV-1089) Change format gunicurn logs not pass IP address to AWS CloudWatch.
* Make tile generation endpoint transaction-less and remove `CREATE TEMP TABLE` statement.
* Added command `reindex_database`.
* [OSDEV-1089](https://opensupplyhub.atlassian.net/browse/OSDEV-1089) Change format gunicurn logs not pass IP address to AWS CloudWatch.
* Removed calling command `clean_facilitylistitems` from the `post_deployment` command.
* Added calling command `reindex_database` from the `post_deployment` command.
* Added calling command `index_facilities_new` from the `post_deployment` command.
* An additional loop was added to the `run_cli_task` script that repeatedly checks the status of an AWS ECS task, waiting for it to stop.

### Bugfix
* [OSDEV-1019](https://opensupplyhub.atlassian.net/browse/OSDEV-1019) - Fixed an error message to 'Your account is not verified. Check your email for a confirmation link.' when a user tries to log in with an uppercase letter in the email address and their account has not been activated through the confirmation link.
* Added the `--if-exists` flag to all calls of the `pg_restore` command to eliminate spam errors when it tries to delete resources that don't exist just because the DB can be empty. Improved the section of the README about applying the database dump locally. Specifically, SQL queries have been added to delete all the tables and recreate an empty database schema to avoid conflicts during the database dump restore.

### What's new
* [OSDEV-1030](https://opensupplyhub.atlassian.net/browse/OSDEV-1030) - The following changes have been made:
    * Replaced the "Donate" button with a "Blog" button in the header
    * Added links to the "Blog" and "Careers" pages in the footer
* [OSDEV-939](https://opensupplyhub.atlassian.net/browse/OSDEV-939) - The following changes have been made:
    * Created new steps `Supporting Documentation` & `Additional Data` for `Facility Claim Request` page.
    * Added popup for successfully submitted claim.
* [OSDEV-1084](https://opensupplyhub.atlassian.net/browse/OSDEV-1084) - Enable adding a range for the number of workers during the claiming process, either after pressing the “I want to claim this production location” link or on the Claimed Facility Details page.

### Release instructions:
* Update code.


## Release 1.13.0

## Introduction
* Product name: Open Supply Hub
* Release date: June 01, 2024

### Database changes
#### Migrations:
* 0145_new_functions_for_clean_facilitylistitems_command - introduced new sql functions for `clean_facilitylistitems` command:
    - drop_table_triggers
    - remove_items_where_facility_id_is_null
    - remove_old_pending_matches
    - remove_items_without_matches_and_related_facilities

### Code/API changes
* [OSDEV-994](https://opensupplyhub.atlassian.net/browse/OSDEV-994) API. Update to pass all merge events to user based on contrib id. A non-admin API user makes:
- a GET call to /moderation-events/merge/
and receives information about merges that have occurred for all contributors.
- a GET call to /moderation-events/merge/?contributors=<id_number_x>&contributors=<id_number_y>&contributors=<id_number_z>
and receives information about merges that have occurred for the contributors with the specified IDs.

### Architecture/Environment changes
* [OSDEV-1003](https://opensupplyhub.atlassian.net/browse/OSDEV-1003) - Added automatic building for the Logstash Docker image in the `Deploy to AWS` workflow. Refactored the `Deploy to AWS` workflow to remove redundant setting values for `build-args` of the `docker/build-push-action` action in cases where the values are not used.
* [OSDEV-1004](https://opensupplyhub.atlassian.net/browse/OSDEV-1004) - Prepared the local environment setup for the Logstash and OpenSearch services to enable local development. Created a script to start the project from scratch with a database populated with sample data.
* [OSDEV-1054](https://opensupplyhub.atlassian.net/browse/OSDEV-1054) - Added a Django command `clean_facilitylistitems` that make next steps:
    - drop table triggers;
    - remove facilitylistitems where facility_id is null;
    - remove facilitylistitems with potential match status more than thirty days;
    - remove facilitylistitems without matches and related facilities;
    - create table triggers;
    - run indexing facilities
* [OSDEV-878](https://opensupplyhub.atlassian.net/browse/OSDEV-878) - Added a Django command `post_deployment` that runs Django migrations during the deployment process. This command can be expanded to include other post-deployment tasks. Used the `post_deployment` command in the `post_deploy` job of the Deploy to AWS workflow.

### Bugfix
* [OSDEV-1056](https://opensupplyhub.atlassian.net/browse/OSDEV-1056) - Refactor OS Hub member's email anonymization.
* [OSDEV-1022](https://opensupplyhub.atlassian.net/browse/OSDEV-1022) - Fix updating facility claim for user. Bring the format of extended field values to the same format as for List / API upload during processing. This has been done because extending fields processing is happening both for List / API uploading and claim update.
* [OSDEV-788](https://opensupplyhub.atlassian.net/browse/OSDEV-788) - Re-written logic for New_Facility/Automatic_Match/Potential_Match when we collect & save data for FacilityListItemTemp/FacilityMatchTemp. That fixed issue with option `create` equal `False` for API requests.
* [OSDEV-1027](https://opensupplyhub.atlassian.net/browse/OSDEV-1027) - Fix rendering of the Average Lead Time section

### What's new
* [OSDEV-1049](https://opensupplyhub.atlassian.net/browse/OSDEV-1049) Update Release protocol.
* [OSDEV-922](https://opensupplyhub.atlassian.net/browse/OSDEV-922) Consent Message. Update wording of consent opt in message on Open Supply Hub. A user who verifies Open Supply Hub for the first time can see the updated message.
* [OSDEV-1068](https://opensupplyhub.atlassian.net/browse/OSDEV-1068) - Created report that shows the number of records from the api_facilitymatch table for contributors: 2060, 1045, 685, 3356

### Release instructions:
* Update code.
* Apply DB migrations up to the latest one.


## Release 1.12.0

## Introduction
* Product name: Open Supply Hub
* Release date: May 18, 2024

### Database changes
#### Migrations:
* 0143_create_facility_claim_attachment_table.py - create api_facilityclaimattachments table to store claimant attachments per facility claim
* 0144_remove_unnecessary_columns_from_facility_claim.py - This migration replaces the old `index_approved_claim` function with a similar one that does not index the `preferred_contact_method` field. Additionally, the migration removes `email` and `preferred_contact_method` from the `FacilityClaim` model and the respective history table.

#### Schema changes
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

#### Schema changes
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

#### Schema changes
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

#### Schema changes
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

#### Schema changes
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

#### Schema changes
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
