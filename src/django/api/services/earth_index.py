"""
Minimal client for the Earth Index API, the service that hosts Earth
Genome's deep searches (OSDEV-3244).

Only what the candidate ingest needs:

* ``GET /v1/projects/{project_id}`` to discover the project's finished
  deep searches (``deep_searches[].status == "success"``);
* ``GET /v1/projects/{project_id}/export`` with
  ``include_deep_search_results=true``, streamed to a local file. The body
  is a GeoJSON ``FeatureCollection`` whose features carry
  ``properties.id`` (the detection id), ``properties.confidence``,
  ``properties.deepSearchId`` / ``layerId`` / ``projectId`` and a
  ``featureType`` of ``deep_search_result`` – the shape the ingest
  command already parses.

Authentication is an Earth Index API key sent as ``Authorization:
Bearer``. The key, the project id and the base URL come from the
``EARTH_INDEX_API_KEY``, ``EARTH_INDEX_PROJECT_ID`` and
``EARTH_INDEX_API_URL`` settings; the key is never logged.
"""
from typing import Dict, List, Optional

import requests

DEFAULT_API_URL = 'https://api.earthindex.ai'
# (connect, read) seconds. The export is served from S3 and can be tens
# of megabytes; the read timeout applies per chunk, not to the whole body.
REQUEST_TIMEOUT = (10, 120)
DOWNLOAD_CHUNK_BYTES = 1024 * 1024
FINISHED_DEEP_SEARCH_STATUS = 'success'


class EarthIndexError(Exception):
    """A failed Earth Index call, with a message safe to show the user."""


class EarthIndexClient:
    def __init__(self, api_key: str, base_url: str = DEFAULT_API_URL):
        if not api_key:
            raise EarthIndexError(
                'EARTH_INDEX_API_KEY is not set. Set it to an Earth Index '
                'API key (Settings > API keys in the Earth Index app).'
            )
        self.base_url = (base_url or DEFAULT_API_URL).rstrip('/')
        self._headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json, application/geo+json',
        }

    # --- HTTP ----------------------------------------------------------

    def _get(self, path: str, params: Optional[Dict] = None,
             stream: bool = False):
        url = f'{self.base_url}{path}'
        try:
            response = requests.get(
                url, params=params, headers=self._headers,
                timeout=REQUEST_TIMEOUT, stream=stream,
            )
        except requests.RequestException as exc:
            raise EarthIndexError(
                f'Earth Index request failed: GET {path}: {exc}'
            ) from exc
        if response.status_code != 200:
            raise EarthIndexError(
                f'Earth Index answered {response.status_code} for GET '
                f'{path}: {_detail(response)}'
            )
        return response

    # --- calls ---------------------------------------------------------

    def project(self, project_id: str) -> Dict:
        """The project record, including its ``deep_searches``."""
        response = self._get(f'/v1/projects/{project_id}')
        try:
            data = response.json()
        except ValueError as exc:
            raise EarthIndexError(
                f'Earth Index project {project_id}: response is not JSON'
            ) from exc
        if not isinstance(data, dict):
            raise EarthIndexError(
                f'Earth Index project {project_id}: unexpected response '
                'shape'
            )
        return data

    @staticmethod
    def finished_deep_search_ids(
        project: Dict, layer_id: Optional[str] = None
    ) -> List[str]:
        """
        Ids of the project's deep searches that finished successfully,
        oldest first (``createdAt``), optionally only those on one layer.
        """
        searches = [
            search for search in (project.get('deep_searches') or [])
            if isinstance(search, dict)
            and search.get('status') == FINISHED_DEEP_SEARCH_STATUS
            and search.get('id')
            and (layer_id is None or search.get('layerId') == layer_id)
        ]
        searches.sort(key=lambda search: str(search.get('createdAt') or ''))
        return [str(search['id']) for search in searches]

    def download_deep_search_results(
        self, project_id: str, deep_search_ids: List[str], destination: str
    ) -> int:
        """
        Stream the GeoJSON export of ``deep_search_ids`` to ``destination``.
        Returns the number of bytes written.
        """
        if not deep_search_ids:
            raise EarthIndexError('No deep search ids to export')
        response = self._get(
            f'/v1/projects/{project_id}/export',
            params={
                'format': 'geojson',
                'include_deep_search_results': 'true',
                'deep_search_ids': ','.join(deep_search_ids),
            },
            stream=True,
        )
        written = 0
        try:
            with open(destination, 'wb') as handle:
                for chunk in response.iter_content(DOWNLOAD_CHUNK_BYTES):
                    if chunk:
                        handle.write(chunk)
                        written += len(chunk)
        except requests.RequestException as exc:
            raise EarthIndexError(
                f'Earth Index export download interrupted: {exc}'
            ) from exc
        finally:
            response.close()
        return written


def _detail(response) -> str:
    """The API's problem ``Detail`` when present, else a body excerpt."""
    try:
        body = response.json()
    except ValueError:
        body = None
    if isinstance(body, dict):
        for key in ('Detail', 'detail', 'message', 'error'):
            if body.get(key):
                return str(body[key])[:200]
    text = (getattr(response, 'text', '') or '').strip()
    return text[:200] or 'no detail'
