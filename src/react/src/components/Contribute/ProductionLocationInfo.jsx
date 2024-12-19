import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import { bool, string, func, object } from 'prop-types';
import { connect } from 'react-redux';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import CircularProgress from '@material-ui/core/CircularProgress';
import StyledSelect from '../Filters/StyledSelect';
import CustomDropdownIndicator from '../../components/Filters/CustomReactSelectComponents/CustomDropdownIndicator';
import { productionLocationInfoStyles } from '../../util/styles';
import {
    countryOptionsPropType,
    facilityProcessingTypeOptionsPropType,
    numberOfWorkerOptionsPropType,
    parentCompanyOptionsPropType,
} from '../../util/propTypes';
import {
    fetchCountryOptions,
    fetchFacilityProcessingTypeOptions,
    fetchNumberOfWorkersOptions,
    fetchParentCompanyOptions,
} from '../../actions/filterOptions';
import InputHelperText from './InputHelperText';
import {
    mapDjangoChoiceTuplesToSelectOptions,
    mapFacilityTypeOptions,
    mapProcessingTypeOptions,
} from '../../util/util';

const mockedSectors = [
    ['Electronics', 'Electronics'],
    ['Accommodation', 'Accommodation'],
    ['Aerospace', 'Aerospace'],
    ['Agriculture', 'Agriculture'],
    ['Air Transportation', 'Air Transportation'],
    ['Allied Products', 'Allied Products'],
    ['Animal Production', 'Animal Production'],
    ['Apparel', 'Apparel'],
    ['Apparel Accessories', 'Apparel Accessories'],
    ['Appliances', 'Appliances'],
    ['Aquaculture', 'Aquaculture'],
    ['Archives', 'Archives'],
    ['Arts', 'Arts'],
    ['Arts & Entertainment', 'Arts & Entertainment'],
    ['Automotive', 'Automotive'],
    ['Automotive Parts', 'Automotive Parts'],
    ['Banking', 'Banking'],
    ['Beauty Products', 'Beauty Products'],
    ['Beverages', 'Beverages'],
    ['Biotechnology', 'Biotechnology'],
    ['Books', 'Books'],
    ['Building Construction', 'Building Construction'],
    ['Building Materials', 'Building Materials'],
    ['Chemicals', 'Chemicals'],
    ['Civics', 'Civics'],
    ['Civil Engineering Construction', 'Civil Engineering Construction'],
    ['Coal', 'Coal'],
    ['Commodities', 'Commodities'],
    ['Components', 'Components'],
    ['Computers', 'Computers'],
    ['Computing Infrastructure', 'Computing Infrastructure'],
    ['Construction', 'Construction'],
    ['Consumer Products', 'Consumer Products'],
    ['Crop Production', 'Crop Production'],
    ['Durable Goods', 'Durable Goods'],
    ['Educational Services', 'Educational Services'],
    ['Electrical Devices', 'Electrical Devices'],
    ['Electricity', 'Electricity'],
    ['Electronic Product Manufacturing', 'Electronic Product Manufacturing'],
    ['Energy', 'Energy'],
    ['Energy Production & Utilities', 'Energy Production & Utilities'],
    ['Entertainment', 'Entertainment'],
    ['Equipment', 'Equipment'],
    ['Farming', 'Farming'],
    ['Finance', 'Finance'],
    ['Financial Services', 'Financial Services'],
    ['Fishing', 'Fishing'],
    ['Food', 'Food'],
    ['Food & Beverage', 'Food & Beverage'],
    ['Food Industry', 'Food Industry'],
    ['Food Manufacturing', 'Food Manufacturing'],
    ['Footwear', 'Footwear'],
    ['Forestry', 'Forestry'],
    ['Furniture', 'Furniture'],
    ['Garden Tools', 'Garden Tools'],
    ['Gas', 'Gas'],
    ['General Merchandise', 'General Merchandise'],
    ['Ground Passenger Transportation', 'Ground Passenger Transportation'],
    ['Hard Goods', 'Hard Goods'],
    ['Health', 'Health'],
    ['Healthcare', 'Healthcare'],
    ['Hobby', 'Hobby'],
    ['Home Accessories', 'Home Accessories'],
    ['Home Furnishings', 'Home Furnishings'],
    ['Hospitals', 'Hospitals'],
    ['Home Textiles', 'Home Textiles'],
    ['Hunting', 'Hunting'],
    ['Information', 'Information'],
    ['International Affairs', 'International Affairs'],
    ['Jewelry', 'Jewelry'],
    ['Leather', 'Leather'],
    ['Logging', 'Logging'],
    ['Machinery Manufacturing', 'Machinery Manufacturing'],
    ['Maintenance', 'Maintenance'],
    ['Manufacturing', 'Manufacturing'],
    ['Material Production', 'Material Production'],
    ['Medical Equipment & Services', 'Medical Equipment & Services'],
    ['Merchant Wholesalers', 'Merchant Wholesalers'],
    ['Metal Manufacturing', 'Metal Manufacturing'],
    ['Mining', 'Mining'],
    ['Multi-Category', 'Multi-Category'],
    ['Musical Instruments', 'Musical Instruments'],
    ['Nondurable Goods', 'Nondurable Goods'],
    ['Nursing', 'Nursing'],
    ['Oil & Gas', 'Oil & Gas'],
    ['Paper Products', 'Paper Products'],
    ['Parts Dealers', 'Parts Dealers'],
    ['Personal Care Products', 'Personal Care Products'],
    ['Pharmaceuticals', 'Pharmaceuticals'],
    ['Pipeline Transportation', 'Pipeline Transportation'],
    ['Plastics', 'Plastics'],
    ['Printing', 'Printing'],
    ['Professional Services', 'Professional Services'],
    ['Quarrying', 'Quarrying'],
    ['Rail Transportation', 'Rail Transportation'],
    ['Recreation', 'Recreation'],
    ['Renewable Energy', 'Renewable Energy'],
    ['Renting', 'Renting'],
    ['Repair', 'Repair'],
    ['Rubber Products', 'Rubber Products'],
    ['Solar Energy', 'Solar Energy'],
    ['Research', 'Research'],
    ['Specialty Trade Contractors', 'Specialty Trade Contractors'],
    ['Sports Equipment', 'Sports Equipment'],
    ['Sporting Goods', 'Sporting Goods'],
    ['Storage', 'Storage'],
    ['Supplies Dealers', 'Supplies Dealers'],
    ['Technical Services', 'Technical Services'],
    ['Technology', 'Technology'],
    ['Telecommunications', 'Telecommunications'],
    ['Textiles', 'Textiles'],
    ['Tobacco Products', 'Tobacco Products'],
    ['Toys', 'Toys'],
    ['Transportation Equipment', 'Transportation Equipment'],
    ['Trucking', 'Trucking'],
    ['Utilities', 'Utilities'],
    ['Water Utilities', 'Water Utilities'],
    ['Warehousing', 'Warehousing'],
    ['Wholesale Trade', 'Wholesale Trade'],
    ['Wood Products', 'Wood Products'],
    ['Consumer Electronics', 'Consumer Electronics'],
    ['Home', 'Home'],
    ['Maritime Transportation', 'Maritime Transportation'],
    [
        'Technical and Scientific Activities',
        'Technical and Scientific Activities',
    ],
    ['Waste Management', 'Waste Management'],
    ['Recycling', 'Recycling'],
    ['Pets', 'Pets'],
    ['Packaging', 'Packaging'],
];

