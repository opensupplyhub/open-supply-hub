import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import {
    Map as ReactLeafletMap,
    TileLayer,
    Marker,
    ZoomControl,
} from 'react-leaflet';
import get from 'lodash/get';
import { withStyles } from '@material-ui/core/styles';

import 'leaflet/dist/leaflet.css';

import productionLocationDetailsMapStyles from './styles';
import {
    OPENTOPOMAP_URL,
    OPENTOPOMAP_ATTRIBUTION,
    markerIcon,
    mapContainerStyles,
} from './constants';
import {
    detailsZoomLevel,
    initialCenter,
    initialZoom,
} from '../../../util/constants.facilitiesMap';

/**
 * Renders the production location detail map with a terrain-style base layer
 * using Leaflet's TileLayer and OpenTopoMap (no Google Maps API). Avoids
 * "google is not defined" and grey tiles; uses the same pattern as Leaflet docs.
 */
function ProductionLocationDetailsMap({ classes, data }) {
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
                        center={center}
                        zoom={zoom}
                        style={mapContainerStyles}
                        zoomControl={false}
                        scrollWheelZoom={false}
                        minZoom={2}
                        maxZoom={18}
                    >
                        <TileLayer
                            url={OPENTOPOMAP_URL}
                            attribution={OPENTOPOMAP_ATTRIBUTION}
                            minZoom={2}
                            maxZoom={17}
                        />
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
