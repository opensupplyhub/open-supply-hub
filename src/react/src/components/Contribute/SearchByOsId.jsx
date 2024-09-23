import React, { useState } from 'react';
import { connect } from 'react-redux';
import { func, object, bool } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';

import { fetchProductionLocationByOsId } from '../../actions/contributeProductionLocation';
import { makeSearchByOsIdStyles } from '../../util/styles';
import { productionLocationPropType } from '../../util/propTypes';

const OS_ID = 'OS ID';

const SearchByOsId = ({ data, fetching, fetchProductionLocation, classes }) => {
    console.log('data >>>', data);
    console.log('fetching >>>', fetching);
    const [value, setValue] = useState('');

    const handleChange = event => {
        const uppercaseValue = event.target.value.toUpperCase();
        setValue(uppercaseValue);
    };

    const helperText = (
        <div className={classes.helperTextContainerStyles}>
            <InfoOutlinedIcon className={classes.infoIconStyles} />
            <Typography className={classes.helperTextStyles}>
                To search you need to enter the full ID production location
            </Typography>
        </div>
    );

    return (
        <>
            <Typography className={classes.instructionTextStyles}>
                Enter the full OS ID to search for a matching profile. Use the
                field below and click “search”.
            </Typography>
            <Paper className={classes.searchContainerStyles}>
                <Typography
                    component="h2"
                    variant="h2"
                    className={classes.mainTitleStyles}
                >
                    Know the OS ID for your location?
                </Typography>
                <Typography
                    component="h4"
                    variant="h4"
                    className={classes.subTitleStyles}
                >
                    If you know the OS ID for your production location enter it
                    below, otherwise select the “Search by Name and Address”
                    tab.
                </Typography>
                <TextField
                    id={OS_ID}
                    className={classes.textFieldStyles}
                    value={value}
                    onChange={handleChange}
                    helperText={helperText}
                    placeholder="Enter the OS ID"
                    variant="outlined"
                    aria-label="Enter the OS ID"
                    InputProps={{
                        classes: {
                            input: classes.searchInputStyles,
                            notchedOutline: classes.notchedOutlineStyles,
                        },
                        inputProps: {
                            maxLength: 15,
                        },
                    }}
                />
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={() => fetchProductionLocation(value)}
                    className={classes.buttonStyles}
                    disabled={value.length < 15}
                >
                    Search by ID
                </Button>
            </Paper>
        </>
    );
};

SearchByOsId.defaultProps = {
    data: null,
};

SearchByOsId.propTypes = {
    data: productionLocationPropType,
    fetching: bool.isRequired,
    fetchProductionLocation: func.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    contributeProductionLocation: {
        singleProductionLocation: { data, fetching },
    },
}) => ({
    data,
    fetching,
});

const mapDispatchToProps = dispatch => ({
    fetchProductionLocation: data =>
        dispatch(fetchProductionLocationByOsId(data)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(makeSearchByOsIdStyles)(SearchByOsId));