# Open Supply Hub

Open Supply Hub (OS Hub) is a tool to identify every goods production facility worldwide.

- [Requirements](#requirements)
- [Setup](#setup)
  - [Google Maps Platform](#google-maps-platform)
- [Development](#development)
  - [Kick-off & start local development](#kick-off--start-local-development)
  - [Restore the DB dump in the local Docker DB container](#restore-the-db-dump-in-the-local-docker-db-container)
  - [Creation of Superusers](#creation-of-superusers)
  - [Upload a list and process it](#upload-a-list-and-process-it)
  - [Hot Reloading 🔥](#hot-reloading-🔥)
  - [Debugging Django](#debugging-django)
  - [Embedded Maps](#embedded-maps)
  - [Ports](#ports)
- [Scripts 🧰](#scripts-🧰)
- [Tools ⚒️](#tools-⚒️)


## Requirements

- [Docker](https://docs.docker.com/desktop/install/mac-install/)
- [Git](https://git-scm.com/downloads)
- [Shellcheck](https://www.shellcheck.net)
  - `brew install shellcheck`


## Setup

- Clone repo
```
git clone git@github.com:opensupplyhub/open-supply-hub.git
cd open-supply-hub
```
- You will need to create an .env file from the provided .env.sample file.
```
cp .env.sample .env
```
- Edit that file and add the google maps API key to GOOGLE_SERVER_SIDE_API_KEY=
Reach team member for actual values.

### Google Maps Platform

OS Hub requires a Google Maps Platform API key to interface with the Maps JavaScript API, Maps Static API, and Maps Geocoding API.

Without an API key, facility detail maps will not load on the client and geocoding will not function on the server. The basemap will also be low-resolution and watermarked with "for development purposes only."

See [Getting Started with Google Maps Platform](https://developers.google.com/maps/gmp-get-started#procedures) and [Get the API key](https://developers.google.com/maps/documentation/javascript/get-api-key#get-the-api-key) for an overview on how to get setup.

```diff
-GOOGLE_SERVER_SIDE_API_KEY=
-REACT_APP_GOOGLE_CLIENT_SIDE_API_KEY=
+GOOGLE_SERVER_SIDE_API_KEY=YOUR_API_KEY
+REACT_APP_GOOGLE_CLIENT_SIDE_API_KEY=YOUR_API_KEY
 REACT_APP_GOOGLE_ANALYTICS_KEY=
 ```

 _Note: Google Maps Platfom requires creation of a billing account, but [they offer](https://cloud.google.com/maps-platform/pricing/) $200 of free monthly usage, which is enough to support development._


## Development

### Kick-off & start local development
- Start up the local development environment with seeded data in the database.
```
./scripts/start_local_dev
```
- Now you are ready for quick start the app
```
open http://localhost:6543
```

### Restore the DB dump in the local Docker DB container

1. The project containers must be running locally.
2. Download the prod dump file.
3. Place it in the `./dumps/` folder.
4. Destroy the Logstash and OpenSearch Docker containers along with their Docker images. It is necessary to refill OpenSearch with new data from the DB dump after it has been restored.
5. Connect to the local DB instance, delete all the tables, and recreate an empty DB schema to avoid conflicts during the restore using the SQL below:
```
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO public;
```
5. Then run the following command in the terminal of your machine to apply the production database dump:
```
docker compose exec -T database pg_restore --verbose --clean --if-exists --no-acl --no-owner -d opensupplyhub -U opensupplyhub < ./dumps/[dump_name].dump
```
6. After successfully completing the DB restoration, start Logstash. It will automatically start OpenSearch, as it depends on it:
```
docker compose up logstash
```

### US County Tigerline Data Setup

The platform uses US County Tigerline geometry data (2021 version) for MIT Living Wage integration. This data is loaded via Django migrations and can be sourced from either a CSV file in S3/MinIO or fixture data for local development.

#### Local Development

For local development, there are two options:

1. **Using CSV file (recommended for full dataset)**:
   - Download the CSV file from `s3://opensupplyhub-development-files-eu-west-1/data/us_county_tigerline_2021.csv`
   - Place `us_county_tigerline_2021.csv` in the `src/django/` directory
   - The migration will download it from MinIO and populate the database

2. **Using fixture data (default for quick setup)**:
   - If the CSV file is not found, the migration will skip data population gracefully
   - Fixture data is automatically loaded via the `load_fixtures` management command
   - The fixture file `src/django/api/fixtures/us_county_tigerline.json` contains sample county data for testing

The fixture data is included in the `load_fixtures` command and will be loaded when running:
```
./scripts/manage load_fixtures
```

This is automatically executed as part of `./scripts/start_local_dev`.

### Creation of Superusers

For local development we could create a superuser by Django Shell:
- Then, inside the container, execute
```
./scripts/manage createsuperuser
```
And add username (email) and a password.

In staging and production we do not have access to the Django Shell so granting
superuser permissions to a member of the OS Hub team or development team that needs
to manage the system requires the use SQL statements to adjust the permissions.

- Connect to the staging or production database via the bastion instance
- Run the following command

```sql
UPDATE api_user
SET is_staff = true, is_superuser = true
WHERE email ilike '{the user's email address}';
```

- You should see `UPDATE 1` printed to the console. If not, check the email
  address and verify that the user has in fact registered an account in the
  environment (staging or production).

### Upload a list and process it

With no AWS batch service being available unless configured, list processing must be triggered manually.
This requires a list to be uploaded, in this example, the list number was 16. You can get the list number by navigating, via the dashboard (http://localhost/dashboard), selecting “View Contributor Lists”, then choosing the one you uploaded, then checking the address bar field (possibly clicking on it to reveal the details), which should read http://localhost/lists/16 for a fresh installation.
```
./scripts/manage batch_process -a parse -l 16
```
Then the list needs to be approved (in the web browser).
Continue by accepting the list in the web browser dashboard. Then, in the django container command line, execute geocoding and matching.
```
./scripts/manage batch_process -a geocode -l 16
./scripts/manage batch_process -a match -l 16
```

### Hot Reloading 🔥

The frontend uses [Create React App](https://github.com/facebook/create-react-app/). When running `server`, the page will automatically [reload](https://github.com/facebook/create-react-app/#whats-included) if you make changes to the code.

The [Django](https://www.djangoproject.com) app runs inside a [Gunicorn](https://www.gunicorn.org) worker. The worker will [restart](https://docs.gunicorn.org/en/stable/settings.html#reload) if you make changes to the code.

### Debugging Django

Breakpoint debugging of the Python back-end is available via Visual Studio Code. To get started, run the Django development server and other services as well by passing the `--debug` flag to the `server` script. Note that you have to run the command below directly and not inside Docker container.

```
./scripts/server --debug
```

In Visual Studio Code, add this config to the `.vscode/launch.json` file:

```json
  "configurations": [
    {
        "name": "Debug Django",
        "type": "python",
        "request": "attach",
        "connect": {
            "host": "localhost",
            "port": 3000
        },
        "pathMappings": [
            {
                "localRoot": "${workspaceFolder}/src/django",
                "remoteRoot": "/usr/local/src"
            }
        ]
    }
    // Other custom configurations
  ]
```

Select the "Run and Debug" view from the sidebar. At the top of the "Run and Debug" pane, click the green arrow next to the "Debug Django" menu item.

<img width="288" alt="image" src="https://user-images.githubusercontent.com/1042475/153924321-3c60a9de-b528-4dad-92b3-8eb8184987fc.png">

If Visual Studio Code can connect, you should see a play/pause/next menu bar in the top right of the window.

Set a breakpoint by clicking in the column next to the line numbers for a `.py` file. A red dot should appear. Now, if the breakpoint is hit when you visit a page of the app in the browser (note that you can access the site via the Django development server port (8081 by default) or React development server port (6543 by default)), Visual Studio Code should highlight the line in the file, the "Run and Debug" window should be populated with information about currently set variables, and execution of the code should be paused.

### Embedded Maps

Three users in development have embedded map access by default. User c2@example.com has Embed Deluxe / Custom Embed permissions, the highest level; user c3@example.com has Embed+ permissions; and user c4@example.com has general Embed permissions, the lowest level.

In order to access the embedded map for a user with permissions, you must go to their Settings
page and set up the basic map configuration, including height and width. A preview will then
be available on their page, or you can visit http://localhost:6543/?embed=1&contributors=id where 'id' is the contributor's id.

### Ports

| Service                  | Port                            |
|--------------------------|---------------------------------|
| React development server | [`6543`](http://localhost:6543) |
| Gunicorn for Django app  | [`8081`](http://localhost:8081) |


## Scripts 🧰

| Name | Description |
| --- | --- |
| `infra` | Plan and apply remote infrastructure changes.|
| `start_local_dev` | This script starts up the local development environment with seeded data in the database. |
| `reset_database` | Clear development database & load fixture data including users, facility lists, matches, and facilities.|
| `server` | Run `docker-compose.yml` services. |
| `update` | Build container images and execute database migrations. |
| `run_be_code_quality` | This script runs a linting check, tests, and also generates the unittest code coverage report for the Django app. The script performs the same code quality checks for the backend as those conducted during the CI pipeline, excluding code coverage comparison. |
| `run_fe_code_quality` | This script performs linting and formatting checks, runs tests, and also generates the Jest code coverage report for the React app. The script performs the same code quality checks for the front-end as those conducted during the CI pipeline, excluding code coverage comparison. |
| `run_bash_script_linter`| This script runs the shellcheck linter for files in the ./scripts folder. It requires the installation of the [shellcheck](https://www.shellcheck.net/) package. |


## Tools ⚒️

| Name                   | Description                                                                                            |
|------------------------|--------------------------------------------------------------------------------------------------------|
| `batch_process`        | Given a list id argument run parse, geocode, and match via the batch_process Django management command |
| `devhealthcheck.sh`    | Simulate application load balancer health checks in development                                        |
| `postfacilitiescsv.py` | POST the rows of a CSV containing facility information to the facilities API                           |


## Running e2e (Playwright) and integration tests

### Playwright Tests

To run the Playwright tests, use the following command:
```
docker compose -f docker-compose.tests.yml run --rm --build --entrypoint "npx playwright test -c playwright.config.ts" playwright-test
```
