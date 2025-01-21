import React, { useEffect, useState, useRef } from 'react';
import { useLocation, useParams, useHistory } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import { func, object, string } from 'prop-types';
import { connect } from 'react-redux';
import { toast } from 'react-toastify';
import { isEmpty } from 'lodash';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';
import TextField from '@material-ui/core/TextField';
import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import ArrowDropDownIcon from '@material-ui/icons/ArrowDropDown';
import ArrowDropUpIcon from '@material-ui/icons/ArrowDropUp';
import StyledSelect from '../Filters/StyledSelect';
import { productionLocationInfoStyles } from '../../util/styles';
import {
    countryOptionsPropType,
    facilityProcessingTypeOptionsPropType,
    moderationEventsListItemPropType,
    productionLocationPropType,
} from '../../util/propTypes';
import {
    fetchCountryOptions,
    fetchFacilityProcessingTypeOptions,
} from '../../actions/filterOptions';
import {
    createProductionLocation,
    updateProductionLocation,
    fetchProductionLocationByOsId,
} from '../../actions/contributeProductionLocation';
import { fetchSingleModerationEvent } from '../../actions/dashboardContributionRecord';
import InputErrorText from './InputErrorText';
import {
    mapDjangoChoiceTuplesToSelectOptions,
    mapFacilityTypeOptions,
    mapProcessingTypeOptions,
    isValidNumberOfWorkers,
    convertRangeField,
    updateStateFromData,
} from '../../util/util';
import { mockedSectors } from '../../util/constants';
import COLOURS from '../../util/COLOURS';
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
    pendingModerationEvent,
    singleModerationEventItem,
    fetchProductionLocation,
    singleProductionLocationData,
}) => {
    const location = useLocation();
    const history = useHistory();
    const { moderationID, osID } = useParams();

    const queryParams = new URLSearchParams(location.search);
    const nameInQuery = queryParams.get('name');
    const addressInQuery = queryParams.get('address');
    const countryInQuery = queryParams.get('country');
    const [isExpanded, setIsExpanded] = useState(false);
    const [inputName, setInputName] = useState(nameInQuery ?? '');
    const [inputAddress, setInputAddress] = useState(addressInQuery ?? '');
    const [inputCountry, setInputCountry] = useState(null);
    const [nameTouched, setNameTouched] = useState(false);
    const [addressTouched, setAddressTouched] = useState(false);
    const [sector, setSector] = useState('');
    const [productType, setProductType] = useState([]);
    const [locationType, setLocationType] = useState(null);
    const [processingType, setProcessingType] = useState(null);
    const [numberOfWorkers, setNumberOfWorkers] = useState('');
    const [parentCompany, setParentCompany] = useState([]);
    const customSelectComponents = { DropdownIndicator: null };

    const selectStyles = {
        control: provided => ({
            ...provided,
            height: '56px',
            borderRadius: '0',
            '&:focus,&:active,&:focus-within': {
                borderColor: COLOURS.PURPLE,
                boxShadow: `inset 0 0 0 1px ${COLOURS.PURPLE}`,
                transition: 'box-shadow 0.2s',
            },
            '&:hover': {
                borderColor: 'black',
            },
        }),
    };

    const [
        showProductionLocationDialog,
        setShowProductionLocationDialog,
    ] = useState(false);

    const toggleExpand = () => {
        setIsExpanded(!isExpanded);
    };
    const handleNameChange = event => {
        setNameTouched(true);
        setInputName(event.target.value);
    };
    const handleAddressChange = event => {
        setAddressTouched(true);
        setInputAddress(event.target.value);
    };
    const handleProductionLocation =
        submitMethod === 'POST'
            ? handleCreateProductionLocation
            : data => handleUpdateProductionLocation(data, osID);
    const submitButtonText = submitMethod === 'POST' ? 'Submit' : 'Update';

    useEffect(() => {
        if (submitMethod === 'PATCH' && osID) {
            fetchProductionLocation(osID);
        }
    }, [submitMethod]);

    useEffect(() => {
        if (singleProductionLocationData && osID) {
            setInputName(singleProductionLocationData.name ?? '');
            setInputAddress(singleProductionLocationData.address ?? '');
            setNumberOfWorkers(
                convertRangeField(
                    singleProductionLocationData.number_of_workers,
                ) ?? '',
            );
            if (singleProductionLocationData.country) {
                setInputCountry({
                    value: singleProductionLocationData?.country.alpha_2,
                    label: singleProductionLocationData?.country.name,
                });
            }
            updateStateFromData(
                singleProductionLocationData,
                'sector',
                setSector,
            );
            updateStateFromData(
                singleProductionLocationData,
                'product_type',
                setProductType,
            );
            updateStateFromData(
                singleProductionLocationData,
                'location_type',
                setLocationType,
            );
            updateStateFromData(
                singleProductionLocationData,
                'processing_type',
                setProcessingType,
            );
            updateStateFromData(
                singleProductionLocationData,
                'parent_company',
                setParentCompany,
            );
        }
    }, [singleProductionLocationData]);

    const prevModerationIDRef = useRef();
    useEffect(() => {
        if (prevModerationIDRef.current !== moderationID) {
            if (isEmpty(singleModerationEventItem)) {
                fetchModerationEvent(moderationID);
            }
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
        if (pendingModerationEvent?.data?.cleaned_data) {
            toast('Your contribution has been added successfully!');
            if (pendingModerationEvent.data?.moderation_id) {
                localStorage.setItem(
                    pendingModerationEvent.data.moderation_id,
                    JSON.stringify(pendingModerationEvent?.data?.cleaned_data),
                );
                history.push({
                    pathname: `${location.pathname}${pendingModerationEvent.data.moderation_id}`,
                    search: '',
                });
            }
        }
    }, [pendingModerationEvent]);

    useEffect(() => {
        if (!isEmpty(singleModerationEventItem) && moderationID) {
            localStorage.removeItem(moderationID);
        }
        setShowProductionLocationDialog(true);
    }, [singleModerationEventItem, pendingModerationEvent]);

    useEffect(() => {
        // Force trailing slash in URL to prevent broken UX scenarios
        if (location.pathname && !location.pathname.endsWith('/')) {
            history.replace(`${location.pathname}/`);
        }

        const unListen = history.listen(appLocation => {
            if (
                appLocation.pathname ===
                    '/contribute/production-location/info/' ||
                appLocation.pathname ===
                    `/contribute/production-location/${osID}/info/`
            ) {
                setShowProductionLocationDialog(false);
            }
        });

        return () => {
            unListen();
        };
    }, [location.pathname, history, osID]);

    return (
        <>
            <div className={classes.mainContainerStyles}>
                <Typography component="h1" className={classes.headerStyles}>
                    Production Location Information
                </Typography>
                <Typography className={classes.instructionStyles}>
                    Use the form below to edit the name, address, and country
                    for your production location. These fields are pre-filled
                    with the data from your search, but you can edit them.
                </Typography>
                <Paper className={classes.infoWrapStyles}>
                    <div
                        className={`${classes.inputSectionWrapStyles} ${classes.wrapStyles}`}
                    >
                        <Typography
                            component="h2"
                            className={classes.titleStyles}
                        >
                            Location Name
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
                            placeholder="Enter the name"
                            variant="outlined"
                            aria-label="Enter the name"
                            InputProps={{
                                classes: {
                                    input: `
                                    ${
                                        nameTouched &&
                                        !isEmpty(inputName) &&
                                        classes.errorStyle
                                    }`,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                            helperText={
                                nameTouched &&
                                !isEmpty(inputName) && <InputErrorText />
                            }
                            FormHelperTextProps={{
                                className: classes.helperText,
                            }}
                            error={nameTouched && !isEmpty(inputName)}
                        />
                    </div>
                    <div
                        className={`${classes.inputSectionWrapStyles} ${classes.wrapStyles}`}
                    >
                        <Typography
                            component="h2"
                            className={classes.titleStyles}
                        >
                            Address
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
                            placeholder="Enter the full address"
                            variant="outlined"
                            aria-label="Enter the address"
                            InputProps={{
                                classes: {
                                    input: `${classes.searchInputStyles}
                                ${
                                    addressTouched &&
                                    !isEmpty(inputAddress) &&
                                    classes.errorStyle
                                }`,
                                    notchedOutline:
                                        classes.notchedOutlineStyles,
                                },
                            }}
                            helperText={
                                addressTouched &&
                                !isEmpty(inputAddress) && <InputErrorText />
                            }
                            FormHelperTextProps={{
                                className: classes.helperText,
                            }}
                            error={addressTouched && !isEmpty(inputAddress)}
                        />
                    </div>
                    <div
                        className={`${classes.inputSectionWrapStyles} ${classes.wrapStyles}`}
                    >
                        <Typography
                            component="h2"
                            className={classes.titleStyles}
                        >
                            Country
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
                            value={inputCountry}
                            onChange={setInputCountry}
                            className={classes.selectStyles}
                            styles={selectStyles}
                            placeholder="Country"
                            isMulti={false}
                        />
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
                            <IconButton onClick={toggleExpand}>
                                {isExpanded ? (
                                    <ArrowDropUpIcon />
                                ) : (
                                    <ArrowDropDownIcon />
                                )}
                            </IconButton>
                        </div>
                        <Typography
                            component="h4"
                            className={classes.subTitleStyles}
                        >
                            Expand this section to add more data about your
                            production location, including product types, number
                            of workers, parent company and more.
                        </Typography>
                        {isExpanded && (
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
                                        styles={selectStyles}
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
                                        value={productType}
                                        onChange={setProductType}
                                        placeholder="Enter product type(s)"
                                        aria-label="Enter product type(s)"
                                        styles={selectStyles}
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
                                            processingType || [],
                                        )}
                                        value={locationType}
                                        onChange={setLocationType}
                                        styles={selectStyles}
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
                                            locationType || [],
                                        )}
                                        value={processingType}
                                        onChange={setProcessingType}
                                        styles={selectStyles}
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
                                            !isValidNumberOfWorkers(
                                                numberOfWorkers,
                                            )
                                        }
                                        variant="outlined"
                                        className={classes.textInputStyles}
                                        value={numberOfWorkers}
                                        onChange={e =>
                                            setNumberOfWorkers(e.target.value)
                                        }
                                        placeholder="Enter the number of workers as a number or range"
                                        helperText={
                                            !isValidNumberOfWorkers(
                                                numberOfWorkers,
                                            ) && (
                                                <InputErrorText text="Enter the number of workers as a number or range" />
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
                                    <StyledSelect
                                        creatable
                                        name="Parent company"
                                        value={parentCompany}
                                        onChange={setParentCompany}
                                        placeholder="Enter the parent company"
                                        aria-label="Parent company"
                                        styles={selectStyles}
                                        className={classes.selectStyles}
                                        components={customSelectComponents}
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
                        <Button
                            color="secondary"
                            variant="contained"
                            onClick={() => {
                                const data = {
                                    name: inputName,
                                    address: inputAddress,
                                    country: inputCountry,
                                    sector,
                                    productType,
                                    locationType,
                                    processingType,
                                    numberOfWorkers,
                                    parentCompany,
                                };
                                handleProductionLocation(data, osID);
                            }}
                            className={classes.submitButtonStyles}
                        >
                            {submitButtonText}
                        </Button>
                    </div>
                </Paper>
            </div>
            {showProductionLocationDialog &&
            (pendingModerationEvent?.data?.cleaned_data ||
                localStorage.getItem(moderationID) ||
                singleModerationEventItem?.cleaned_data) ? (
                <ProductionLocationDialog
                    data={
                        pendingModerationEvent?.data?.cleaned_data ||
                        JSON.parse(localStorage.getItem(moderationID)) ||
                        singleModerationEventItem?.cleaned_data
                    }
                    osID={osID}
                />
            ) : null}
        </>
    );
};

ProductionLocationInfo.defaultProps = {
    countriesOptions: null,
    facilityProcessingTypeOptions: null,
    pendingModerationEvent: null,
    singleModerationEventItem: null,
};

ProductionLocationInfo.propTypes = {
    countriesOptions: countryOptionsPropType,
    fetchCountries: func.isRequired,
    fetchModerationEvent: func.isRequired,
    fetchFacilityProcessingType: func.isRequired,
    handleCreateProductionLocation: func.isRequired,
    handleUpdateProductionLocation: func.isRequired,
    facilityProcessingTypeOptions: facilityProcessingTypeOptionsPropType,
    pendingModerationEvent: moderationEventsListItemPropType,
    singleModerationEventItem: moderationEventsListItemPropType,
    fetchProductionLocation: func.isRequired,
    singleProductionLocationData: productionLocationPropType.isRequired,
    submitMethod: string.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    filterOptions: {
        countries: { data: countriesOptions },
        facilityProcessingType: { data: facilityProcessingTypeOptions },
    },
    contributeProductionLocation: { pendingModerationEvent },
    dashboardContributionRecord: {
        singleModerationEvent: { data: singleModerationEventItem },
    },
    contributeProductionLocation: {
        singleProductionLocation: { data: singleProductionLocationData },
    },
}) => ({
    countriesOptions,
    facilityProcessingTypeOptions,
    pendingModerationEvent,
    singleModerationEventItem,
    singleProductionLocationData,
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
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(productionLocationInfoStyles)(ProductionLocationInfo));
