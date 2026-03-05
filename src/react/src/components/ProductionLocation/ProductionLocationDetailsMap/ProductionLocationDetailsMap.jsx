import React, { useMemo, useRef, useCallback } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Button from '@material-ui/core/Button';
import { Map as ReactLeafletMap, TileLayer, Marker } from 'react-leaflet';
import Control from 'react-leaflet-control';
import MarkerClusterGroup from 'react-leaflet-markercluster';
import AddIcon from '@material-ui/icons/Add';
import RemoveIcon from '@material-ui/icons/Remove';
import MyLocationIcon from '@material-ui/icons/MyLocation';
import get from 'lodash/get';
import L from 'leaflet';
import { withStyles } from '@material-ui/core/styles';

import 'leaflet/dist/leaflet.css';
import 'react-leaflet-markercluster/dist/styles.min.css';
import '../../../styles/css/leafletMap.css';

import productionLocationDetailsMapStyles from './styles';
import {
    SATELLITE_TILE_URL,
    SATELLITE_TILE_ATTRIBUTION,
    markerIcon,
    unselectedMarkerIcon,
    mapContainerStyles,
} from './constants';
import {
    detailsZoomLevel,
    initialCenter,
    initialZoom,
} from '../../../util/constants.facilitiesMap';
import { productionLocationDetailsRoute } from '../../../util/constants';

/**
 * Production location detail map: satellite base layer, zoom/center controls,
 * all facilities as markers (from Redux), and Open in Google Maps.
 */
function ProductionLocationDetailsMap({
    classes,
    data: facilitiesData,
    singleFacilityData,
    history: { push },
    match: { params: { osID } = {} } = {},
}) {
    const mapRef = useRef(null);

    const coordinates = get(singleFacilityData, 'geometry.coordinates', null);
    const center = useMemo(() => {
        if (Array.isArray(coordinates) && coordinates.length >= 2) {
            return [coordinates[1], coordinates[0]];
        }
        return [initialCenter.lat, initialCenter.lng];
    }, [coordinates]);

    const zoom = coordinates ? detailsZoomLevel : initialZoom;

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

    const navigateToProductionLocation = useCallback(
        id => push(productionLocationDetailsRoute.replace(':osID', id)),
        [push],
    );

    const features = get(facilitiesData, 'features', []).filter(
        f =>
            Array.isArray(get(f, 'geometry.coordinates')) &&
            get(f, 'geometry.coordinates', []).length >= 2,
    );

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
                                >
                                    Open in Google Maps
                                </Button>
                            </Control>
                        )}
                        <MarkerClusterGroup
                            showCoverageOnHover={false}
                            removeOutsideVisibleBounds
                            spiderfyOnMaxZoom={false}
                            iconCreateFunction={cluster => {
                                const clusterCount = cluster.getChildCount();
                                const [iconClassName, iconSize] = (() => {
                                    if (clusterCount < 10)
                                        return ['cluster-icon-one', [53, 53]];
                                    if (clusterCount < 25)
                                        return ['cluster-icon-two', [55, 55]];
                                    if (clusterCount < 50)
                                        return ['cluster-icon-three', [65, 65]];
                                    if (clusterCount < 100)
                                        return ['cluster-icon-four', [78, 78]];
                                    return ['cluster-icon-five', [90, 90]];
                                })();
                                return L.divIcon({
                                    className: `cluster-icon ${iconClassName}`,
                                    iconSize,
                                    html: `<span style="margin:-0.1rem; display: block">${clusterCount}</span>`,
                                });
                            }}
                        >
                            {features.map(f => (
                                <Marker
                                    key={f.id}
                                    position={[
                                        get(f, 'geometry.coordinates[1]', null),
                                        get(f, 'geometry.coordinates[0]', null),
                                    ]}
                                    icon={
                                        f.id === osID
                                            ? markerIcon
                                            : unselectedMarkerIcon
                                    }
                                    onClick={() =>
                                        navigateToProductionLocation(f.id)
                                    }
                                />
                            ))}
                        </MarkerClusterGroup>
                    </ReactLeafletMap>
                </div>
            </div>
        </div>
    );
}

ProductionLocationDetailsMap.propTypes = {
    classes: PropTypes.object.isRequired,
    data: PropTypes.object,
    singleFacilityData: PropTypes.object,
    history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
    match: PropTypes.shape({
        params: PropTypes.shape({ osID: PropTypes.string }),
    }).isRequired,
};

ProductionLocationDetailsMap.defaultProps = {
    data: null,
    singleFacilityData: null,
};

function mapStateToProps({
    facilities: {
        facilities: { data },
        singleFacility: { data: singleFacilityData },
    },
}) {
    return {
        data: data || null,
        singleFacilityData: singleFacilityData || null,
    };
}

export default withRouter(
    connect(mapStateToProps)(
        withStyles(productionLocationDetailsMapStyles)(
            ProductionLocationDetailsMap,
        ),
    ),
);
