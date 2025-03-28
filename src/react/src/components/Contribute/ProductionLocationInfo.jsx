import React, { useEffect, useMemo, useState, useRef } from 'react';
import { useLocation, useParams, useHistory } from 'react-router-dom';
import { array, bool, func, number, object, string } from 'prop-types';
import { connect } from 'react-redux';
import { toast } from 'react-toastify';
import { endsWith, isEmpty, toString } from 'lodash';

import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Paper from '@material-ui/core/Paper';
import Switch from '@material-ui/core/Switch';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import {
    createProductionLocation,
    updateProductionLocation,
    fetchProductionLocationByOsId,
    resetPendingModerationEvent,
    resetSingleProductionLocation,
} from '../../actions/contributeProductionLocation';
import {
    fetchSingleModerationEvent,
    cleanupContributionRecord,
} from '../../actions/dashboardContributionRecord';
import {
    fetchCountryOptions,
    fetchFacilityProcessingTypeOptions,
} from '../../actions/filterOptions';

import {
    mockedSectors,
    productionLocationInfoRouteCommon,
    MODERATION_STATUSES_ENUM,
    DISABLE_LIST_UPLOADING,
    MAINTENANCE_MESSAGE,
} from '../../util/constants';
import { useResetScrollPosition } from '../../util/hooks';
import {
    countryOptionsPropType,
    facilityProcessingTypeOptionsPropType,
    moderationEventsListItemPropType,
    productionLocationPropType,
} from '../../util/propTypes';
import { productionLocationInfoStyles } from '../../util/styles';
import {
    mapDjangoChoiceTuplesToSelectOptions,
    mapFacilityTypeOptions,
    mapProcessingTypeOptions,
    isValidNumberOfWorkers,
    isRequiredFieldValid,
    getSelectStyles,
    getNumberOfWorkersValidationError,
} from '../../util/util';

import FeatureFlag from '../FeatureFlag';
import RequiredAsterisk from '../RequiredAsterisk';
import StyledSelect from '../Filters/StyledSelect';
import RequireAuthNotice from '../RequireAuthNotice';
import StyledTooltip from '../StyledTooltip';

import InputErrorText from './InputErrorText';
import ProductionLocationDialog from './ProductionLocationDialog';

