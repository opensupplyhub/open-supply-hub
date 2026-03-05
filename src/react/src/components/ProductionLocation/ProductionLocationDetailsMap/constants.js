import L from 'leaflet';

// OpenTopoMap: free topographic/terrain-style tiles (no Google API required).
// See https://leafletjs.com/ and https://opentopomap.org/
export const OPENTOPOMAP_URL =
    'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png';
export const OPENTOPOMAP_ATTRIBUTION =
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://opentopomap.org">OpenTopoMap</a>';

export const markerIcon = L.icon({
    iconUrl: '/images/selectedmarker.png',
    iconSize: [30, 40],
    iconAnchor: [15, 40],
    popupAnchor: null,
    shadowUrl: null,
    shadowSize: null,
    shadowAnchor: null,
});

export const mapContainerStyles = Object.freeze({
    height: '100%',
    width: '100%',
});
