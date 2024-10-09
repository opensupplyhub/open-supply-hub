import time
import csv
import requests
import json
import click
from tabulate import tabulate

'''
Steps for testing the script

Inside container named opensearch-query-service run:

python main.py climate-trace-data-min.csv --name-search --address-search
'''


def load_query(name_search, address_search, lat, lon, name):
    with open('query.json', 'r') as file:
        query = json.load(file)

        # Disable name search if name_search is False
        if not name_search:
            query['query']['function_score']['query']['bool']['should'] = []

        # Disable address search if address_search is False
        for condition in query['query']['function_score']['query']['bool']['must'][:]:
            if 'geo_distance' in condition and not address_search:
                query['query']['function_score']['query']['bool']['must'].remove(condition)

        # Update coordinates for geo_distance
        query['query']['function_score']['query']['bool']['must'] = [
            condition for condition in query['query']['function_score']['query']['bool']['must']
        ]

        # Update geo_distance coordinates
        for condition in query['query']['function_score']['query']['bool']['must']:
            if 'geo_distance' in condition:
                condition['geo_distance']['coordinates'] = {
                    'lat': lat,
                    'lon': lon
                }

        # Update the match query for name
        for condition in query['query']['function_score']['query']['bool']['should']:
            if 'match' in condition:
                condition['match']['name']['query'] = name

    return query


# Function to send the query to OpenSearch and fetch results
def query_opensearch(query, retries=5, delay=2):
    url = "http://opensearch-single-node:9200/production-locations/_search"
    headers = {"Content-Type": "application/json"}

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(query))
            response.raise_for_status()
            data = response.json()
            hits = data.get('hits', {}).get('hits', [])
            return hits
        except requests.exceptions.ConnectionError as e:
            click.echo(f"Connection error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except requests.exceptions.HTTPError as e:
            click.echo(f"HTTP error: {e}")
            return []

    click.echo("Max retries exceeded. Could not connect to OpenSearch.")
    return []


# Function to display hits in a table
def display_results(hits):
    if hits:
        table_data = []
        for hit in hits:
            source = hit['_source']
            table_data.append([
                source.get('name', 'N/A'),
                source.get('address', 'N/A'),
                source.get('country', {}).get('name', 'N/A'),
                source.get('sector', 'N/A'),
                source.get('number_of_workers', {}).get('max', 'N/A')
            ])
        
        table_headers = ['Name', 'Address', 'Country', 'Sector', 'Number of Workers']
        click.echo(tabulate(table_data, headers=table_headers, tablefmt="grid"))
    else:
        click.echo("No results found.")


# CLI command to run the script
@click.command()
@click.argument('csvfile', type=click.File('r'))
@click.option('--name-search/--no-name-search', default=True, help="Enable or disable name search.")
@click.option('--address-search/--no-address-search', default=True, help="Enable or disable address search.")
def run(csvfile, name_search, address_search):
    """Parse CSV, modify query, and send it to OpenSearch."""
    reader = csv.DictReader(csvfile)

    for row in reader:
        click.echo(f"Processing row: {row}")

        lat = float(row.get('lat', 0))
        lon = float(row.get('lon', 0))
        name = row.get('name', '')

        query = load_query(name_search, address_search, lat, lon, name)

        hits = query_opensearch(query)

        display_results(hits)


if __name__ == '__main__':
    run()
