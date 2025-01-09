const $mapDiv = document.getElementById("map");
let map = null;
let query = null;
let polygons = [];
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
  let body = {
    aggregations: {
      grouped: {
        geohex_grid: {
          field: "coordinates",
          precision: precision && precision > 2 ? precision - 2 : 1,
        },
      },
    },
  };

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
  const locations = await fetchLocations(precision, bounds);
  const buckets = locations.aggregations.grouped.buckets;
  const maxCount = Math.max(...buckets.map((bucket) => bucket.doc_count));
  polygons.forEach((polygon) => polygon.setMap(null));
  polygons = [];

  buckets.forEach((bucket) => {
    const polygon = new google.maps.Polygon({
      paths: bucket.boundary,
      strokeColor: "#FF0000",
      strokeOpacity: 0.8,
      strokeWeight: 3,
      fillColor: "#FF0000",
      fillOpacity: bucket.doc_count / maxCount,
    });

    polygon.setMap(map);
    polygons.push(polygon);
  });
}

async function init() {
  const { Map } = await google.maps.importLibrary("maps");

  map = new Map($mapDiv, {
    center: { lat: 0, lng: 0 },
    zoom: precision,
  });

  drawTheGrid();

  map.addListener("tilesloaded", async () => {
    bounds = map.getBounds();
    precision = map.getZoom();
    drawTheGrid();
  });
}

init();
