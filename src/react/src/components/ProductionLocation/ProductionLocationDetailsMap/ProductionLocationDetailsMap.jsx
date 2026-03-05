import React, { useMemo, useRef, useCallback } from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Launch from '@material-ui/icons/Launch';
import Button from '@material-ui/core/Button';
import { Map as ReactLeafletMap, TileLayer, Marker } from 'react-leaflet';
import Control from 'react-leaflet-control';
import AddIcon from '@material-ui/icons/Add';
import RemoveIcon from '@material-ui/icons/Remove';
import MyLocationIcon from '@material-ui/icons/MyLocation';
import get from 'lodash/get';
import { withStyles } from '@material-ui/core/styles';

import 'leaflet/dist/leaflet.css';

import productionLocationDetailsMapStyles from './styles';
import {
    SATELLITE_TILE_URL,
    SATELLITE_TILE_ATTRIBUTION,
    markerIcon,
    mapContainerStyles,
} from './constants';
// import ExternalLinkIcon from './ExternalLinkIcon';
import {
    detailsZoomLevel,
    initialCenter,
    initialZoom,
} from '../../../util/constants.facilitiesMap';

/**
 * Renders the production location detail map with a satellite (aerial) base layer
 * using Leaflet's TileLayer and ESRI World Imagery. Keeps the map interactive
 * without requiring the Google Maps API.
 */
function ProductionLocationDetailsMap({ classes, data }) {
    const mapRef = useRef(null);

    const coordinates = get(data, 'geometry.coordinates', null);
    const center = useMemo(() => {
        if (Array.isArray(coordinates) && coordinates.length >= 2) {
            return [coordinates[1], coordinates[0]]; // GeoJSON [lng, lat] → Leaflet [lat, lng]
        }
        return [initialCenter.lat, initialCenter.lng];
    }, [coordinates]);

    const zoom = coordinates ? detailsZoomLevel : initialZoom;
    const position =
        Array.isArray(coordinates) && coordinates.length >= 2
            ? [coordinates[1], coordinates[0]]
            : null;

    const handleCenterOnLocation = useCallback(() => {
        const map = mapRef.current?.leafletElement;
        if (map && center) {
            map.setView(center, zoom);
        }
    }, [center, zoom]);

    const handleZoomIn = useCallback(() => {
        const map = mapRef.current?.leafletElement;
        if (map) map.zoomIn();
    }, []);

    const handleZoomOut = useCallback(() => {
        const map = mapRef.current?.leafletElement;
        if (map) map.zoomOut();
    }, []);

    const googleMapsUrl = useMemo(() => {
        if (Array.isArray(center) && center.length >= 2) {
            const [lat, lng] = center;
            return `https://www.google.com/maps?q=${lat},${lng}`;
        }
        return null;
    }, [center]);

    return (
        <div className={classes.container}>
            <Typography
                component="h3"
                variant="title"
                className={classes.sectionTitle}
            >
                <Launch />
                Geographic information
            </Typography>
            <div className={classes.mapContainer}>
                <div className={classes.mapInner}>
                    <ReactLeafletMap
                        ref={mapRef}
                        center={center}
                        zoom={zoom}
                        style={mapContainerStyles}
                        zoomControl={false}
                        scrollWheelZoom={false}
                        minZoom={2}
                        maxZoom={18}
                    >
                        <TileLayer
                            url={SATELLITE_TILE_URL}
                            attribution={SATELLITE_TILE_ATTRIBUTION}
                            minZoom={2}
                            maxZoom={19}
                        />
                        <Control position="topleft">
                            <div className={classes.mapControlsRow}>
                                <IconButton
                                    size="small"
                                    className={classes.mapControlButton}
                                    onClick={handleZoomIn}
                                    aria-label="Zoom in"
                                >
                                    <AddIcon />
                                </IconButton>
                                <IconButton
                                    size="small"
                                    className={classes.mapControlButton}
                                    onClick={handleZoomOut}
                                    aria-label="Zoom out"
                                >
                                    <RemoveIcon />
                                </IconButton>
                                <IconButton
                                    size="small"
                                    className={classes.mapControlButton}
                                    onClick={handleCenterOnLocation}
                                    aria-label="Center map on facility location"
                                >
                                    <MyLocationIcon />
                                </IconButton>
                            </div>
                        </Control>
                        {googleMapsUrl && (
                            <Control position="bottomright">
                                <Button
                                    size="small"
                                    variant="outlined"
                                    className={classes.googleMapsButton}
                                    href={googleMapsUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    startIcon={<Launch />}
                                >
                                    Open in Google Maps
                                </Button>
                            </Control>
                        )}
                        {position && (
                            <Marker position={position} icon={markerIcon} />
                        )}
                    </ReactLeafletMap>
                </div>
            </div>
        </div>
    );
}

ProductionLocationDetailsMap.propTypes = {
    classes: PropTypes.object.isRequired,
    data: PropTypes.object,
};

ProductionLocationDetailsMap.defaultProps = {
    data: null,
};

export default withStyles(productionLocationDetailsMapStyles)(
    ProductionLocationDetailsMap,
);