const ProductionLocationInfo = ({
    submitMethod,
    classes,
    countriesOptions,
    fetchCountries,
    facilityProcessingTypeOptions,
    fetchModerationEvent,
    handleCreateProductionLocation,
    handleUpdateProductionLocation,
    fetchFacilityProcessingType,
    pendingModerationEventData,
    pendingModerationEventFetching,
    pendingModerationEventError,
    singleModerationEventItem,
    singleModerationEventItemFetching,
    singleModerationEventItemError,
    fetchProductionLocation,
    singleProductionLocationData,
    singleProductionLocationFetching,
    singleProductionLocationError,
    innerWidth,
    handleCleanupContributionRecord,
    handleResetPendingModerationEvent,
    handleResetSingleProductionLocation,
    userHasSignedIn,
    fetchingSessionSignIn,
}) => {
    const TITLE = 'Production Location Information';
    const location = useLocation();
    const history = useHistory();
    const { moderationID, osID } = useParams();

    const queryParams = new URLSearchParams(location.search);
    const nameInQuery = queryParams.get('name');
    const addressInQuery = queryParams.get('address');
    const countryInQuery = queryParams.get('country');
    const [inputName, setInputName] = useState(nameInQuery ?? '');
    const [inputAddress, setInputAddress] = useState(addressInQuery ?? '');
    const [inputCountry, setInputCountry] = useState(null);
    const [nameTouched, setNameTouched] = useState(false);
    const [addressTouched, setAddressTouched] = useState(false);
    const [countryTouched, setCountryTouched] = useState(false);
    const [enabledTaxonomy, setEnabledTaxonomy] = useState(false);
    const [sector, setSector] = useState('');
    const [productType, setProductType] = useState([]);
    const [locationType, setLocationType] = useState(null);
    const [processingType, setProcessingType] = useState(null);
    const [numberOfWorkers, setNumberOfWorkers] = useState('');
    const [parentCompany, setParentCompany] = useState('');
    const customSelectComponents = { DropdownIndicator: null };
    const isCountryError = countryTouched && !inputCountry?.value;

    const resetAdditionalDataFields = () => {
        setSector('');
        setProductType([]);
        setLocationType(null);
        setProcessingType(null);
        setNumberOfWorkers('');
        setParentCompany('');
    };

    useResetScrollPosition(location);

    const inputData = useMemo(
        () => ({
            name: inputName,
            address: inputAddress,
            country: inputCountry,
            sector,
            productType,
            locationType,
            processingType,
            numberOfWorkers,
            parentCompany,
        }),
        [
            inputName,
            inputAddress,
            inputCountry,
            sector,
            productType,
            locationType,
            processingType,
            numberOfWorkers,
            parentCompany,
        ],
    );

    const [
        showProductionLocationDialog,
        setShowProductionLocationDialog,
    ] = useState(null);

    const handleNameChange = event => {
        setInputName(event.target.value);
    };
    const handleAddressChange = event => {
        setInputAddress(event.target.value);
    };
    const handleParentCompanyChange = event => {
        setParentCompany(event.target.value);
    };

    const handleNameBlur = () => {
        setNameTouched(true);
    };
    const handleAddressBlur = () => {
        setAddressTouched(true);
    };
    const handleCountryBlur = () => {
        setCountryTouched(true);
    };

    const isFormValid = !!(
        isRequiredFieldValid(inputName) &&
        isRequiredFieldValid(inputAddress) &&
        inputCountry?.value &&
        isValidNumberOfWorkers(numberOfWorkers)
    );

    let handleProductionLocation;
    switch (submitMethod) {
        case 'POST':
            handleProductionLocation = handleCreateProductionLocation;
            break;
        case 'PATCH':
            handleProductionLocation = data =>
                handleUpdateProductionLocation(data, osID);
            break;
        default:
            handleProductionLocation = () => {
                console.error(`Unsupported submit method: ${submitMethod}`);
            };
            break;
    }

    const instructionExtraMessage =
        submitMethod === 'PATCH'
            ? 'These fields are pre-filled with the data from your search, but you can edit them.'
            : '';
    const submitButtonText = submitMethod === 'POST' ? 'Submit' : 'Update';

    const [showAdditionalInfo, setShowAdditionalInfo] = useState(false);
    const onSwitchChange = () => {
        setShowAdditionalInfo(prevShowAdditionalInfo => {
            const newShowAdditionalInfo = !prevShowAdditionalInfo;
            if (!newShowAdditionalInfo) {
                resetAdditionalDataFields();
            }
            return newShowAdditionalInfo;
        });
    };

    useEffect(() => {
        if (submitMethod === 'PATCH' && osID) {
            fetchProductionLocation(osID);
        }
    }, [submitMethod, osID, fetchProductionLocation]);

    useEffect(() => {
        if (showProductionLocationDialog === false) {
            const pathSegments = location.pathname.split('/');
            // URL may contain trailing slash which should be trimmed
            if (endsWith(pathSegments, '')) {
                pathSegments.pop();
            }
            pathSegments.pop();
            const baseContributeInfoLocation = pathSegments.join('/');
            history.push({
                pathname: baseContributeInfoLocation,
                search: '',
            });
            handleCleanupContributionRecord();
            handleResetPendingModerationEvent();
        }
    }, [showProductionLocationDialog]);

    useEffect(() => {
        if (singleProductionLocationData && osID) {
            setInputName(singleProductionLocationData.name ?? '');
            setInputAddress(singleProductionLocationData.address ?? '');
            if (singleProductionLocationData.country) {
                setInputCountry({
                    value: singleProductionLocationData?.country.alpha_2,
                    label: singleProductionLocationData?.country.name,
                });
            }
        }
    }, [singleProductionLocationData, osID]);

    const prevModerationIDRef = useRef();
    useEffect(() => {
        if (
            moderationID &&
            prevModerationIDRef.current !== moderationID &&
            isEmpty(singleModerationEventItem)
        ) {
            fetchModerationEvent(moderationID);
        }
        if (
            singleModerationEventItem?.os_id &&
            isEmpty(singleProductionLocationData)
        ) {
            fetchProductionLocation(singleModerationEventItem.os_id);
        }
        prevModerationIDRef.current = moderationID;
    }, [moderationID, singleModerationEventItem]);

    useEffect(() => {
        if (!countriesOptions) {
            fetchCountries();
        }
    }, [countriesOptions, fetchCountries]);

    useEffect(() => {
        if (countriesOptions && !isEmpty(countryInQuery)) {
            const prefilledCountry = countriesOptions.filter(
                el => el.value === countryInQuery,
            );
            setInputCountry(prefilledCountry[0]);
        }
    }, [countriesOptions]);

    useEffect(() => {
        if (!facilityProcessingTypeOptions) {
            fetchFacilityProcessingType();
        }
    }, [facilityProcessingTypeOptions, fetchFacilityProcessingType]);

    useEffect(() => {
        if (pendingModerationEventData?.cleaned_data) {
            toast('Your contribution has been added successfully!');
            if (pendingModerationEventData?.moderation_id) {
                localStorage.setItem(
                    pendingModerationEventData.moderation_id,
                    JSON.stringify(pendingModerationEventData?.cleaned_data),
                );
                history.push({
                    pathname: `${location.pathname}${pendingModerationEventData.moderation_id}`,
                    search: '',
                });
            }
        }
    }, [pendingModerationEventData]);

    useEffect(() => {
        if (!isEmpty(singleModerationEventItem) && moderationID) {
            localStorage.removeItem(moderationID);
        }
        if (moderationID) {
            setShowProductionLocationDialog(true);
        }
    }, [singleModerationEventItem, pendingModerationEventData, moderationID]);

    useEffect(() => {
        // Force trailing slash in URL to prevent broken UX scenarios
        if (location.pathname && !location.pathname.endsWith('/')) {
            history.replace(`${location.pathname}/`);
        }

        const unListen = history.listen(appLocation => {
            if (
                appLocation.pathname === productionLocationInfoRouteCommon ||
                appLocation.pathname ===
                    `${productionLocationInfoRouteCommon}${osID}/info/`
            ) {
                setShowProductionLocationDialog(false);
            }
        });

        return () => {
            unListen();
        };
    }, [location.pathname, history, osID]);

    useEffect(() => {
        if (!pendingModerationEventFetching && pendingModerationEventError) {
            toast(toString(pendingModerationEventError));
        }
    }, [pendingModerationEventFetching, pendingModerationEventError]);

    useEffect(() => {
        /*
        After first POST or PATCH v1/production-locations, there will be an error
        because moderation event should be re-indexed in the OpenSearch,
        so move this effect to the very end of event loop to make sure moderation event
        will be saved in the local storage
        */
        let timeoutId;
        if (
            moderationID &&
            !singleModerationEventItemFetching &&
            singleModerationEventItemError &&
            !localStorage.getItem(moderationID)
        ) {
            timeoutId = setTimeout(() => {
                toast(toString(singleModerationEventItemError));
            }, 0);
        }
        return () => {
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
        };
    }, [
        singleModerationEventItemFetching,
        singleModerationEventItemError,
        moderationID,
    ]);

    useEffect(() => {
        setEnabledTaxonomy(
            sector.length === 1 && sector[0].value === 'Apparel',
        );
    }, [sector]);

    useEffect(
        () => () => {
            handleCleanupContributionRecord();
            handleResetPendingModerationEvent();
            handleResetSingleProductionLocation();
        },
        [],
    );

    useEffect(() => {
        if (!isEmpty(singleProductionLocationError)) {
            toast(singleProductionLocationError[0]);
        }
    }, [singleProductionLocationError]);

    const activeSubmitButton = (
        <Button
            color="secondary"
            variant="contained"
            onClick={() => handleProductionLocation(inputData, osID)}
            className={classes.submitButtonStyles}
            disabled={!isFormValid}
        >
            {submitButtonText}
        </Button>
    );

    const maintenanceSubmitButton = (
        <StyledTooltip title={MAINTENANCE_MESSAGE} placement="top">
            <div className={classes.submitButtonWrapperStyles}>
                <Button
                    className={classes.submitButtonStyles}
                    disabled
                    variant="contained"
                    aria-label="Submit button disabled during maintenance"
                >
                    {submitButtonText}
                </Button>
            </div>
        </StyledTooltip>
    );

    if (fetchingSessionSignIn) {
        return (
            <div className={classes.circularProgressContainerStyles}>
                <CircularProgress />
            </div>
        );
    }

    if (!userHasSignedIn) {
        return <RequireAuthNotice title={TITLE} />;
    }

    if (singleProductionLocationFetching) {
        return (
            <div className={classes.circularProgressStyles}>
                <CircularProgress />
            </div>
        );
    }

    return (
        <>
            <div className={classes.mainContainerStyles}>
                <Typography component="h1" className={classes.headerStyles}>
                    {TITLE}
                </Typography>
                <Typography className={classes.instructionStyles}>
                    {`Use the form below to edit the name, address, and country
                    for your production location. ${instructionExtraMessage}`}
                </Typography>
                <Paper className={classes.infoWrapStyles}>
                    <div
                        className={`${classes.inputSectionWrapStyles} ${classes.wrapStyles}`}
                    >
                        <Typography
                            component="h2"
                            className={classes.titleStyles}
                        >
                            Location Name <RequiredAsterisk />
                        </Typography>

                        <Typography
                            component="h4"
                            className={classes.subTitleStyles}
                        >
                            Enter the name of the production location that you
                            are uploading.
                        </Typography>
                        <TextField
                            id="name"
                            className={classes.textInputStyles}
                            value={inputName}
                            onChange={handleNameChange}
                            onBlur={handleNameBlur}
                            placeholder="Enter the name"
                            variant="outlined"
                            aria-label="Enter the name"
                            InputProps={{
                                classes: {
                                    input: `
                                    ${
                                        nameTouched &&
                                        !isRequiredFieldValid(inputName) &&
                                        classes.errorStyle
                                    }`,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                            helperText={
                                nameTouched &&
                                !isRequiredFieldValid(inputName) && (
                                    <InputErrorText />
                                )
                            }
                            FormHelperTextProps={{
                                className: classes.helperText,
                            }}
                            error={
                                nameTouched && !isRequiredFieldValid(inputName)
                            }
                        />
                    </div>
                    <div
                        className={`${classes.inputSectionWrapStyles} ${classes.wrapStyles}`}
                    >
                        <Typography
                            component="h2"
                            className={classes.titleStyles}
                        >
                            Address <RequiredAsterisk />
                        </Typography>
                        <Typography
                            component="h4"
                            className={classes.subTitleStyles}
                        >
                            Enter the address of the production location. We
                            will use this to plot the location on a map.
                        </Typography>
                        <TextField
                            id="address"
                            className={classes.textInputStyles}
                            value={inputAddress}
                            onChange={handleAddressChange}
                            onBlur={handleAddressBlur}
                            placeholder="Enter the full address"
                            variant="outlined"
                            aria-label="Enter the address"
                            InputProps={{
                                classes: {
                                    input: `${classes.searchInputStyles}
                                ${
                                    addressTouched &&
                                    !isRequiredFieldValid(inputAddress) &&
                                    classes.errorStyle
                                }`,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                            helperText={
                                addressTouched &&
                                !isRequiredFieldValid(inputAddress) && (
                                    <InputErrorText />
                                )
                            }
                            FormHelperTextProps={{
                                className: classes.helperText,
                            }}
                            error={
                                addressTouched &&
                                !isRequiredFieldValid(inputAddress)
                            }
                        />
                    </div>
                    <div
                        className={`${classes.inputSectionWrapStyles} ${classes.wrapStyles}`}
                    >
                        <Typography
                            component="h2"
                            className={classes.titleStyles}
                        >
                            Country <RequiredAsterisk />
                        </Typography>
                        <Typography
                            component="h4"
                            className={classes.subTitleStyles}
                        >
                            Select the country where the production site is
                            located.
                        </Typography>
                        <StyledSelect
                            id="country"
                            name="country"
                            aria-label="Country"
                            options={countriesOptions || []}
                            value={inputCountry}
                            onChange={setInputCountry}
                            onBlur={handleCountryBlur}
                            className={classes.selectStyles}
                            styles={getSelectStyles(isCountryError)}
                            placeholder="Country"
                            isMulti={false}
                        />
                        {isCountryError && (
                            <div className={classes.errorWrapStyles}>
                                <InputErrorText />
                            </div>
                        )}
                    </div>
                    <hr className={classes.separator} />
                    <div
                        className={`${classes.sectionWrapStyles} ${classes.wrapStyles}`}
                    >
                        <div className={classes.rowContainerStyles}>
                            <Typography
                                component="h2"
                                className={`${classes.titleStyles} ${classes.marginRight}`}
                            >
                                Additional information
                            </Typography>
                            <Switch
                                color="primary"
                                onChange={onSwitchChange}
                                checked={showAdditionalInfo}
                                style={{ zIndex: 1 }}
                                className={classes.switchButton}
                                inputProps={{
                                    'data-testid':
                                        'switch-additional-info-fields',
                                }}
                            />
                        </div>
                        <Typography
                            component="h4"
                            className={classes.subTitleStyles}
                        >
                            Expand this section to add more data about your
                            production location, including product types, number
                            of workers, parent company and more.
                        </Typography>
                        {showAdditionalInfo && (
                            <>
                                <div
                                    className={`${classes.inputSectionWrapStyles} ${classes.wrapStyles}`}
                                >
                                    <Typography
                                        component="h2"
                                        className={classes.titleStyles}
                                    >
                                        Sector(s)
                                    </Typography>
                                    <Typography
                                        component="h4"
                                        className={classes.subTitleStyles}
                                    >
                                        Select the sector(s) that this location
                                        operates in. For example: Apparel,
                                        Electronics, Renewable Energy.
                                    </Typography>
                                    <StyledSelect
                                        id="sector"
                                        name="sector"
                                        aria-label="Select sector"
                                        options={
                                            mapDjangoChoiceTuplesToSelectOptions(
                                                mockedSectors,
                                            ) || []
                                        }
                                        value={sector}
                                        onChange={setSector}
                                        styles={getSelectStyles()}
                                        className={classes.selectStyles}
                                        placeholder="Select sector(s)"
                                    />
                                </div>
                                <div
                                    className={`${classes.inputSectionWrapStyles} ${classes.wrapStyles}`}
                                >
                                    <Typography
                                        component="h2"
                                        className={classes.titleStyles}
                                    >
                                        Product Type(s)
                                    </Typography>
                                    <Typography
                                        component="h4"
                                        className={classes.subTitleStyles}
                                    >
                                        Enter the type of products produced at
                                        this location. For example: Shirts,
                                        Laptops, Solar Panels.
                                    </Typography>

                                    <StyledSelect
                                        creatable
                                        name="product-type"
                                        value={productType}
                                        onChange={setProductType}
                                        placeholder="Enter product type(s)"
                                        aria-label="Enter product type(s)"
                                        styles={getSelectStyles()}
                                        className={classes.selectStyles}
                                        components={customSelectComponents}
                                    />
                                </div>
                                <div
                                    className={`${classes.inputSectionWrapStyles} ${classes.wrapStyles}`}
                                >
                                    <Typography
                                        component="h2"
                                        className={classes.titleStyles}
                                    >
                                        Location Type(s)
                                    </Typography>
                                    <Typography
                                        component="h4"
                                        className={classes.subTitleStyles}
                                    >
                                        Select or enter the location type(s) for
                                        this production location. For example:
                                        Final Product Assembly, Raw Materials
                                        Production or Processing, Office/HQ.
                                    </Typography>
                                    {enabledTaxonomy ? (
                                        <StyledSelect
                                            id="location_type"
                                            name="location-type"
                                            aria-label="Location type"
                                            options={mapFacilityTypeOptions(
                                                facilityProcessingTypeOptions ||
                                                    [],
                                                processingType || [],
                                            )}
                                            value={locationType}
                                            onChange={setLocationType}
                                            styles={getSelectStyles()}
                                            className={classes.selectStyles}
                                            placeholder="Select location type(s)"
                                        />
                                    ) : (
                                        <StyledSelect
                                            creatable
                                            name="location-type"
                                            value={locationType || []}
                                            onChange={setLocationType}
                                            placeholder="Enter location type(s)"
                                            aria-label="Location type"
                                            styles={getSelectStyles()}
                                            className={classes.selectStyles}
                                            components={customSelectComponents}
                                        />
                                    )}
                                </div>
                                <div
                                    className={`${classes.inputSectionWrapStyles} ${classes.wrapStyles}`}
                                >
                                    <Typography
                                        component="h2"
                                        className={classes.titleStyles}
                                    >
                                        Processing Type(s)
                                    </Typography>
                                    <Typography
                                        component="h4"
                                        className={classes.subTitleStyles}
                                    >
                                        Select or enter the type of processing
                                        activities that take place at this
                                        location. For example: Printing,
                                        Tooling, Assembly.
                                    </Typography>
                                    {enabledTaxonomy ? (
                                        <StyledSelect
                                            id="processing_type"
                                            name="processing-type"
                                            aria-label="Processing Type"
                                            options={mapProcessingTypeOptions(
                                                facilityProcessingTypeOptions ||
                                                    [],
                                                locationType || [],
                                            )}
                                            value={processingType}
                                            onChange={setProcessingType}
                                            styles={getSelectStyles()}
                                            className={classes.selectStyles}
                                            placeholder="Select processing type(s)"
                                        />
                                    ) : (
                                        <StyledSelect
                                            creatable
                                            name="processing-type"
                                            value={processingType || []}
                                            onChange={setProcessingType}
                                            placeholder="Enter processing type(s)"
                                            aria-label="Processing Type"
                                            styles={getSelectStyles()}
                                            className={classes.selectStyles}
                                            components={customSelectComponents}
                                        />
                                    )}
                                </div>
                                <div
                                    className={`${classes.inputSectionWrapStyles} ${classes.wrapStyles}`}
                                >
                                    <Typography
                                        component="h2"
                                        className={classes.titleStyles}
                                    >
                                        Number of Workers
                                    </Typography>
                                    <Typography
                                        component="h4"
                                        className={classes.subTitleStyles}
                                    >
                                        Enter a number or a range for the number
                                        of people employed at the location. For
                                        example: 100, 100-150.
                                    </Typography>
                                    <TextField
                                        id="number_of_workers"
                                        error={
                                            !isValidNumberOfWorkers(
                                                numberOfWorkers,
                                            )
                                        }
                                        variant="outlined"
                                        className={classes.textInputStyles}
                                        value={numberOfWorkers}
                                        onChange={e =>
                                            setNumberOfWorkers(
                                                e.target.value.trim(),
                                            )
                                        }
                                        placeholder="Enter the number of workers as a number or range"
                                        helperText={
                                            !isValidNumberOfWorkers(
                                                numberOfWorkers,
                                            ) && (
                                                <InputErrorText
                                                    text={getNumberOfWorkersValidationError(
                                                        numberOfWorkers,
                                                    )}
                                                />
                                            )
                                        }
                                        FormHelperTextProps={{
                                            className: classes.helperText,
                                        }}
                                        InputProps={{
                                            classes: {
                                                input: `
                                            ${
                                                !isValidNumberOfWorkers(
                                                    numberOfWorkers,
                                                ) && classes.errorStyle
                                            }`,
                                                notchedOutline:
                                                    classes.notchedOutlineStyles,
                                            },
                                        }}
                                        aria-label="Number of Workers"
                                    />
                                </div>
                                <div
                                    className={`${classes.inputSectionWrapStyles} ${classes.wrapStyles}`}
                                >
                                    <Typography
                                        component="h2"
                                        className={classes.titleStyles}
                                    >
                                        Parent Company
                                    </Typography>
                                    <Typography
                                        component="h4"
                                        className={classes.subTitleStyles}
                                    >
                                        Enter the company that holds majority
                                        ownership for this production.
                                    </Typography>
                                    <TextField
                                        id="parent_company"
                                        className={classes.textInputStyles}
                                        value={parentCompany}
                                        onChange={handleParentCompanyChange}
                                        placeholder="Enter the parent company"
                                        variant="outlined"
                                        aria-label="Parent company"
                                        InputProps={{
                                            classes: {
                                                notchedOutline:
                                                    classes.notchedOutlineStyles,
                                            },
                                        }}
                                    />
                                </div>
                            </>
                        )}
                    </div>
                    <div className={classes.buttonsContainerStyles}>
                        <Button
                            variant="outlined"
                            onClick={() => history.goBack()}
                            className={classes.goBackButtonStyles}
                        >
                            Go Back
                        </Button>
                        <FeatureFlag
                            flag={DISABLE_LIST_UPLOADING}
                            alternative={activeSubmitButton}
                        >
                            {maintenanceSubmitButton}
                        </FeatureFlag>
                    </div>
                </Paper>
            </div>
            {showProductionLocationDialog &&
            (pendingModerationEventData?.cleaned_data ||
                localStorage.getItem(moderationID) ||
                singleModerationEventItem?.cleaned_data) ? (
                <ProductionLocationDialog
                    data={
                        pendingModerationEventData?.cleaned_data ||
                        JSON.parse(localStorage.getItem(moderationID)) ||
                        singleModerationEventItem?.cleaned_data
                    }
                    osID={osID || singleModerationEventItem?.os_id}
                    innerWidth={innerWidth}
                    moderationStatus={
                        pendingModerationEventData?.status ||
                        singleModerationEventItem?.status ||
                        MODERATION_STATUSES_ENUM.PENDING
                    }
                    claimStatus={
                        singleProductionLocationData?.claim_status || null
                    }
                />
            ) : null}
        </>
    );
};

ProductionLocationInfo.defaultProps = {
    countriesOptions: null,
    facilityProcessingTypeOptions: null,
    pendingModerationEventData: null,
    pendingModerationEventFetching: false,
    pendingModerationEventError: null,
    singleModerationEventItem: null,
    singleModerationEventItemFetching: false,
    singleModerationEventItemError: null,
    singleProductionLocationFetching: false,
    singleProductionLocationError: null,
};

ProductionLocationInfo.propTypes = {
    countriesOptions: countryOptionsPropType,
    fetchCountries: func.isRequired,
    fetchModerationEvent: func.isRequired,
    fetchFacilityProcessingType: func.isRequired,
    handleCreateProductionLocation: func.isRequired,
    handleUpdateProductionLocation: func.isRequired,
    facilityProcessingTypeOptions: facilityProcessingTypeOptionsPropType,
    pendingModerationEventData: moderationEventsListItemPropType,
    pendingModerationEventFetching: bool,
    pendingModerationEventError: array,
    singleModerationEventItem: moderationEventsListItemPropType,
    singleModerationEventItemFetching: bool,
    singleModerationEventItemError: array,
    fetchProductionLocation: func.isRequired,
    singleProductionLocationData: productionLocationPropType.isRequired,
    singleProductionLocationFetching: bool,
    singleProductionLocationError: array,
    submitMethod: string.isRequired,
    classes: object.isRequired,
    innerWidth: number.isRequired,
    handleCleanupContributionRecord: func.isRequired,
    handleResetPendingModerationEvent: func.isRequired,
    handleResetSingleProductionLocation: func.isRequired,
    userHasSignedIn: bool.isRequired,
    fetchingSessionSignIn: bool.isRequired,
};

const mapStateToProps = ({
    filterOptions: {
        countries: { data: countriesOptions },
        facilityProcessingType: { data: facilityProcessingTypeOptions },
    },
    contributeProductionLocation: {
        pendingModerationEvent: {
            data: pendingModerationEventData,
            fetching: pendingModerationEventFetching,
            error: pendingModerationEventError,
        },
        singleProductionLocation: {
            data: singleProductionLocationData,
            fetching: singleProductionLocationFetching,
            error: singleProductionLocationError,
        },
    },
    dashboardContributionRecord: {
        singleModerationEvent: {
            data: singleModerationEventItem,
            fetching: singleModerationEventItemFetching,
            error: singleModerationEventItemError,
        },
    },
    ui: {
        window: { innerWidth },
    },
    auth: {
        user: { user },
        session: { fetching: fetchingSessionSignIn },
    },
}) => ({
    countriesOptions,
    facilityProcessingTypeOptions,
    pendingModerationEventData,
    pendingModerationEventFetching,
    pendingModerationEventError,
    singleModerationEventItem,
    singleModerationEventItemFetching,
    singleModerationEventItemError,
    singleProductionLocationData,
    singleProductionLocationFetching,
    singleProductionLocationError,
    innerWidth,
    userHasSignedIn: !user.isAnon,
    fetchingSessionSignIn,
});

function mapDispatchToProps(dispatch) {
    return {
        fetchCountries: () => dispatch(fetchCountryOptions()),
        fetchFacilityProcessingType: () =>
            dispatch(fetchFacilityProcessingTypeOptions()),
        handleCreateProductionLocation: data =>
            dispatch(createProductionLocation(data)),
        handleUpdateProductionLocation: (data, osID) =>
            dispatch(updateProductionLocation(data, osID)),
        fetchModerationEvent: moderationID =>
            dispatch(fetchSingleModerationEvent(moderationID)),
        fetchProductionLocation: osId =>
            dispatch(fetchProductionLocationByOsId(osId)),
        handleCleanupContributionRecord: () =>
            dispatch(cleanupContributionRecord()),
        handleResetPendingModerationEvent: () =>
            dispatch(resetPendingModerationEvent()),
        handleResetSingleProductionLocation: () =>
            dispatch(resetSingleProductionLocation()),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(productionLocationInfoStyles)(ProductionLocationInfo));
