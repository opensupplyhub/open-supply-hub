import React, { useState, useEffect } from 'react';
import { bool, string, func, object } from 'prop-types';
import { useHistory } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import { connect } from 'react-redux';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import CircularProgress from '@material-ui/core/CircularProgress';
import StyledSelect from '../Filters/StyledSelect';

import { makeSearchByNameAddressTabStyles } from '../../util/styles';

import { countryOptionsPropType } from '../../util/propTypes';
import { fetchCountryOptions } from '../../actions/filterOptions';

const InputHelperText = ({ classes }) => (
    <span className={classes.helperTextWrapStyles}>
        <InfoOutlinedIcon className={classes.iconInfoStyles} />
        <Typography component="span" className={classes.inputHelperTextStyles}>
            This field is required.
        </Typography>
    </span>
);

const defaultCountryOption = {
    label: "What's the country?",
    value: '',
};

const selectStyles = {
    control: provided => ({
        ...provided,
        height: '56px',
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
    const [inputCountry, setInputCountry] = useState(defaultCountryOption);
    const [nameTouched, setNameTouched] = useState(false);
    const [addressTouched, setAddressTouched] = useState(false);

    const history = useHistory();
    const validate = val => val.length > 0;
    const handleNameChange = event => {
        setNameTouched(true);
        setInputName(event.target.value);
    };
    const handleAddressChange = event => {
        setAddressTouched(true);
        setInputAddress(event.target.value);
    };
    const handleCountryChange = event => {
        setInputCountry(event || defaultCountryOption);
    };

    const handleSearch = () => {
        const baseUrl = '/contribute/production-location/search/';
        const params = new URLSearchParams({
            name: inputName,
            address: inputAddress,
            country: inputCountry.value ?? '',
        });
        const url = `${baseUrl}?${params.toString()}`;

        history.push(url);
    };
    const isFormValid =
        validate(inputName) &&
        validate(inputAddress) &&
        validate(inputCountry.value);

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
                        !validate(inputName) && (
                            <InputHelperText classes={classes} />
                        )
                    }
                    error={nameTouched && !validate(inputName)}
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
                        !validate(inputAddress) && (
                            <InputHelperText classes={classes} />
                        )
                    }
                    error={addressTouched && !validate(inputAddress)}
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
                    className={`basic-multi-select notranslate ${classes.selectStyles}`}
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
    error: string,
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
