import { useRef, useEffect, useState, useCallback } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
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

import {
    CONFIRM_ACTION,
    MERGE_ACTION,
    REJECT_ACTION,
    MAX_PRODUCT_TYPE_COUNT,
} from './constants';

import { isCleanValueMeaningful } from './util';

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
        resetCheckboxes,
        handleSelectChange,
        toggleCheckbox,
        isCheckboxDisabled,
    };
};

export const useMergeButtonClickHandler = ({
    targetFacilityOSID,
    facilityToMergeOSID,
    facilitiesToMergeData,
    updateToMergeOSID,
    updateTargetOSID,
    fetchToMergeFacility,
    fetchTargetFacility,
    openMergeModal,
}) => {
    const handleMergeButtonClick = useCallback(() => {
        const facilitiesToMergeDataArr =
            typeof facilitiesToMergeData[0] === 'object' &&
            'os_id' in facilitiesToMergeData[0]
                ? facilitiesToMergeData.map(
                      facilityToMerge => facilityToMerge.os_id,
                  )
                : facilitiesToMergeData;

        if (
            targetFacilityOSID !== facilitiesToMergeDataArr[0] &&
            facilityToMergeOSID !== facilitiesToMergeDataArr[1]
        ) {
            updateToMergeOSID(facilitiesToMergeDataArr[1]);
            updateTargetOSID(facilitiesToMergeDataArr[0]);
            fetchToMergeFacility();
            fetchTargetFacility();
        }
        if (targetFacilityOSID !== facilitiesToMergeDataArr[0]) {
            updateTargetOSID(facilitiesToMergeDataArr[0]);
            fetchTargetFacility();
        }
        if (facilityToMergeOSID !== facilitiesToMergeDataArr[1]) {
            updateToMergeOSID(facilitiesToMergeDataArr[1]);
            fetchToMergeFacility();
        }
        openMergeModal();
    }, [
        targetFacilityOSID,
        facilityToMergeOSID,
        facilitiesToMergeData,
        updateToMergeOSID,
        updateTargetOSID,
        fetchToMergeFacility,
        fetchTargetFacility,
        openMergeModal,
    ]);

    return handleMergeButtonClick;
};

export const useMenuState = () => {
    const [menuIsOpen, setMenuIsOpen] = useState(false);

    const onMenuOpen = () => {
        setMenuIsOpen(true);
    };

    const onMenuClose = () => {
        setMenuIsOpen(false);
    };

    return { menuIsOpen, setMenuIsOpen, onMenuOpen, onMenuClose };
};

export const useExpandedGroups = optionsData => {
    const [expandedGroups, setExpandedGroups] = useState([]);

    const handleInputChange = useCallback(
        inputValue => {
            if (inputValue.trim() === '') {
                setExpandedGroups([]);
                return;
            }

            const newExpandedGroups = optionsData
                .filter(group =>
                    group.options.some(option =>
                        option.label
                            .toLowerCase()
                            .includes(inputValue.toLowerCase()),
                    ),
                )
                .map(group => group.label);

            setExpandedGroups(newExpandedGroups);
        },
        [optionsData],
    );

    return { expandedGroups, setExpandedGroups, handleInputChange };
};

export const useFileUploadHandler = ({
    resetForm,
    fetching,
    error,
    fetchLists,
    toast,
}) => {
    const fileInput = useRef(null);
    const prevFetchingRef = useRef(fetching);
    const prevFetching = prevFetchingRef.current;

    useEffect(() => {
        fetchLists();
    }, []);

    useEffect(() => resetForm, [resetForm]);

    useEffect(() => {
        prevFetchingRef.current = fetching;
    }, [fetching]);

    useEffect(() => {
        if (prevFetching && !fetching && !error) {
            const { current } = fileInput;
            if (current) {
                current.value = null;
            }

            toast('Your facility list has been uploaded successfully!');
        }
    }, [fetching, error, prevFetching, fileInput]);

    return { fileInput };
};

