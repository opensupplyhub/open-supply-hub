import React, { useState } from 'react';
// import { useHistory } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';

import StyledSelect from '../Filters/StyledSelect';

import { makeSearchByNameAddressTabStyles } from '../../util/styles';

const NameHelperText = ({ classes }) => (
    <span className={classes.helperTextContainerStyles}>
        <InfoOutlinedIcon className={classes.infoIconStyles} />
        <Typography component="span" className={classes.helperTextStyles}>
            This field is required.
        </Typography>
    </span>
);

const createCountriesChoicesFromParams = params => {
    if (params.length) {
        return params.map(x => ({ label: x.name, value: x.alpha_2 }));
    }
    return null;
};

const selectStyles = {
    control: provided => ({
        ...provided,
        height: '56px',
    }),
};

const SearchByNameAndAddressTab = ({ classes }) => {
    const [inputName, setInputName] = useState('');
    const [inputAddress, setInputAddress] = useState('');
    const [inputCountry, setInputCountry] = useState('');
    const [nameTouched, setNameTouched] = useState(false);
    const [addressTouched, setAddressTouched] = useState(false);

    // const history = useHistory();
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
        setInputCountry(event || '');
    };

    const handleSearch = () => {
        // history.push(
        //     `/contribute/production-location/search/?name=${inputName}&address=${inputAddress}&country=${inputCountry.value}`,
        // );
    };
    const isDisabled =
        validate(inputName) &&
        validate(inputAddress) &&
        validate(inputCountry.label || '');
    const mockCountries = [
        {
            name: 'United Kingdom of Great Britain and Northern Ireland',
            alpha_2: 'GB',
            alpha_3: 'GBR',
            numeric: '826',
        },
        {
            name: 'United States of America',
            alpha_2: 'US',
            alpha_3: 'USA',
            numeric: '840',
        },
    ];

    return (
        <>
            <Typography className={classes.instructionTextStyles}>
                Check if the production location is already on OS Hub. Enter the
                production location’s name, address and country in the fields
                below and click “Search”.
            </Typography>
            <Paper className={classes.searchContainerStyles}>
                <Typography component="h2" className={classes.mainTitleStyles}>
                    Production Location Details
                </Typography>
                <Typography component="h4" className={classes.subTitleStyles}>
                    Enter the Name
                </Typography>
                <TextField
                    id="name"
                    className={classes.textFieldStyles}
                    value={inputName}
                    onChange={handleNameChange}
                    placeholder="Type a name"
                    variant="outlined"
                    aria-label="Type a name"
                    InputProps={{
                        classes: {
                            input: classes.searchInputStyles,
                            notchedOutline: classes.notchedOutlineStyles,
                        },
                        inputProps: {
                            type: 'text',
                        },
                    }}
                    helperText={
                        nameTouched &&
                        !validate(inputName) && (
                            <NameHelperText classes={classes} />
                        )
                    }
                    error={nameTouched && !validate(inputName)}
                />
                <Typography component="h4" className={classes.subTitleStyles}>
                    Enter the Address
                </Typography>
                <TextField
                    id="address"
                    className={classes.textFieldStyles}
                    value={inputAddress}
                    onChange={handleAddressChange}
                    placeholder="Address"
                    variant="outlined"
                    aria-label="Address"
                    InputProps={{
                        classes: {
                            input: classes.searchInputStyles,
                            notchedOutline: classes.notchedOutlineStyles,
                        },
                        inputProps: {
                            type: 'text',
                        },
                    }}
                    helperText={
                        addressTouched &&
                        !validate(inputAddress) && (
                            <NameHelperText classes={classes} />
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
                    options={
                        createCountriesChoicesFromParams(mockCountries) || []
                    }
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
                    className={classes.buttonStyles}
                    classes={{
                        label: classes.buttonLabel,
                    }}
                    disabled={!isDisabled}
                >
                    Search
                </Button>
            </Paper>
        </>
    );
};

export default withStyles(makeSearchByNameAddressTabStyles)(
    SearchByNameAndAddressTab,
);
