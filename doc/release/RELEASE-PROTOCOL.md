# Software Development Life Cycle (SDLC) for the opensupplyhub monorepo

## Overview

This document outlines the SDLC pillars of the opensupplyhub monorepo, as well as the steps and procedures to follow when preparing and releasing a new version of the system.

- [Schedule](#release-schedule)
- [General Information](#general-information)
  - [Requirements and key results](#requirements-and-key-results)
  - [Environments](#environments)
  - [Versioning](#versioning)
  - [Git branches and tags](#git-branches-and-tags)
    - [Feature branches](#feature-branches)
    - [Release branches and tags](#release-branches-and-tags)
    - [Hotfix branches](#hotfix-branches)
    - [Quick-fix branches](#quick-fix-branches)
- [Development and release of the new release version](#development-and-release-of-the-new-release-version)
  - [Duration of the development of the new release version](#duration-of-the-development-of-the-new-release-version)
  - [Introductory actions after starting the development cycle of the new release version](#introductory-actions-after-starting-the-development-cycle-of-the-new-release-version)
  - [Code Freeze](#code-freeze)
  - [QA process](#qa-process)
  - [Release to production and sandbox](#release-to-production-and-sandbox)
  - [Hotfixes](#hotfixes)
  - [Shut down the pre-prod environment](#shut-down-the-pre-prod-environment)
  - [Post Release Notes](#post-release-notes)
  - [Reloading the DedupeHub](#reloading-the-dedupehub)


## Release Schedule

| Version |  Release date | Code Freeze Date |  Responsible  |
| --- | --- |  ---   | --- |
| v1.8.0 | January 27, 2024  | January 22, 2024 | @Vlad Shapik |
| v1.9.0 | February 24, 2024  | February 19, 2024 | @Vlad Shapik |
| v1.10.0 | March 23, 2024  | March 18, 2024 | @Nessa Drew |
| v1.11.0 | April 20, 2024  | April 15, 2024 | @Nessa Drew |
| v1.12.0 | May 18, 2024  | May 14, 2024 | @Vadim Kovalenko |
| v1.13.0 | June 01, 2024  | May 29, 2024 | @Vadim Kovalenko |
| v1.14.0 | June 15, 2024  | June 12, 2024 | @Oleksandr Mazur |
| v1.15.0 | June 29, 2024  | June 26, 2024 | @Oleksandr Mazur |
| v1.16.0 | July 13, 2024  | July 10, 2024 | @Roman Stolar |
| v1.17.0 | July 27, 2024  | July 23, 2024 | @Roman Stolar |
| v1.18.0 | August 10, 2024  | August 6, 2024 | @Vlad Shapik |
| v1.19.0 | August 24, 2024  | August 20, 2024 | @Vlad Shapik |
| v1.20.0 | September 07, 2024  | September 03, 2024 | @Anhelina Bohdanova |
| v1.21.0 | September 21, 2024  | September 17, 2024 | @Anhelina Bohdanova |
| v1.22.0 | October 19, 2024  | October 15, 2024 | @Vadim Kovalenko |
| v1.23.0 | November 02, 2024  | October 29, 2024 | @Vadim Kovalenko |
| v1.24.0 | November 16, 2024  | November 12, 2024 | @Oleksandr Mazur |
| v1.25.0 | November 30, 2024  | November 26, 2024 | @Oleksandr Mazur |

## General Information

### Requirements and key results

The Software Development Life Cycle (SDLC) aims to enhance the development and release process. Here are the key aspects:
- SDLC should streamline and optimize the development process for faster delivery.
- SDLC should prevent bugs from appearing in production and sandbox environments by executing all possible checks in the CI pipeline.
- SDLC should facilitate testing of features on real datasets no later than 2 days after implementation.
- SDLC should allow for an environment with real datasets, frozen code, and resources close to production for the regression testing cycle before deploying to production and sandbox.
- SDLC should promote collaboration and communication among team members involved in the development and testing processes.

Key Results:
- Achieve zero regressions in the software.
- Maintain zero hotfixes between releases.
- Ensure 99.95% uptime for the deployed software.
- Complete the regression testing cycle within a specified timeframe.
- Validate the stability of features on real datasets immediately after implementation.
- Ensure testing on real dataset is conducted within the 2-day timeframe.
- Establish a robust environment for regression testing before deploying to production.


### Environments

The following list of environments could support [Requirements and key results](#requirements-and-key-results):

1. Feature Environment:
    - The virtual environment that runs code quality checks with the help of GitHub runners on each change in the GitHub pull request. It doesn't utilize any AWS resources.
2. [Development Environment](http://dev.os-hub.net):
    - The environment intended for quick and preliminary tests of new features and fixed bugs on seeded data by software developers immediately after merging into the `main` branch. This environment uses minimal AWS resources.
3. [Test Environment](http://test.os-hub.net):
    - The environment designed for testing new features and fixed bugs by QA and software engineers on real datasets. This environment utilizes average AWS resources and is manually deployed by QA Engineer as needed.
4. [Pre-Prod Environment](https://preprod.os-hub.net/):
    - The environment intended for use during the preparation for deploying to production and sandbox. All features and bug fixes should be verified here, as well as regression testing. It is supposed to be run only during the release process, five working days before the release. This environment uses maximum AWS resources to mirror the production environment.

Read more about the existing environments in the [ENVIRONMENTS.md](./ENVIRONMENTS.md) file.


### Versioning

We follow semantic versioning (SemVer) for our releases. The version number is structured as MAJOR.MINOR.PATCH.

- MAJOR version is increased for incompatible API changes.
- MINOR version is increased for backward-compatible features.
- PATCH version is increased for backward-compatible bug fixes.


### Git branches and tags

#### Git flow of the opensupplyhub monorepo
![Git flow of the opensupplyhub monorepo](./diagrams/gitflow.drawio.svg)

#### Feature branches

Each new feature should reside in its own branch, which can be pushed to the central repository for backup and collaboration. Feature branches should use `main` as their parent branch. When a feature is complete, it gets merged back into `main`. Features should never interact directly with release branches or release tags.

#### Release branches and tags

Once `main` has acquired enough features for a release (or a predetermined release date is approaching), you run the `Release [Init]` GitHub workflow that creates a new release branch with a version number for the release. The release version number for release branches includes only the major and minor versions.

When the release branch is ready for release, the `Release [Deploy]` workflow should be run for each environment, such as sandbox and production. This workflow will create two Git tags, each with a version number.
This workflow will also initiate the Deploy to AWS workflow and pass it the necessary parameters. If you need to clear OpenSearch indexes during deployment, you need to select the Clear OpenSearch indexes checkbox.

#### Hotfix branches

Hotfix branches are utilized to quickly patch production and sandbox releases. They resemble release branches and feature branches, except they are based on a release branch instead of `main`. This is the branch that should fork directly from a release branch. As soon as the fix is complete, it should be merged into the release branch and, if the fix isn't dirty, into `main` as well. After manually running the `Release [Deploy]` workflow, two new tags with increased patch versions will be created, and the new version will be shipped to sandbox and production environments.
This workflow will also initiate the Deploy to AWS workflow and pass it the necessary parameters. If you need to clear OpenSearch indexes during deployment, you need to select the Clear OpenSearch indexes checkbox.

#### Quick-fix branches

Quick-fix branches are utilized to quickly patch the release candidate that is being tested, avoiding the need for future hotfixes. They resemble hotfix branches, except they shouldn’t be released as tags with increased patch versions. This branch should fork directly from a release branch. Once the quick fix is complete, it should be merged into the release branch and, if the quick fix is clean, into the main branch as well. Quick fixes will be released along with other features in the release tags for sandbox and production.

## Development and release of the new release version

### Duration of the development of the new release version

The development of the new release version takes two weeks before it is released.


### Introductory actions after starting the development cycle of the new release version

Make sure that:
1. The version planned for release in two weeks is created in Jira and is indicated in all Jira tickets related to the upcoming release.
2. The start and release dates are set on the page of the release in Jira.
3. The draft with changes for the upcoming release is added to the RELEASE-NOTES.md file. Ensure the version of the release and its date are set for the change draft.
4. Verify that the release schedule in the RELEASE-PROTOCOL.md file is correctly filled.


### Code Freeze

1. Code freeze occurs every Tuesday following two weeks of development for a new release version. To enhance communication within the team, all stakeholders must be notified about the code freeze two working days before the code freeze by the responsible person for the release.
2. Before initiating the code freeze process, ensure that all commands required for the deployment process (e.g., `index_facilities_new`) are included in the `post_deployment` command.
3. On the day of the code freeze, the responsible person has to run the `Release [Init]` workflow from the `main` branch, specifying the major and minor versions of the release. Subsequently, the `releases/v.X.Y` branch will be created and automatically deployed to the running pre-prod environment via the `Deploy to AWS` workflow.
4. After a successful deployment, you should copy the ARN of the `terraform` user from the AWS IAM console. Navigate to the AWS console's search input, type "IAM", and open the IAM console. In the IAM console, find and click on the "Users" tab. In the list of available users, locate the `terraform` user, click on it, and on that page, you will find its ARN. After copying this value, go to the AWS OpenSearch console in the same way you accessed the IAM console. Open the available domains and locate the domain for the preprod environment. Open it, then navigate to the security configuration and click "Edit". Find the section titled "Fine-grained access control", and under this section, you will find an "IAM ARN" input field. Paste the copied ARN into this field and save the changes. It may take several minutes to apply. Make sure that the "Configuration change status" field has green status.
5. You need to run the `DB - Save Anonymized DB` workflow (if this job did not run on the same or the previous day). Once the Anonymized DB is successfully saved, run the `DB - Apply Anonymized DB` workflow to ensure that testing will be conducted with up-to-date data.
6. In case there is a need to run a command in the terminal of the Django container, follow [this instruction](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/140443651/DevOps+Guidelines+for+Migration+Database+Snapshots+and+ECS+Management#All-the-steps-described-in-this-Document-should-be-run-by-DevOps-or-Tech-Lead-Engineers-only%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5DHow-to-correctly-run-migrations-for-our-four-environments%3F---Even-if-it-will-be-done-in-the-OSDEV-564-JIRA-ticket%2C-we-need-to-have-instructions-for-the-current-state-of-the-infrastructure.).

### QA process

- The Test environment can be updated manually by running the `Deploy to AWS` workflow from the `main` branch at any convenient time. Be sure to select 'Test' in the 'Environment to deploy' field. This allows QA engineers to test the most recent changes on a copy of the live database. To identify the tasks that should be tested, QA engineers can refer to the Jira release page for the developing version, where all feature and bug-fix tickets intended for the release are displayed.
- Five working days before the release, which always takes place on Saturday, the QA engineer creates a new tab in [the QA Checklist sheet](https://docs.google.com/spreadsheets/d/1uinHJOPpGfrUNkewBxPVsDeDXnNx4dJnnX94LoBA_zk/edit?usp=sharing) for the new release version. They add all the features that will be shipped with the release on Saturday to the Change List section. Then, the QA engineer goes through all the items in the list. If a regression bug is found, it should be immediately documented as a Jira bug ticket and rated depending on whether it is a P1-P3 bug. If the bug has a P1 level, the entire team should be notified, and the bug ticket should be assigned to the software development team for fixing as quickly as possible. After the bug is fixed and the fix is deployed to the pre-prod environment, the entire QA checklist should be verified from the very beginning before the release.
- The QA Engineer should also test the items listed under the *prod* column in [the QA Checklist sheet](https://docs.google.com/spreadsheets/d/1uinHJOPpGfrUNkewBxPVsDeDXnNx4dJnnX94LoBA_zk/edit?usp=sharing) on the production site once the new version is released on the designated date.

### Release to production and sandbox

1. To enhance communication within the team, the responsible person for the release must notify all stakeholders about the release two working days before its scheduled date and in 1-2 hours to prevent any actions on the environment on which the deployment is carried out.
2. The responsible person have to take db snapshot manually via Amazon RDS in the `Snapshots` tab with name `env-db-date` (examples: `stg-db-05-18-2024` and `prd-db-05-18-2024`).
3. On the designated time and day, before triggering workflow on Production environment the responsible person have manually make active switch `disable_list_uploading` through the `Switch` page in the Django admin panel.
4. Then the responsible person runs the `Release [Deploy]` workflow for the sandbox and production environments from the release branch. They need to fill in the full release tag version (`X.Y.Z`) and choose the environment. If the responsible person need to clear OpenSearch indexes during deployment, they must select the Clear OpenSearch indexes checkbox.
ℹ️ Note, that `Deploy to AWS` workflow will be triggered <strong>automatically</strong> for the sandbox and production environments respectively.
5. After completing the triggered workflows, the responsible person must open the AWS console and verify that all tasks of the `OpenSupplyHubStagingAppDD`, `OpenSupplyHubStagingApp`, `OpenSupplyHubStagingAppLogstash`, `OpenSupplyHubProductionAppDD`, `OpenSupplyHubProductionApp` and `OpenSupplyHubProductionAppLogstash` services in the `ecsOpenSupplyHubStagingCluster` and `ecsOpenSupplyHubProductionCluster` Amazon ECS clusters, respectively, have been restarted.
6. Additionally, it is necessary to check the OpenSearch domains and their statuses, such as Domain Processing Status, Configuration Change Status, and Cluster Health, to ensure they are green (which indicates that everything is fine). Use the Amazon OpenSearch Service console to check this.
7. The responsible person also needs to check that DedupeHub is up and running. To do this, they should open CloudWatch via the AWS console, navigate to the Log groups section in the menu, open logOpenSupplyHubProductionAppDD and logOpenSupplyHubStagingAppDD, then open the latest log stream of each log group. Ensure that there is a recent message: `INFO: Application startup complete.`
If there is no such message and DedupeHub hangs, you need to reload it (perhaps several times), as mentioned in [Reloading the DedupeHub](#reloading-the-dedupehub).
8. Once the aforementioned steps are successfully completed, the person responsible for the release should also verify that all actions included in the post_deployment command have been successfully executed. Here is the [instructions](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/280788993/Checking+successful+application+of+post-deployment+actions+in+the+test+environment).
In case there is a need to run additional command in the terminal of the Django container, follow [this instruction](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/140443651/DevOps+Guidelines+for+Migration+Database+Snapshots+and+ECS+Management#All-the-steps-described-in-this-Document-should-be-run-by-DevOps-or-Tech-Lead-Engineers-only%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5DHow-to-correctly-run-migrations-for-our-four-environments%3F---Even-if-it-will-be-done-in-the-OSDEV-564-JIRA-ticket%2C-we-need-to-have-instructions-for-the-current-state-of-the-infrastructure.).
9. Disable the `disable_list_uploading` switch.
10. Notify the QA Engineer that the new version has been released, and they can commence testing the items listed under the *prod* column in [the QA Checklist sheet](https://docs.google.com/spreadsheets/d/1uinHJOPpGfrUNkewBxPVsDeDXnNx4dJnnX94LoBA_zk/edit?usp=sharing).
11. The QA Engineer must notify stakeholders in the *#data_x_product* Slack channel when testing is complete in the sandbox and in the production, as well as issues, if any encountered during testing.
12. Upon completing the release, the responsible person must notify stakeholders in the *#data_x_product* Slack channel that the releases to sandbox and production have concluded. Additionally, update the *Unreleased* version's status in Jira.

### Hotfixes

- To deploy a hotfix to pre-prod, you should fork from the latest release branch, and after preparing the fix, merge it back. Merging will trigger the `Deploy to AWS` workflow that will deploy the hotfix to the **running** pre-prod environment.
- To release a hotfix to production and staging, you should fork from the latest release branch, and after preparing the fix, merge it back. The last step is to execute the `Release [Deploy]` workflow for each environment separately, which will deploy the fix to these two environments. If you need to clear OpenSearch indexes during deployment, you must select the Clear OpenSearch indexes checkbox.

### Quick-fixes

- To deploy a quick-fix to pre-prod, you should fork from the latest release branch, and after preparing the fix, merge it back. Merging will trigger the `Deploy to AWS` workflow that will deploy the quick-fix to the **running** pre-prod environment. If it is a stable fix, merge it into the `main` branch as well.

### Shut down the pre-prod environment

1. Shutting down the pre-prod environment starts after passing all QA checklist items for the pre-prod.
2. First step is to destroy pre-prod DB Instance manually via RDS -> Databases -> `opensupplyhub-enc-pp`. Press Modify -> Enable deletion protection=false. Then select Delete in Actions.
3. Finally, to shut down the Pre-prod the responsible person have to select `Destroy Environment` in the Actions menu. Press run workflow with `main` branch and select `Pre-prod` env.

### Post Release Notes

On Monday after each release, current metrics should be checked by QA engineer.

1. Kamino:
    - Successfully logged with valid OS HUb admin credentials and re-directed to Kamino's [main page](https://34.241.25.221/kamino/bk).
2. Looker:
    - `duplicate_ratio_perc` ~ 2 (+- 0.1)
    - `estimated_duplicates` ~ 4000-6000
3. Airflow:
    - Dag_Id duplillom should approximately take 50 min. So we can conclude that it <strong>must be > 2.5</strong>

### Reloading the DedupeHub
- To restart DedupeHub the responsible person have to find `ecsOpenSupplyHubProductionCluster` in Amazon Elastic Container Service (ECS), select `OpenSupplyHubProductionAppDD` and press update. Then select `Force New Deployment` and press update button.