export const useResetScrollPosition = location => {
    useEffect(() => {
        window.scrollTo(0, 0);
    }, [location]);
};

export const useSingleLocationContributionForm = onSubmit =>
    useFormik({
        initialValues: {
            name: '',
            address: '',
            country: null,
            sector: [],
            productType: [],
            locationType: [],
            processingType: [],
            numberOfWorkers: '',
            parentCompany: '',
        },
        validationSchema: Yup.object({
            name: Yup.string()
                .test(
                    'is-trimmed',
                    'Remove leading and trailing spaces.',
                    value => value == null || value === value.trim(),
                )
                .test('not-a-number', 'Name cannot be a number.', value => {
                    if (value == null) return true;

                    const numberPattern = /^-?(0|[1-9]\d*)(\.\d+)?$/;
                    return !numberPattern.test(value);
                })
                .test(
                    'meaningful-characters',
                    'Name can’t solely consist of punctuation and whitespaces.',
                    value => value == null || isCleanValueMeaningful(value),
                )
                .max(200, 'Name cannot exceed 200 characters.')
                .required('Name is required.'),
            address: Yup.string()
                .test(
                    'is-trimmed',
                    'Remove leading and trailing spaces.',
                    value => value == null || value === value.trim(),
                )
                .test('not-a-number', 'Address cannot be a number.', value => {
                    if (value == null) return true;

                    const numberPattern = /^-?(0|[1-9]\d*)(\.\d+)?$/;
                    return !numberPattern.test(value);
                })
                .test(
                    'meaningful-characters',
                    'Address can’t solely consist of punctuation and whitespaces.',
                    value => value == null || isCleanValueMeaningful(value),
                )
                .max(200, 'Address cannot exceed 200 characters.')
                .required('Address is required.'),
            country: Yup.object().nullable().required('Country is required.'),
            productType: Yup.array().max(
                MAX_PRODUCT_TYPE_COUNT,
                `Maximum of ${MAX_PRODUCT_TYPE_COUNT} product types allowed.`,
            ),
            numberOfWorkers: Yup.string()
                .test(
                    'is-trimmed',
                    'Remove leading and trailing spaces.',
                    value => value == null || value === value.trim(),
                )
                .test(
                    'valid-format-and-range',
                    'Enter a single positive number (e.g., 5) or a valid range (e.g., 3–10). The minimum value must be less than or equal to the maximum value, and both must be greater than or equal to 1.',
                    value => {
                        if (value == null) return true;

                        const singleNumberPattern = /^\d+$/;
                        const rangePattern = /^(\d+)-(\d+)$/;

                        if (singleNumberPattern.test(value)) {
                            return (
                                !/^0/.test(value) && parseInt(value, 10) >= 1
                            );
                        }

                        const match = value.match(rangePattern);
                        if (match) {
                            const [minStr, maxStr] = match.slice(1, 3);

                            const min = parseInt(minStr, 10);
                            const max = parseInt(maxStr, 10);

                            if (/^0/.test(minStr) || /^0/.test(maxStr))
                                return false;

                            return min >= 1 && max >= 1 && min <= max;
                        }

                        return false;
                    },
                ),
            parentCompany: Yup.string()
                .test(
                    'is-trimmed',
                    'Remove leading and trailing spaces.',
                    value => value == null || value === value.trim(),
                )
                .test(
                    'not-a-number',
                    'Parent company cannot be a number.',
                    value => {
                        if (value == null) return true;

                        const numberPattern = /^-?(0|[1-9]\d*)(\.\d+)?$/;
                        return !numberPattern.test(value);
                    },
                )
                .test(
                    'meaningful-characters',
                    'Parent company can’t solely consist of punctuation and whitespaces.',
                    value => value == null || isCleanValueMeaningful(value),
                )
                .max(200, 'Parent company cannot exceed 200 characters.'),
        }),
        onSubmit,
        validateOnMount: true,
    });
