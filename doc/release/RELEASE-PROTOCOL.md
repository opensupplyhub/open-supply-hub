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
- [Development and release of the new release version](#development-and-release-of-the-new-release-version)
  - [Duration of the development of the new release version](#duration-of-the-development-of-the-new-release-version)
  - [Introductory actions after starting the development cycle of the new release version](#introductory-actions-after-starting-the-development-cycle-of-the-new-release-version)
  - [Code Freeze](#code-freeze)
  - [QA process](#qa-process)
  - [Release to production and sandbox](#release-to-production-and-sandbox)
  - [Hotfixes](#hotfixes)
  - [Shut down the pre-prod environment](#shut-down-pre-prod)
  - [Reloading the DedupeHub](#reload-dedupehub)


## Release Schedule

| Version |  Release date | Code Freeze Date |  Responsible  |
| --- | --- |  ---   | --- |
| v1.8.0 | January 27, 2024  | January 22, 2024 | @Vlad Shapik |
| v1.9.0 | February 24, 2024  | February 19, 2024 | @Vlad Shapik |
| v1.10.0 | March 23, 2024  | March 18, 2024 | @Nessa Drew |
| v1.11.0 | April 20, 2024  | April 15, 2024 | @Nessa Drew |
| v1.12.0 | May 18, 2024  | May 14, 2024 | @Vadim Kovalenko |
| v1.13.0 | June 01, 2024  | May 27, 2024 | @Vadim Kovalenko |


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
    - The environment designed for testing new features and fixed bugs by QA and software engineers on real datasets twice a week. This environment utilizes average AWS resources and is automatically deployed twice a week.
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

Once `main` has acquired enough features for a release (or a predetermined release date is approaching), you run the Release [Init] GitHub workflow that creates a new release branch with a version number for the release. The release version number for release branches includes only the major and minor versions.

When the release branch is ready for release, the Release [Deploy] workflow should be run for each environment, such as sandbox and production. This workflow will create two Git tags, each with a version number.

#### Hotfix branches

Hotfix branches are utilized to quickly patch production and sandbox releases. They resemble release branches and feature branches, except they are based on a release branch instead of `main`. This is the only branch that should fork directly from a release branch. As soon as the fix is complete, it should be merged into the release branch and, if the fix isn't dirty, into `main` as well. After manually running the Release [Deploy] workflow, two new tags with increased patch versions will be created, and the new version will be shipped to sandbox and production environments.


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

1. Code freeze occurs every Monday following two weeks of development for a new release version. To enhance communication within the team, all stakeholders must be notified about the code freeze two working days before the code freeze by the responsible person for the release.
2.  On the day of the code freeze, the responsible person has to run the Release [Init] workflow from the main branch, specifying the major and minor versions of the release. Subsequently, the releases/vX.Y branch will be created and automatically deployed to the running pre-prod environment via the Deploy to AWS workflow.
3. The final step is to follow the instructions outlined in the Release section of the [RELEASE-NOTES.md](./RELEASE-NOTES.md) file for the deployed version. In case there is a need to run a command in the terminal of the Django container, follow [this instruction](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/140443651/DevOps+Guidelines+for+Migration+Database+Snapshots+and+ECS+Management#All-the-steps-described-in-this-Document-should-be-run-by-DevOps-or-Tech-Lead-Engineers-only%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5DHow-to-correctly-run-migrations-for-our-four-environments%3F---Even-if-it-will-be-done-in-the-OSDEV-564-JIRA-ticket%2C-we-need-to-have-instructions-for-the-current-state-of-the-infrastructure.).


### QA process

- Twice a week, the Test environment is updated so that QA engineers can test the most recent changes on a copy of the live database. To identify the tasks that should be tested, they can use the Jira release page of the developing version, where all the feature and bug fix tickets intended for the release are displayed.
- Five working days before the release, which always takes place on Saturday, the QA engineer creates a new tab in [the QA Checklist sheet](https://docs.google.com/spreadsheets/d/1uinHJOPpGfrUNkewBxPVsDeDXnNx4dJnnX94LoBA_zk/edit?usp=sharing) for the new release version. They add all the features that will be shipped with the release on Saturday to the Change List section. Then, the QA engineer goes through all the items in the list. If a regression bug is found, it should be immediately documented as a Jira bug ticket and rated depending on whether it is a P1-P4 bug. If the bug has a P1 level, the entire team should be notified, and the bug ticket should be assigned to the software development team for fixing as quickly as possible. After the bug is fixed and the fix is deployed to the pre-prod environment, the entire QA checklist should be verified from the very beginning before the release.
- The QA Engineer should also test the items listed under the *prod* column in [the QA Checklist sheet](https://docs.google.com/spreadsheets/d/1uinHJOPpGfrUNkewBxPVsDeDXnNx4dJnnX94LoBA_zk/edit?usp=sharing) on the production site once the new version is released on the designated date.

### Release to production and sandbox

1. To enhance communication within the team, the responsible person for the release must notify all stakeholders about the release two working days before its scheduled date and in 1-2 hours to prevent any actions on the environment on which the deployment is carried out.
2. The responsible person have to take db snapshot manually via Amazon RDS in the `Snapshots` tab with name `env-db-date`.
3. On the designated time and day, the responsible person runs the Release [Deploy] workflow for the sandbox and production environments from the release branch. They need to fill in the full release tag version (`X.Y.Z`) and choose the environment.
4. The next step is for the responsible person to run the `Deploy to AWS` workflow for the sandbox and production environments from the release branch and not select other checkboxes.
5. After completing the triggered workflows, the responsible person must open the AWS console and verify that all tasks of the OpenSupplyHubStagingAppDD, OpenSupplyHubStagingApp, OpenSupplyHubProductionAppDD, and OpenSupplyHubProductionApp services in the ecsOpenSupplyHubStagingCluster and ecsOpenSupplyHubProductionCluster Amazon ECS clusters, respectively, have been restarted.
6. The responsible person also needs to check that DedupeHub is up and running. To do this, they should open CloudWatch via the AWS console, navigate to the Log groups section in the menu, open logOpenSupplyHubProductionAppDD and logOpenSupplyHubStagingAppDD, then open the latest log stream of each log group. Ensure that there is a recent message: `INFO: Application startup complete.`
If there is no such message and DedupeHub hangs, you need to reload it (perhaps several times), as mentioned in [Reloading the DedupeHub](#reload-dedupehub).
7. Once the aforementioned steps are successfully completed, the person responsible for the release should also follow the instructions outlined in the Release section of the [RELEASE-NOTES.md](./RELEASE-NOTES.md) file for the released version. In case there is a need to run a command in the terminal of the Django container, follow [this instruction](https://opensupplyhub.atlassian.net/wiki/spaces/SD/pages/140443651/DevOps+Guidelines+for+Migration+Database+Snapshots+and+ECS+Management#All-the-steps-described-in-this-Document-should-be-run-by-DevOps-or-Tech-Lead-Engineers-only%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5D%5BhardBreak%5DHow-to-correctly-run-migrations-for-our-four-environments%3F---Even-if-it-will-be-done-in-the-OSDEV-564-JIRA-ticket%2C-we-need-to-have-instructions-for-the-current-state-of-the-infrastructure.).
8. Notify the QA Engineer that the new version has been released, and they can commence testing the items listed under the *prod* column in [the QA Checklist sheet](https://docs.google.com/spreadsheets/d/1uinHJOPpGfrUNkewBxPVsDeDXnNx4dJnnX94LoBA_zk/edit?usp=sharing).
9. The QA Engineer must notify stakeholders in the *#data_x_product* Slack channel when testing is complete in the sandbox and in the production, as well as issues, if any encountered during testing.
10. Upon completing the release, the responsible person must notify stakeholders in the *#data_x_product* Slack channel that the releases to sandbox and production have concluded. Additionally, update the *Unreleased* version's status in Jira.
11. As the final step, shut down the pre-prod environment, as it is no longer required for the current version of the release.

### Hotfixes

- To deploy a hotfix to pre-prod, you should fork from the latest release branch, and after preparing the fix, merge it back. Merging will trigger the Deploy to AWS workflow that will deploy the hotfix to the **running** pre-prod environment. Before doing it, don't forget about the step involving switching databases, as mentioned in [the Code Freeze section]((#requirements-and-key-results)).
- To release a hotfix to production and staging, you should fork from the latest release branch, and after preparing the fix, merge it back. The last step is to execute the Release [Deploy] workflow for each environment separately, which will deploy the fix to these two environments.

### Shut down the pre-prod environment

- To shut down the Pre-prod the responsible person have to select `Destroy Environment` in the Actions menu. Press run workflow with `main` branch and select `Pre-prod` env.
- DB Instance has to be destroyed manually via RDS -> Databases -> `opensupplyhub-enc-pp`. Press Modify -> Enable deletion protection=false. Then select Delete in Actions.

### Reloading the DedupeHub
- To restart DedupeHub the responsible person have to find ecsOpenSupplyHubProductionCluster in Amazon Elastic Container Service, select OpenSupplyHubProductionAppDD and press update. Then select `Force New Deployment` and press update button.