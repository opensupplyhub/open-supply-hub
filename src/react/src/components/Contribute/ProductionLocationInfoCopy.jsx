import React, { useEffect, useState, useRef } from 'react';
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
import {
    useResetScrollPosition,
    useSingleLocationContributionForm,
} from '../../util/hooks';
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
    convertRangeField,
    updateStateFromData,
    getSelectStyles,
} from '../../util/util';

import FeatureFlag from '../FeatureFlag';
import RequiredAsterisk from '../RequiredAsterisk';
import StyledSelect from '../Filters/StyledSelect';
import RequireAuthNotice from '../RequireAuthNotice';
import StyledTooltip from '../StyledTooltip';

import InputErrorText from './InputErrorText';
import ProductionLocationDialog from './ProductionLocationDialog';
import PostContributionSubmitErrorNotification from './PostContributionSubmitErrorNotification/PostContributionSubmitErrorNotification';

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

    useResetScrollPosition(location);

    const [
        showProductionLocationDialog,
        setShowProductionLocationDialog,
    ] = useState(null);

    const [
        showPostSubmitErrorNotification,
        setShowPostSubmitErrorNotification,
    ] = useState(false);

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

    const contributionForm = useSingleLocationContributionForm(values => {
        setShowPostSubmitErrorNotification(false);
        handleProductionLocation(values, osID);
    });

    const fillAdditionalDataFields = () => {
        const fillSelectField = (key, formKey) => {
            updateStateFromData(singleProductionLocationData, key, value =>
                contributionForm.setFieldValue(formKey, value),
            );
        };

        fillSelectField('sector', 'sector');
        fillSelectField('product_type', 'productType');
        fillSelectField('location_type', 'locationType');
        fillSelectField('processing_type', 'processingType');
        contributionForm.setFieldValue(
            'numberOfWorkers',
            convertRangeField(singleProductionLocationData.number_of_workers) ??
                '',
        );
        // contributionForm.setFieldValue(
        //     'parentCompany',
        //     singleProductionLocationData.parent_company ?? '',
        // );
    };

    const resetAdditionalDataFields = () => {
        contributionForm.setValues({
            ...contributionForm.values,
            sector: '',
            productType: [],
            locationType: null,
            processingType: null,
            numberOfWorkers: '',
            parentCompany: '',
        });
    };

    const customSelectComponents = { DropdownIndicator: null };

    const instructionExtraMessage =
        submitMethod === 'PATCH'
            ? 'These fields are pre-filled with the data from your search, but you can edit them.'
            : '';
    const submitButtonText = submitMethod === 'POST' ? 'Submit' : 'Update';

    const [showAdditionalInfo, setShowAdditionalInfo] = useState(false);
    const onSwitchChange = () => {
        setShowAdditionalInfo(prevShowAdditionalInfo => {
            const newShowAdditionalInfo = !prevShowAdditionalInfo;
            if (newShowAdditionalInfo) {
                fillAdditionalDataFields();
            } else {
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
            contributionForm.setValues({
                ...contributionForm.values,
                name: singleProductionLocationData.name ?? '',
                address: singleProductionLocationData.address ?? '',
                country: singleProductionLocationData.country
                    ? {
                          value: singleProductionLocationData?.country.alpha_2,
                          label: singleProductionLocationData?.country.name,
                      }
                    : null,
            });
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
            setShowPostSubmitErrorNotification(true);
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

    console.log('contributionForm.isValid');
    console.log(contributionForm.isValid);
    const activeSubmitButton = (
        <Button
            color="secondary"
            variant="contained"
            onClick={contributionForm.handleSubmit}
            className={classes.submitButtonStyles}
            disabled={!contributionForm.isValid}
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
                    {/* <form onSubmit={contributionForm.handleSubmit}> */}
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
                            {...contributionForm.getFieldProps('name')}
                            placeholder="Enter the name"
                            variant="outlined"
                            aria-label="Enter the name"
                            InputProps={{
                                classes: {
                                    input: `
                                    ${
                                        contributionForm.touched.name &&
                                        contributionForm.errors.name &&
                                        classes.errorStyle
                                    }`,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                            helperText={
                                contributionForm.touched.name &&
                                contributionForm.errors.name && (
                                    <InputErrorText
                                        text={contributionForm.errors.name}
                                    />
                                )
                            }
                            FormHelperTextProps={{
                                className: classes.helperText,
                            }}
                            error={
                                contributionForm.touched.name &&
                                !!contributionForm.errors.name
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
                            {...contributionForm.getFieldProps('address')}
                            placeholder="Enter the full address"
                            variant="outlined"
                            aria-label="Enter the address"
                            InputProps={{
                                classes: {
                                    input: `${classes.searchInputStyles}
                                ${
                                    contributionForm.touched.address &&
                                    contributionForm.errors.address &&
                                    classes.errorStyle
                                }`,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                            helperText={
                                contributionForm.touched.address &&
                                contributionForm.errors.address && (
                                    <InputErrorText
                                        text={contributionForm.errors.address}
                                    />
                                )
                            }
                            FormHelperTextProps={{
                                className: classes.helperText,
                            }}
                            error={
                                contributionForm.touched.address &&
                                !!contributionForm.errors.address
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
                            name="Country"
                            aria-label="Country"
                            options={countriesOptions || []}
                            value={contributionForm.values.country}
                            onChange={value =>
                                contributionForm.setFieldValue('country', value)
                            }
                            onBlur={() =>
                                contributionForm.setFieldTouched(
                                    'country',
                                    true,
                                )
                            }
                            className={classes.selectStyles}
                            styles={getSelectStyles(
                                contributionForm.touched.country &&
                                    !!contributionForm.errors.country,
                            )}
                            placeholder="Country"
                            isMulti={false}
                        />
                        {contributionForm.touched.country &&
                            contributionForm.errors.country && (
                                <div className={classes.errorWrapStyles}>
                                    <InputErrorText
                                        text={contributionForm.errors.country}
                                    />
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
                                        value={contributionForm.values.sector}
                                        onChange={value =>
                                            contributionForm.setFieldValue(
                                                'sector',
                                                value,
                                            )
                                        }
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
                                        name="Product Type"
                                        value={
                                            contributionForm.values.productType
                                        }
                                        onChange={value =>
                                            contributionForm.setFieldValue(
                                                'productType',
                                                value,
                                            )
                                        }
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
                                        Select the location type(s) for this
                                        production location. For example: Final
                                        Product Assembly, Raw Materials
                                        Production or Processing, Office/HQ.
                                    </Typography>
                                    <StyledSelect
                                        id="location_type"
                                        name="Location type"
                                        aria-label="Location type"
                                        options={mapFacilityTypeOptions(
                                            facilityProcessingTypeOptions || [],
                                            contributionForm.values
                                                .processingType || [],
                                        )}
                                        value={
                                            contributionForm.values.locationType
                                        }
                                        onChange={value =>
                                            contributionForm.setFieldValue(
                                                'locationType',
                                                value,
                                            )
                                        }
                                        styles={getSelectStyles()}
                                        className={classes.selectStyles}
                                        placeholder="Select location type(s)"
                                    />
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
                                        Select the type of processing activities
                                        that take place at this location. For
                                        example: Printing, Tooling, Assembly.
                                    </Typography>
                                    <StyledSelect
                                        id="processing_type"
                                        name="Processing Type"
                                        aria-label="Processing Type"
                                        options={mapProcessingTypeOptions(
                                            facilityProcessingTypeOptions || [],
                                            contributionForm.values
                                                .locationType || [],
                                        )}
                                        value={
                                            contributionForm.values
                                                .processingType
                                        }
                                        onChange={value =>
                                            contributionForm.setFieldValue(
                                                'processingType',
                                                value,
                                            )
                                        }
                                        styles={getSelectStyles()}
                                        className={classes.selectStyles}
                                    />
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
                                            // contributionForm.touched
                                            //     .numberOfWorkers &&
                                            !!contributionForm.errors
                                                .numberOfWorkers
                                        }
                                        variant="outlined"
                                        className={classes.textInputStyles}
                                        {...contributionForm.getFieldProps(
                                            'numberOfWorkers',
                                        )}
                                        placeholder="Enter the number of workers as a number or range"
                                        helperText={
                                            contributionForm.errors
                                                .numberOfWorkers && (
                                                <InputErrorText
                                                    text={
                                                        contributionForm.errors
                                                            .numberOfWorkers
                                                    }
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
                                                contributionForm.errors
                                                    .numberOfWorkers &&
                                                classes.errorStyle
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
                                        {...contributionForm.getFieldProps(
                                            'parentCompany',
                                        )}
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
                    {showPostSubmitErrorNotification && (
                        <PostContributionSubmitErrorNotification
                            showNotification={
                                setShowPostSubmitErrorNotification
                            }
                            errorObj={pendingModerationEventError}
                        />
                    )}
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
                    {/* </form> */}
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
    pendingModerationEventError: object,
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