const ProductionLocationInfo = ({
    classes,
    countriesOptions,
    fetchCountries,
    facilityProcessingTypeOptions,
    fetching,
    error,
    fetchFacilityProcessingType,
    numberOfWorkersOptions,
    fetchNumberOfWorkers,
    parentCompanyOptions,
    fetchParentCompanies,
}) => {
    const location = useLocation();
    const defaultCountryOption = {
        label: 'Country',
        value: '',
    };

    const queryParams = new URLSearchParams(location.search);
    const nameInQuery = queryParams.get('name');
    const addressInQuery = queryParams.get('address');
    const countryInQuery = queryParams.get('country');
    const [isExpanded, setIsExpanded] = useState(false);
    const [inputName, setInputName] = useState(nameInQuery ?? '');
    const [inputAddress, setInputAddress] = useState(addressInQuery ?? '');
    const [inputCountry, setInputCountry] = useState(defaultCountryOption);
    const [nameTouched, setNameTouched] = useState(false);
    const [addressTouched, setAddressTouched] = useState(false);
    const [sector, setSector] = useState('');
    const [productType, setProductType] = useState([]);
    const [locationType, setLocationType] = useState(null);
    const [processingType, setProcessingType] = useState(null);
    const [numberOfWorkers, setNumberOfWorkers] = useState(null);
    const [parentCompany, setParentCompany] = useState([]);

    const selectStyles = {
        control: provided => ({
            ...provided,
            height: '56px',
        }),
    };
    const validate = val => val.length > 0;
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
    const handleCountryChange = event =>
        setInputCountry(event || defaultCountryOption);

    const handleSectorChange = event => setSector(event);
    const handleProductType = event => setProductType(event);
    const handleProcessingType = event => setProcessingType(event);
    const handleLocationType = event => setLocationType(event);
    const handleParentCompany = event => setParentCompany(event);

    const handleNumberOfWorkers = event => setNumberOfWorkers(event);

    useEffect(() => {
        if (!countriesOptions) {
            fetchCountries();
        }
    }, [countriesOptions, fetchCountries]);

    useEffect(() => {
        if (countriesOptions && validate(countryInQuery)) {
            const prefilledCountry = countriesOptions.filter(
                el => el.value === countryInQuery,
            );

            handleCountryChange(prefilledCountry[0]);
        }
    }, [countriesOptions]);

    useEffect(() => {
        if (!facilityProcessingTypeOptions) {
            fetchFacilityProcessingType();
        }
    }, [facilityProcessingTypeOptions, fetchFacilityProcessingType]);

    useEffect(() => {
        if (!numberOfWorkersOptions) {
            fetchNumberOfWorkers();
        }
    }, [numberOfWorkersOptions, fetchNumberOfWorkers]);

    useEffect(() => {
        if (!parentCompanyOptions) {
            fetchParentCompanies();
        }
    }, [parentCompanyOptions, fetchParentCompanies]);

    if (fetching) {
        return <CircularProgress />;
    }

    if (error) {
        return (
            <Typography variant="body2" className={classes.errorStyle}>
                {error}
            </Typography>
        );
    }

    return (
        <div className={classes.mainContainerStyles}>
            <Typography component="h1" className={classes.headerStyles}>
                Production Location Information
            </Typography>
            <Typography className={classes.instructionStyles}>
                Use the form below to edit the name, address, and country for
                your production location. These fields are pre-filled with the
                data from your search, but you can edit them.
            </Typography>
            <Paper className={classes.infoWrapStyles}>
                <div className={classes.inputSectionWrapStyles}>
                    <Typography component="h2" className={classes.titleStyles}>
                        Location Name
                    </Typography>
                    <Typography
                        component="h4"
                        className={classes.subTitleStyles}
                    >
                        Enter the name of the production location that you are
                        uploading.
                    </Typography>
                    <TextField
                        id="name"
                        className={classes.textInputStyles}
                        value={inputName ?? ''}
                        onChange={handleNameChange}
                        placeholder="Enter the name"
                        variant="outlined"
                        aria-label="Enter the name"
                        InputProps={{
                            classes: {
                                input: `${classes.searchInputStyles}
                                    ${
                                        nameTouched &&
                                        !validate(inputName) &&
                                        classes.errorStyle
                                    }`,
                                notchedOutline: classes.notchedOutlineStyles,
                            },
                            inputProps: {
                                type: 'text',
                            },
                        }}
                        helperText={
                            nameTouched &&
                            !validate(inputName) && <InputHelperText />
                        }
                        error={nameTouched && !validate(inputName)}
                    />
                </div>
                <div className={classes.inputSectionWrapStyles}>
                    <Typography component="h2" className={classes.titleStyles}>
                        Address
                    </Typography>
                    <Typography
                        component="h4"
                        className={classes.subTitleStyles}
                    >
                        Enter the address of the production location. We will
                        use this to plot the location on a map.
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
                                    !validate(inputAddress) &&
                                    classes.errorStyle
                                }`,
                                notchedOutline: classes.notchedOutlineStyles,
                            },
                            inputProps: {
                                type: 'text',
                            },
                        }}
                        helperText={
                            addressTouched &&
                            !validate(inputAddress) && <InputHelperText />
                        }
                        error={addressTouched && !validate(inputAddress)}
                    />
                </div>
                <div className={classes.inputSectionWrapStyles}>
                    <Typography component="h2" className={classes.titleStyles}>
                        Country
                    </Typography>
                    <Typography
                        component="h4"
                        className={classes.subTitleStyles}
                    >
                        Enter the country where the production site is located.
                    </Typography>
                    <StyledSelect
                        id="countries"
                        name="Country"
                        aria-label="Country"
                        label={null}
                        options={countriesOptions || []}
                        value={inputCountry}
                        onChange={handleCountryChange}
                        className={`basic-multi-select notranslate ${classes.selectStyles}`}
                        styles={selectStyles}
                        placeholder="Country"
                        isMulti={false}
                    />
                </div>
                <hr className={classes.separator} />
                <div className={classes.inputSectionWrapStyles}>
                    <div
                        className={classes.rowContainerStyles}
                        onClick={toggleExpand}
                        onKeyDown={toggleExpand}
                        role="button"
                        styling="link"
                        tabIndex={0}
                    >
                        <Typography
                            component="h2"
                            className={`${classes.titleStyles} ${classes.marginRight}`}
                        >
                            Additional information
                        </Typography>
                        <CustomDropdownIndicator arrowDown={!isExpanded} />
                    </div>
                    <Typography
                        component="h4"
                        className={classes.subTitleStyles}
                    >
                        Expand this section to add more data, including product
                        types, number of workers, parent company and more.
                    </Typography>
                    {isExpanded && (
                        <>
                            <div className={classes.inputSectionWrapStyles}>
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
                                    Enter the type of products produced at this
                                    location. For example: Shirts, Laptops,
                                    Solar Panels.
                                </Typography>
                                <StyledSelect
                                    id="sector"
                                    name="sector"
                                    aria-label="Select sector"
                                    label={null}
                                    options={
                                        mapDjangoChoiceTuplesToSelectOptions(
                                            mockedSectors,
                                        ) || []
                                    }
                                    value={sector}
                                    onChange={handleSectorChange}
                                    className={`basic-multi-select notranslate ${classes.selectStyles}`}
                                    styles={selectStyles}
                                    placeholder="Select"
                                    isMulti={!false}
                                />
                            </div>
                            <div className={classes.inputSectionWrapStyles}>
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
                                    Enter the type of products produced at this
                                    location. For example: Shirts, Laptops,
                                    Solar Panels.
                                </Typography>
                                <StyledSelect
                                    creatable
                                    label={null}
                                    name="Product Type"
                                    value={productType}
                                    onChange={handleProductType}
                                    placeholder="Enter product type(s)"
                                    aria-label="Enter product type(s)"
                                    className={`basic-multi-select notranslate ${classes.selectStyles}`}
                                    styles={selectStyles}
                                />
                            </div>
                            <div className={classes.inputSectionWrapStyles}>
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
                                    this production location. For example: Final
                                    Product Assembly, Raw Materials Production
                                    or Processing, Office/HQ.
                                </Typography>
                                <StyledSelect
                                    id="location_type"
                                    name="Location type"
                                    aria-label="Location type"
                                    label={null}
                                    options={mapFacilityTypeOptions(
                                        facilityProcessingTypeOptions || [],
                                        processingType || [],
                                    )}
                                    value={locationType}
                                    onChange={handleLocationType}
                                    className={`basic-multi-select notranslate ${classes.selectStyles}`}
                                    styles={selectStyles}
                                    placeholder="Select"
                                />
                            </div>
                            <div className={classes.inputSectionWrapStyles}>
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
                                    Enter the type of processing activities that
                                    take place at this location. For example:
                                    Printing, Tooling, Assembly.
                                </Typography>
                                <StyledSelect
                                    id="processing_type"
                                    name="Processing Type"
                                    aria-label="Processing Type"
                                    label={null}
                                    options={mapProcessingTypeOptions(
                                        facilityProcessingTypeOptions || [],
                                        locationType || [],
                                    )}
                                    value={processingType}
                                    onChange={handleProcessingType}
                                    className={`basic-multi-select notranslate ${classes.selectStyles}`}
                                    styles={selectStyles}
                                />
                            </div>
                            <div className={classes.inputSectionWrapStyles}>
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
                                    Enter a number or a range for the number of
                                    people employed at the location. For
                                    example: 100, 100-150.
                                </Typography>
                                <StyledSelect
                                    id="number_of_workers"
                                    label={null}
                                    name="Number of Workers"
                                    options={numberOfWorkersOptions || []}
                                    value={numberOfWorkers}
                                    onChange={handleNumberOfWorkers}
                                    placeholder="Enter the number of workers as a number or range"
                                    aria-label="Number of workers"
                                    isMulti={false}
                                    className={`basic-multi-select notranslate ${classes.selectStyles}`}
                                    styles={selectStyles}
                                />
                            </div>
                            <div className={classes.inputSectionWrapStyles}>
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
                                    Select or enter the company that holds
                                    majority ownership for this production.
                                </Typography>
                                <StyledSelect
                                    creatable
                                    label={null}
                                    name="Parent company"
                                    value={parentCompany}
                                    onChange={handleParentCompany}
                                    placeholder="Select"
                                    aria-label="Parent company"
                                    className={`basic-multi-select notranslate ${classes.selectStyles}`}
                                    styles={selectStyles}
                                />
                            </div>
                        </>
                    )}
                </div>

                <div className={classes.buttonsContainerStyles}>
                    <Button
                        variant="outlined"
                        onClick={() => {}}
                        className={classes.goBackButtonStyles}
                        // classes={{
                        //     label: classes.buttonLabel,
                        // }}
                    >
                        Go Back
                    </Button>
                    <Button
                        color="secondary"
                        variant="contained"
                        onClick={() => {}}
                        className={classes.submitButtonStyles}
                        classes={{
                            label: classes.buttonLabel,
                        }}
                        // disabled={!isFormValid}
                    >
                        Submit
                    </Button>
                </div>
            </Paper>
        </div>
    );
};

ProductionLocationInfo.defaultProps = {
    countriesOptions: null,
    facilityProcessingTypeOptions: null,
    numberOfWorkersOptions: null,
    parentCompanyOptions: null,
    error: null,
};

ProductionLocationInfo.propTypes = {
    countriesOptions: countryOptionsPropType,
    fetchCountries: func.isRequired,
    fetchFacilityProcessingType: func.isRequired,
    facilityProcessingTypeOptions: facilityProcessingTypeOptionsPropType,
    numberOfWorkersOptions: numberOfWorkerOptionsPropType,
    parentCompanyOptions: parentCompanyOptionsPropType,
    fetchParentCompanies: func.isRequired,
    fetching: bool.isRequired,
    error: string,
    classes: object.isRequired,
};

const mapStateToProps = ({
    filterOptions: {
        countries: { data: countriesOptions, fetching, error },
        parentCompanies: {
            data: parentCompanyOptions,
            // fetching: fetchingParentCompanies,
        },
        facilityProcessingType: {
            data: facilityProcessingTypeOptions,
            // fetching: fetchingFacilityProcessingType,
        },
        numberOfWorkers: {
            data: numberOfWorkersOptions,
            // fetching: fetchingNumberofWorkers,
        },
    },
}) => ({
    countriesOptions,
    facilityProcessingTypeOptions,
    numberOfWorkersOptions,
    parentCompanyOptions,
    fetching,
    error,
});

function mapDispatchToProps(dispatch) {
    return {
        fetchCountries: () => dispatch(fetchCountryOptions()),
        fetchFacilityProcessingType: () =>
            dispatch(fetchFacilityProcessingTypeOptions()),
        fetchNumberOfWorkers: () => dispatch(fetchNumberOfWorkersOptions()),
        fetchParentCompanies: () => dispatch(fetchParentCompanyOptions()),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(productionLocationInfoStyles)(ProductionLocationInfo));
