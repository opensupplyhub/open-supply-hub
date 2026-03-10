// ESRI World Imagery: satellite/aerial base layer (no API key required).
// See https://leafletjs.com/ and https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a9
export const SATELLITE_TILE_URL =
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
export const SATELLITE_TILE_ATTRIBUTION =
    '&copy; <a href="https://www.esri.com/">Esri</a>, Maxar, Earthstar Geographics, and the GIS User Community';

export const mapContainerStyles = Object.freeze({
    height: '100%',
    width: '100%',
});

export const FIELD_TYPE = Object.freeze({
    ADDRESS: 'address',
    COORDINATES: 'coordinates',
});

export const GEOGRAPHIC_INFORMATION_TOOLTIP =
    'Physical address and geographic coordinates for this production location.';
