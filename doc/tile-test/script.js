const LOCATION_LEVEL_ZOOM = 12;
const BASE_COLOR = "#00b300";
const $mapDiv = document.getElementById("map");
let map = null;
let query = null;
let polygons = [];
let markers = [];
let precision = 1;
let bounds = null;

function getCoordinates(bucket) {
  const centerCords = h3.cellToLatLng(bucket.key);
  const center = {
    lat: centerCords[0],
    lng: centerCords[1],
  };
  const boundary = h3.cellToBoundary(bucket.key).map((coords) => {
    return {
      lat: coords[0],
      lng: coords[1],
    };
  });

  return {
    ...bucket,
    boundary,
    center,
  };
}

async function fetchLocations() {
  const url = "http://localhost:9200/production-locations/_search";
  let body = {};

  if (precision <= LOCATION_LEVEL_ZOOM) {
    body = {
      ...body,
      aggregations: {
        grouped: {
          geohex_grid: {
            field: "coordinates",
            precision: precision && precision > 2 ? precision - 2 : 1,
          },
        },
      },
    }
  }

  if (precision > LOCATION_LEVEL_ZOOM) {
    body = {
      size: 200,
    }
  }

  if (query) {
    body = {
      ...body,
      multi_match: {
        query,
        fields: ["name", "address"],
      },
    };
  }

  if (bounds) {
    const southWest = bounds.getSouthWest();
    const northEast = bounds.getNorthEast();
    const coordinates = {
      top_left: {
        lat: northEast.lat(),
        lon: southWest.lng(),
      },
      bottom_right: {
        lat: southWest.lat(),
        lon: northEast.lng(),
      },
    };

    body = {
      ...body,
      query: {
        bool: {
          must: {
            match_all: {},
          },
          filter: {
            geo_bounding_box: {
              coordinates,
            },
          },
        },
      },
    };
  }

  const response = await fetch(url, {
    method: "POST",
    headers: {
      Origin: "http://localhost:9200",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await response.json();

  if (data.aggregations && data.aggregations.grouped) {
    data.aggregations.grouped.buckets =
      data.aggregations.grouped.buckets.map(getCoordinates);
  }

  return data;
}

async function drawTheGrid() {
  polygons.forEach((polygon) => polygon.setMap(null));
  markers.forEach((marker) => marker.setMap(null));

  const locations = await fetchLocations(precision, bounds);
  const buckets = locations.aggregations ? locations.aggregations.grouped.buckets : [];
  const maxCount = Math.max(...buckets.map((bucket) => bucket.doc_count));
  const { Polygon, InfoWindow } = await google.maps.importLibrary("maps");
  const { Marker } = await google.maps.importLibrary("marker")
  const infoWindow = new InfoWindow();

  polygons = buckets.map((bucket) => {
    const polygon = new Polygon({
      paths: bucket.boundary,
      strokeColor: BASE_COLOR,
      strokeOpacity: 0.8,
      strokeWeight: 3,
      fillColor: BASE_COLOR,
      fillOpacity: bucket.doc_count / maxCount,
      map
    });
    return polygon;
  });

  if (precision > LOCATION_LEVEL_ZOOM) {
    markers = locations.hits.hits.map((hit) => {
      const marker = new Marker({
        position: {
          lat: hit._source.coordinates.lat,
          lng: hit._source.coordinates.lon,
        },
        title: hit._source.name,
        map,
      });

      marker.addListener("click", () => {
        infoWindow.close();
        infoWindow.setContent(`<b>${hit._source.name}</b><br/><br/><i>${hit._source.address}</i>`);
        infoWindow.open(marker.map, marker);
      });

      return marker;
    });
  }
}

async function init() {
  const { Map } = await google.maps.importLibrary("maps");

  map = new Map($mapDiv, {
    center: { lat: 0, lng: 0 },
    zoom: precision,
    styles,
  });

  drawTheGrid();

  map.addListener("bounds_changed", async () => {
    bounds = map.getBounds();
  });

  map.addListener("zoom_changed", async () => {
    precision = map.getZoom();
  });

  map.addListener("tilesloaded", async () => {
    drawTheGrid();
  });
}

init();
