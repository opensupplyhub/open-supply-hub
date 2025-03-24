import { useRef, useEffect, useState, useCallback } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import get from 'lodash/get';
import head from 'lodash/head';
import last from 'lodash/last';
import delay from 'lodash/delay';
import L from 'leaflet';
import { isInt } from 'validator';

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
                .trim()
                .max(200, 'Name cannot exceed 200 characters.')
                .test('not-a-number', 'Name cannot be a number.', value =>
                    Number.isNaN(Number(value)),
                )
                .test(
                    'meaningful-characters',
                    'Name can’t solely consist of punctuation and whitespaces.',
                    value => isCleanValueMeaningful(value),
                )
                .required('Name is required'),
            address: Yup.string()
                .trim()
                .max(200, 'Address cannot exceed 200 characters.')
                .test('not-a-number', 'Address cannot be a number.', value =>
                    Number.isNaN(Number(value)),
                )
                .test(
                    'meaningful-characters',
                    'Address can’t solely consist of punctuation and whitespaces.',
                    value => isCleanValueMeaningful(value),
                )
                .required('Address is required.'),
            country: Yup.object().nullable().required('Country is required.'),
            productType: Yup.array().max(
                MAX_PRODUCT_TYPE_COUNT,
                `Maximum of ${MAX_PRODUCT_TYPE_COUNT} product types allowed.`,
            ),
            numberOfWorkers: Yup.string()
                .trim()
                .test(
                    'valid-format',
                    'Invalid format. Enter a whole number or a valid numeric range (e.g., 1-5).',
                    value => {
                        if (!value) return true;
                        const rangePattern = /^\d+-\d+$/;
                        return isInt(value, 10) || rangePattern.test(value);
                    },
                )
                .test(
                    'non-zero',
                    'The value of zero is not valid. Enter a positive whole number or a valid range (e.g., 1-5).',
                    value => {
                        if (!value) return true;
                        return parseInt(value, 10) !== 0;
                    },
                )
                .test(
                    'valid-range',
                    'Invalid range. The minimum value must be less than or equal to the maximum value.',
                    value => {
                        if (!value) return true;
                        const rangePattern = /^\d+-\d+$/;
                        if (!rangePattern.test(value)) return true;
                        const [start, end] = value
                            .split('-')
                            .map(v => v.trim());
                        return (
                            isInt(end, {
                                min: 1,
                                allow_leading_zeroes: false,
                            }) && parseInt(start, 10) <= parseInt(end, 10)
                        );
                    },
                ),
            parentCompany: Yup.string()
                .trim()
                .max(200, 'Parent company cannot exceed 200 characters.')
                .test(
                    'not-a-number',
                    'Parent company cannot be a number.',
                    value => Number.isNaN(Number(value)),
                ),
        }),
        onSubmit,
        validateOnMount: true,
    });
