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
import { productionLocationInfoRoute } from '../../util/constants';
import COLOURS from '../../util/COLOURS';
import { makeSearchByNameAddressTabStyles } from '../../util/styles';

import { countryOptionsPropType } from '../../util/propTypes';
import { fetchCountryOptions } from '../../actions/filterOptions';

const defaultCountryOption = {
    label: "What's the country?",
    value: '',
};

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
    placeholder: provided => ({
        ...provided,
        opacity: 0.7,
    }),
};

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

    const history = useHistory();
    const isValid = val => {
        if (val) {
            return val.length > 0;
        }
        return false;
    };
    const handleNameChange = event => {
        setNameTouched(true);
        setInputName(event.target.value);
    };
    const handleAddressChange = event => {
        setAddressTouched(true);
        setInputAddress(event.target.value);
    };
    const handleCountryChange = event => {
        setCountryTouched(true);
        setInputCountry(event);
    };

    const handleSearch = () => {
        const baseUrl = productionLocationInfoRoute;
        const params = new URLSearchParams({
            name: inputName,
            address: inputAddress,
            country: inputCountry.value ?? '',
        });
        const url = `${baseUrl}?${params.toString()}`;

        history.push(url);
    };
    const isFormValid =
        isValid(inputName) &&
        isValid(inputAddress) &&
        countryTouched &&
        isValid(inputCountry.value);

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
                <Typography component="h4" className={classes.subTitleStyles}>
                    Enter the Name
                </Typography>
                <TextField
                    id="name"
                    className={classes.textInputStyles}
                    value={inputName}
                    onChange={handleNameChange}
                    placeholder="Type a name"
                    variant="outlined"
                    aria-label="Type a name"
                    InputProps={{
                        classes: {
                            input: `${classes.searchInputStyles}
                                ${
                                    nameTouched &&
                                    !isValid(inputName) &&
                                    classes.errorStyle
                                }`,
                            notchedOutline: classes.notchedOutlineStyles,
                        },
                        inputProps: {
                            type: 'text',
                        },
                    }}
                    helperText={
                        nameTouched && !isValid(inputName) && <InputErrorText />
                    }
                    error={nameTouched && !isValid(inputName)}
                />
                <Typography component="h4" className={classes.subTitleStyles}>
                    Enter the Address
                </Typography>
                <TextField
                    id="address"
                    className={classes.textInputStyles}
                    value={inputAddress}
                    onChange={handleAddressChange}
                    placeholder="Address"
                    variant="outlined"
                    aria-label="Address"
                    InputProps={{
                        classes: {
                            input: `${classes.searchInputStyles}
                            ${
                                addressTouched &&
                                !isValid(inputAddress) &&
                                classes.errorStyle
                            }`,
                            notchedOutline: classes.notchedOutlineStyles,
                        },
                    }}
                    helperText={
                        addressTouched &&
                        !isValid(inputAddress) && <InputErrorText />
                    }
                    error={addressTouched && !isValid(inputAddress)}
                />
                <Typography component="h4" className={classes.subTitleStyles}>
                    Select the Country
                </Typography>
                <StyledSelect
                    id="countries"
                    name="What's the country?"
                    aria-label="Select country"
                    label={null}
                    options={countriesData || []}
                    value={inputCountry}
                    onChange={handleCountryChange}
                    className={classes.selectStyles}
                    styles={selectStyles}
                    placeholder="What's the country?"
                    isMulti={false}
                />

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
