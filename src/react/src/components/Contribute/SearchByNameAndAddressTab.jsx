import React, { useState, useEffect } from 'react';
import { bool, string, func, object, arrayOf } from 'prop-types';
import { useHistory } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import { connect } from 'react-redux';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import CircularProgress from '@material-ui/core/CircularProgress';
import StyledSelect from '../Filters/StyledSelect';
import InputErrorText from './InputErrorText';
import RequiredAsterisk from '../RequiredAsterisk';
import { fetchCountryOptions } from '../../actions/filterOptions';
import { searchByNameAndAddressResultRoute } from '../../util/constants';
import { countryOptionsPropType } from '../../util/propTypes';
import { makeSearchByNameAddressTabStyles } from '../../util/styles';
import { getSelectStyles, isRequiredFieldValid } from '../../util/util';

const FormFieldTitle = ({ label, classes }) => (
    <Typography component="h4" className={classes.formFieldTitleStyles}>
        {label}
        <RequiredAsterisk />
    </Typography>
);

const SearchByNameAndAddressTab = ({
    classes,
    countriesData,
    fetchCountries,
    fetching,
    error,
}) => {
    const [inputName, setInputName] = useState('');
    const [inputAddress, setInputAddress] = useState('');
    const [inputCountry, setInputCountry] = useState(null);
    const [nameTouched, setNameTouched] = useState(false);
    const [addressTouched, setAddressTouched] = useState(false);
    const [countryTouched, setCountryTouched] = useState(false);

    const isCountryError = countryTouched && !inputCountry?.value;

    const history = useHistory();

    const handleNameChange = event => {
        setInputName(event.target.value);
    };
    const handleAddressChange = event => {
        setInputAddress(event.target.value);
    };
    const handleCountryChange = event => {
        setInputCountry(event);
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

    const handleSearch = () => {
        const baseUrl = searchByNameAndAddressResultRoute;
        const params = new URLSearchParams({
            name: inputName,
            address: inputAddress,
            country: inputCountry.value ?? '',
        });
        const url = `${baseUrl}?${params.toString()}`;

        history.push(url);
    };

    const isFormValid = !!(
        isRequiredFieldValid(inputName) &&
        isRequiredFieldValid(inputAddress) &&
        inputCountry?.value
    );

    useEffect(() => {
        if (!countriesData) {
            fetchCountries();
        }
    }, [countriesData, fetchCountries]);

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
        <>
            <Typography className={classes.instructionStyles}>
                Check if the production location is already on OS Hub. Enter the
                production location’s name, address and country in the fields
                below and click “Search”.
            </Typography>
            <Paper className={classes.searchWrapStyles}>
                <Typography component="h2" className={classes.titleStyles}>
                    Production Location Details
                </Typography>
                <FormFieldTitle label="Enter the Name" classes={classes} />
                <TextField
                    id="name"
                    className={classes.textInputStyles}
                    value={inputName}
                    onChange={handleNameChange}
                    onBlur={handleNameBlur}
                    placeholder="Type a name"
                    variant="outlined"
                    aria-label="Type a name"
                    helperText={
                        nameTouched &&
                        !isRequiredFieldValid(inputName) && <InputErrorText />
                    }
                    error={nameTouched && !isRequiredFieldValid(inputName)}
                    InputProps={{
                        classes: {
                            input: `${classes.searchInputStyles}
                                ${
                                    nameTouched &&
                                    !isRequiredFieldValid(inputName) &&
                                    classes.errorStyle
                                }`,
                            notchedOutline: classes.notchedOutlineStyles,
                        },
                        inputProps: {
                            type: 'text',
                        },
                    }}
                    FormHelperTextProps={{
                        classes: {
                            root: classes.helperTextStyles,
                        },
                    }}
                />
                <FormFieldTitle label="Enter the Address" classes={classes} />
                <TextField
                    id="address"
                    className={classes.textInputStyles}
                    value={inputAddress}
                    onChange={handleAddressChange}
                    onBlur={handleAddressBlur}
                    placeholder="Address"
                    variant="outlined"
                    aria-label="Address"
                    helperText={
                        addressTouched &&
                        !isRequiredFieldValid(inputAddress) && (
                            <InputErrorText />
                        )
                    }
                    error={
                        addressTouched && !isRequiredFieldValid(inputAddress)
                    }
                    InputProps={{
                        classes: {
                            input: `${classes.searchInputStyles}
                            ${
                                addressTouched &&
                                !isRequiredFieldValid(inputAddress) &&
                                classes.errorStyle
                            }`,
                            notchedOutline: classes.notchedOutlineStyles,
                        },
                    }}
                    FormHelperTextProps={{
                        classes: {
                            root: classes.helperTextStyles,
                        },
                    }}
                />
                <FormFieldTitle label="Select the Country" classes={classes} />
                <StyledSelect
                    id="countries"
                    name="What's the country?"
                    aria-label="Select country"
                    label={null}
                    options={countriesData || []}
                    value={inputCountry}
                    onChange={handleCountryChange}
                    onBlur={handleCountryBlur}
                    className={classes.selectStyles}
                    styles={getSelectStyles(isCountryError)}
                    placeholder="What's the country?"
                    isMulti={false}
                />
                {isCountryError && (
                    <div className={classes.errorWrapStyles}>
                        <InputErrorText text="The country is missing from your search. Select the correct country from the drop down menu." />
                    </div>
                )}

                <Button
                    color="secondary"
                    variant="contained"
                    onClick={handleSearch}
                    className={classes.searchButtonStyles}
                    classes={{
                        label: classes.buttonLabel,
                    }}
                    disabled={!isFormValid}
                >
                    Search
                </Button>
            </Paper>
        </>
    );
};

SearchByNameAndAddressTab.defaultProps = {
    countriesData: null,
    error: null,
};

SearchByNameAndAddressTab.propTypes = {
    countriesData: countryOptionsPropType,
    fetching: bool.isRequired,
    error: arrayOf(string),
    fetchCountries: func.isRequired,
    classes: object.isRequired,
};

FormFieldTitle.propTypes = {
    label: string.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    filterOptions: {
        countries: { data: countriesData, error, fetching },
    },
}) => ({
    countriesData,
    fetching,
    error,
});

const mapDispatchToProps = dispatch => ({
    fetchCountries: () => dispatch(fetchCountryOptions()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(makeSearchByNameAddressTabStyles)(SearchByNameAndAddressTab));
