import React, { useMemo, useRef, useCallback } from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import {
    Map as ReactLeafletMap,
    TileLayer,
    Marker,
    ZoomControl,
} from 'react-leaflet';
import Control from 'react-leaflet-control';
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

    return (
        <div className={classes.container}>
            <Typography
                component="h3"
                variant="title"
                className={classes.sectionTitle}
            >
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
                            <IconButton
                                size="small"
                                className={classes.centerButton}
                                onClick={handleCenterOnLocation}
                                aria-label="Center map on facility location"
                            >
                                <MyLocationIcon />
                            </IconButton>
                        </Control>
                        <ZoomControl position="bottomright" />
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
