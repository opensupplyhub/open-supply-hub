import React, { useMemo, useRef, useCallback, useState } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import Button from '@material-ui/core/Button';
import { Map as ReactLeafletMap, TileLayer, Marker } from 'react-leaflet';
import Control from 'react-leaflet-control';
import AddIcon from '@material-ui/icons/Add';
import RemoveIcon from '@material-ui/icons/Remove';
import MyLocationIcon from '@material-ui/icons/MyLocation';
import LaunchIcon from '@material-ui/icons/Launch';
import InfoOutlined from '@material-ui/icons/InfoOutlined';
import get from 'lodash/get';
import { withStyles } from '@material-ui/core/styles';

import 'leaflet/dist/leaflet.css';

import VectorTileFacilitiesLayer, {
    createMarkerIcon,
} from '../../VectorTileFacilitiesLayer';
import VectorTileFacilityGridLayer from '../../VectorTileFacilityGridLayer';
import VectorTileGridLegend from '../../VectorTileGridLegend';

import productionLocationDetailsMapStyles from './styles';
import {
    SATELLITE_TILE_URL,
    SATELLITE_TILE_ATTRIBUTION,
    mapContainerStyles,
    GEOGRAPHIC_INFORMATION_TOOLTIP,
} from './constants';
import {
    detailsZoomLevel,
    initialCenter,
    initialZoom,
    maxVectorTileFacilitiesGridZoom,
} from '../../../util/constants.facilitiesMap';
import {
    productionLocationDetailsRoute,
    SelectedMarkerColor,
} from '../../../util/constants';

import MapPointer from '../../Icons/MapPointer';
import IconComponent from '../../Shared/IconComponent/IconComponent';
import DataPoint from '../DataPoint/DataPoint';
import ContributionsDrawer from '../ContributionsDrawer/ContributionsDrawer';
import useDrawerState from '../hooks';
import { getFieldContributorInfo } from './utils';
import { FIELD_CONFIG } from '..//constants';
import getSelectedDrawerField from '../utils';

/**
 * Production location detail map: satellite base layer, zoom/center controls,
 * vector-tile facilities (markers when zoomed in, circles with count when zoomed out),
 * and Open in Google Maps. Clicking other locations navigates or shows a popup list
 * when multiple facilities share the same point.
 */
