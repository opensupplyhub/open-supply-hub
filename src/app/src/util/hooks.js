import { useRef, useEffect, useState } from 'react';
import get from 'lodash/get';
import head from 'lodash/head';
import last from 'lodash/last';
import delay from 'lodash/delay';
import L from 'leaflet';

import {
    detailsZoomLevel,
    initialZoom,
    initialCenter,
    maxVectorTileFacilitiesGridZoom,
} from './constants.facilitiesMap';

import { CONFIRM_ACTION, MERGE_ACTION, REJECT_ACTION } from './constants';

export const useUpdateLeafletMapImperatively = (
    resetButtonClickCount,
    {
        osID,
        data,
        shouldPanMapToFacilityDetails,
        isVectorTileMap = false,
        extent,
        zoomToSearch,
        boundary,
    } = {},
) => {
    const mapRef = useRef(null);

    const [currentExtent, setCurrentExtent] = useState(extent);
    useEffect(() => {
        if (zoomToSearch && extent != null && currentExtent !== extent) {
            const leafletMap = get(mapRef, 'current.leafletElement', null);

            const bounds = L.latLngBounds(
                [extent[3], extent[2]],
                [extent[1], extent[0]],
            );

            if (boundary) {
                // leaflet takes lat, lng, but geometry.coordinates
                // is [lng, lat] - we need to explicitly name the lat and lng
                const latLngs = boundary.coordinates[0].map(lngLat => ({
                    lng: lngLat[0],
                    lat: lngLat[1],
                }));
                bounds.extend(L.latLngBounds(latLngs));
            }

            if (leafletMap) {
                leafletMap.fitBounds(bounds, {
                    maxZoom: detailsZoomLevel,
                    padding: [20, 20],
                });
            }

            setCurrentExtent(extent);
        }
    }, [extent, currentExtent, zoomToSearch, boundary]);

    // Reset the map state when the reset button is clicked
    // while zoom to search is disabled.
    const [
        currentResetButtonClickCount,
        setCurrentResetButtonClickCount,
    ] = useState(resetButtonClickCount);

    useEffect(() => {
        if (
            !zoomToSearch &&
            resetButtonClickCount !== currentResetButtonClickCount
        ) {
            const leafletMap = get(mapRef, 'current.leafletElement', null);

            if (leafletMap) {
                leafletMap.setView(initialCenter, initialZoom);
            }

            setCurrentResetButtonClickCount(resetButtonClickCount);
        }
    }, [
        resetButtonClickCount,
        currentResetButtonClickCount,
        setCurrentResetButtonClickCount,
        zoomToSearch,
    ]);

    // Set the map view centered on the facility marker, zoomed to level 15
    // if the user has arrived at the page with a URL including an OS ID.
    const [
        shouldSetViewOnReceivingData,
        setShouldSetViewOnReceivingData,
    ] = useState(!!osID);

    useEffect(() => {
        if (data && shouldSetViewOnReceivingData) {
            const leafletMap = get(mapRef, 'current.leafletElement', null);
            const facilityLocation = get(data, 'geometry.coordinates', null);

            delay(() => {
                if (leafletMap && facilityLocation) {
                    const facilityLatLng = {
                        lng: head(facilityLocation),
                        lat: last(facilityLocation),
                    };

                    leafletMap.setView(facilityLatLng, detailsZoomLevel);
                }
            }, 0);

            setShouldSetViewOnReceivingData(false);
        }
    }, [data, shouldSetViewOnReceivingData, setShouldSetViewOnReceivingData]);

    useEffect(() => {
        const leafletMap = get(mapRef, 'current.leafletElement', null);

        const facilityLocation = get(data, 'geometry.coordinates', null);

        if (leafletMap && facilityLocation) {
            const facilityLatLng = {
                lng: head(facilityLocation),
                lat: last(facilityLocation),
            };

            const mapBoundsContainsFacility = leafletMap
                .getBounds()
                .contains(facilityLatLng);

            const currentMapZoomLevel = leafletMap.getZoom();

            const shouldSetMapView =
                (isVectorTileMap &&
                    currentMapZoomLevel <
                        maxVectorTileFacilitiesGridZoom + 1) ||
                !mapBoundsContainsFacility;

            if (shouldSetMapView) {
                leafletMap.setView(facilityLatLng, detailsZoomLevel);
            }
        }
    }, [data, shouldPanMapToFacilityDetails, isVectorTileMap]);

    return mapRef;
};

export const useCheckboxManager = () => {
    const [action, setAction] = useState(CONFIRM_ACTION);
    const [activeCheckboxes, setActiveCheckboxes] = useState([]);
    const [activeSubmitButton, setActiveSubmitButton] = useState(false);

    const handleConfirmSelection = item => {
        setActiveCheckboxes(
            activeCheckboxes.some(activeItem => activeItem.id === item.id)
                ? []
                : [item],
        );
    };

    const resetCheckboxes = () => {
        setActiveCheckboxes([]);
    };

    const handleRejectSelection = item => {
        const currentIndex = activeCheckboxes.findIndex(
            activeItem => activeItem.id === item.id,
        );
        const newActiveCheckboxes = [...activeCheckboxes];

        if (currentIndex === -1) {
            newActiveCheckboxes.push(item);
        } else {
            newActiveCheckboxes.splice(currentIndex, 1);
        }
        setActiveCheckboxes(newActiveCheckboxes);
    };

    const handleMergeSelection = item => {
        const currentIndex = activeCheckboxes.findIndex(
            activeItem => activeItem.id === item.id,
        );
        const newActiveCheckboxes = [...activeCheckboxes];

        if (currentIndex === -1 && newActiveCheckboxes.length < 2) {
            newActiveCheckboxes.push(item);
        } else if (currentIndex !== -1) {
            newActiveCheckboxes.splice(currentIndex, 1);
        }
        setActiveCheckboxes(newActiveCheckboxes);
    };

    const toggleCheckbox = item => {
        switch (action) {
            case CONFIRM_ACTION:
                handleConfirmSelection(item);
                break;
            case REJECT_ACTION:
                handleRejectSelection(item);
                break;
            case MERGE_ACTION:
                handleMergeSelection(item);
                break;
            default:
                throw new Error('Unknown action type!');
        }
    };

    const handleSelectChange = value => {
        setAction(value);
        resetCheckboxes();
        setActiveSubmitButton(false);
    };

    const isCheckboxDisabled = id => {
        switch (action) {
            case CONFIRM_ACTION:
                return (
                    activeCheckboxes.length > 0 && activeCheckboxes[0].id !== id
                );
            case MERGE_ACTION:
                return (
                    activeCheckboxes.length >= 2 &&
                    !activeCheckboxes.some(activeItem => activeItem.id === id)
                );
            default:
                return false;
        }
    };

    useEffect(() => {
        const shouldSetActive =
            (action === MERGE_ACTION && activeCheckboxes.length === 2) ||
            (action === CONFIRM_ACTION && activeCheckboxes.length === 1) ||
            (action === REJECT_ACTION && activeCheckboxes.length > 0);
        setActiveSubmitButton(shouldSetActive);
    }, [activeCheckboxes, action]);

    return {
        action,
        activeCheckboxes,
        activeSubmitButton,
        handleSelectChange,
        toggleCheckbox,
        isCheckboxDisabled,
    };
};