const ProductionLocationDetailsMap = ({
    classes,
    singleFacilityData,
    gridColorRamp,
    history: { push },
    match: { params: { osID } = {} } = {},
}) => {
    const mapRef = useRef(null);

    const coordinates = get(singleFacilityData, 'geometry.coordinates', null);
    const hasCoordinates =
        Array.isArray(coordinates) && coordinates.length >= 2;

    const [currentMapZoomLevel, setCurrentMapZoomLevel] = useState(
        hasCoordinates ? detailsZoomLevel : initialZoom,
    );
    const [
        openDrawerFieldKey,
        isDrawerOpen,
        openDrawer,
        closeDrawer,
    ] = useDrawerState(null);

    const address = get(singleFacilityData, 'properties.address', '') || '';
    const coordinatesDisplay = hasCoordinates
        ? `${coordinates[1]}, ${coordinates[0]}`
        : '';

    const addressInfo = useMemo(
        () =>
            getFieldContributorInfo(
                singleFacilityData,
                FIELD_CONFIG.address.key,
            ),
        [singleFacilityData],
    );

    const coordinatesInfo = useMemo(
        () =>
            getFieldContributorInfo(
                singleFacilityData,
                FIELD_CONFIG.coordinates.key,
            ),
        [singleFacilityData],
    );

    const selectedDrawerContent = useMemo(
        () =>
            getSelectedDrawerField(
                [addressInfo, coordinatesInfo],
                openDrawerFieldKey,
            ),
        [openDrawerFieldKey, addressInfo, coordinatesInfo],
    );

    const center = useMemo(() => {
        if (Array.isArray(coordinates) && coordinates.length >= 2) {
            return [coordinates[1], coordinates[0]];
        }
        return [initialCenter.lat, initialCenter.lng];
    }, [coordinates]);

    const selectedMarkerIcon = useMemo(
        () => createMarkerIcon(SelectedMarkerColor),
        [],
    );

    const zoom = hasCoordinates ? detailsZoomLevel : initialZoom;

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
        if (!hasCoordinates) return null;
        const [lat, lng] = center;
        return `https://www.google.com/maps?q=${lat},${lng}`;
    }, [hasCoordinates, center]);

    const handleMarkerClick = useCallback(
        e => {
            const id = get(e, 'layer.properties.id', null);
            if (id) {
                push(productionLocationDetailsRoute.replace(':osID', id));
            }
        },
        [push],
    );

    const handleFacilityClick = useCallback(
        id => {
            if (id) {
                push(productionLocationDetailsRoute.replace(':osID', id));
            }
        },
        [push],
    );

    const handleCellClick = useCallback(event => {
        const { xmin, ymin, xmax, ymax, count } = get(
            event,
            'layer.properties',
            {},
        );
        const leafletMap = mapRef.current?.leafletElement;
        if (count && leafletMap) {
            leafletMap.fitBounds([
                [ymin, xmin],
                [ymax, xmax],
            ]);
        }
    }, []);

    const handleZoomEnd = useCallback(e => {
        const newZoom = get(e, 'target._zoom', null);
        if (typeof newZoom === 'number') {
            setCurrentMapZoomLevel(newZoom);
        }
    }, []);

    return (
        <div className={classes.container}>
            <div className={classes.sectionTitleRow}>
                <MapPointer
                    width={20}
                    height={20}
                    className={classes.sectionTitleIcon}
                />
                <Typography
                    component="h3"
                    variant="title"
                    className={classes.sectionTitle}
                >
                    Geographic Information
                </Typography>
                <IconComponent
                    title={GEOGRAPHIC_INFORMATION_TOOLTIP}
                    icon={InfoOutlined}
                    className={classes.sectionTitleInfoButton}
                    data-testid="geographic-information-tooltip"
                />
            </div>
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
                        onZoomEnd={handleZoomEnd}
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
                                    component="span"
                                    size="small"
                                    variant="outlined"
                                    color="default"
                                    className={classes.googleMapsButton}
                                    onClick={() =>
                                        window.open(
                                            googleMapsUrl,
                                            '_blank',
                                            'noopener,noreferrer',
                                        )
                                    }
                                >
                                    <LaunchIcon
                                        className={classes.googleMapsButtonIcon}
                                    />
                                    Open in Google Maps
                                </Button>
                            </Control>
                        )}
                        <Control position="bottomleft">
                            <VectorTileGridLegend
                                currentZoomLevel={currentMapZoomLevel}
                                gridColorRamp={gridColorRamp}
                                label="Production locations"
                            />
                        </Control>
                        <Control position="bottomleft">
                            <Typography
                                component="span"
                                className={classes.mapDragHint}
                            >
                                Drag to pan
                            </Typography>
                        </Control>
                        <VectorTileFacilitiesLayer
                            handleMarkerClick={handleMarkerClick}
                            handleFacilityClick={handleFacilityClick}
                            osID={osID}
                            pushRoute={push}
                            minZoom={maxVectorTileFacilitiesGridZoom + 1}
                            maxZoom={22}
                        />
                        {hasCoordinates && (
                            <Marker
                                position={center}
                                icon={selectedMarkerIcon}
                                zIndexOffset={1000}
                                interactive={false}
                            />
                        )}
                        {currentMapZoomLevel <=
                            maxVectorTileFacilitiesGridZoom && (
                            <VectorTileFacilityGridLayer
                                handleCellClick={handleCellClick}
                                minZoom={1}
                                maxZoom={maxVectorTileFacilitiesGridZoom}
                                zoomLevel={currentMapZoomLevel}
                            />
                        )}
                    </ReactLeafletMap>
                </div>
            </div>
            <div
                className={classes.infoGrid}
                data-testid="production-location-info-grid"
            >
                <div data-testid="production-location-address-row">
                    <DataPoint
                        label="Address"
                        value={address || '—'}
                        statusLabel={addressInfo.status}
                        contributorName={addressInfo.contributorName || null}
                        userId={addressInfo.userId}
                        date={addressInfo.date || null}
                        drawerData={addressInfo.drawerData}
                        tooltipText={addressInfo.tooltipText}
                        onOpenDrawer={
                            addressInfo.drawerData
                                ? () => openDrawer(addressInfo.key)
                                : undefined
                        }
                    />
                </div>
                <div data-testid="production-location-coordinates-row">
                    <DataPoint
                        label="Coordinates"
                        value={coordinatesDisplay || '—'}
                        statusLabel={coordinatesInfo.status}
                        contributorName={
                            coordinatesInfo.contributorName || null
                        }
                        userId={coordinatesInfo.userId}
                        date={coordinatesInfo.date || null}
                        drawerData={coordinatesInfo.drawerData}
                        tooltipText={coordinatesInfo.tooltipText}
                        onOpenDrawer={
                            coordinatesInfo.drawerData
                                ? () => openDrawer(coordinatesInfo.key)
                                : undefined
                        }
                    />
                </div>
            </div>
            <ContributionsDrawer
                open={isDrawerOpen}
                onClose={closeDrawer}
                fieldName={selectedDrawerContent?.label}
                promotedContribution={
                    selectedDrawerContent?.drawerData?.promotedContribution
                }
                contributions={
                    selectedDrawerContent?.drawerData?.contributions ?? []
                }
            />
        </div>
    );
};

ProductionLocationDetailsMap.propTypes = {
    classes: PropTypes.object.isRequired,
    singleFacilityData: PropTypes.object,
    gridColorRamp: PropTypes.arrayOf(PropTypes.array),
    history: PropTypes.shape({ push: PropTypes.func.isRequired }).isRequired,
    match: PropTypes.shape({
        params: PropTypes.shape({ osID: PropTypes.string }),
    }).isRequired,
};

ProductionLocationDetailsMap.defaultProps = {
    singleFacilityData: null,
    gridColorRamp: [],
};

function mapStateToProps({
    facilities: {
        singleFacility: { data: singleFacilityData },
    },
    vectorTileLayer: { gridColorRamp },
}) {
    return {
        singleFacilityData: singleFacilityData || null,
        gridColorRamp: gridColorRamp || [],
    };
}

export default withRouter(
    connect(mapStateToProps)(
        withStyles(productionLocationDetailsMapStyles)(
            ProductionLocationDetailsMap,
        ),
    ),
);
