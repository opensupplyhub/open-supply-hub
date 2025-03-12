import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';

import { makeSearchByOsIdTabStyles } from '../../util/styles';
import { OS_ID_LENGTH } from '../../util/constants';

const HelperText = ({ classes }) => (
    <span className={classes.helperTextContainerStyles}>
        <InfoOutlinedIcon className={classes.infoIconStyles} />
        <Typography component="span" className={classes.helperTextStyles}>
            To search by ID, you need to enter the full OS ID of the production
            location.
        </Typography>
    </span>
);

const SearchByOsIdTab = ({ classes }) => {
    const [inputOsId, setInputOsId] = useState('');
    const history = useHistory();
    const isValidOsId = inputOsId.length === OS_ID_LENGTH;

    const handleChange = event => {
        const uppercaseValue = event.target.value.toUpperCase();
        setInputOsId(uppercaseValue);
    };

    const handleSearch = () => {
        history.push(
            `/contribute/single-location/search/id/${encodeURIComponent(
                inputOsId,
            )}`,
        );
    };

    return (
        <>
            <Typography className={classes.instructionTextStyles}>
                Enter the full OS ID to search for a matching profile. Use the
                field below and click “search”.
            </Typography>
            <Paper className={classes.searchContainerStyles}>
                <Typography component="h2" className={classes.mainTitleStyles}>
                    Know the OS ID for your location?
                </Typography>
                <Typography component="h4" className={classes.subTitleStyles}>
                    If you know the OS ID for your production location enter it
                    below, otherwise select the “Search by Name and Address”
                    tab.
                </Typography>
                <TextField
                    id="os-id"
                    className={classes.textFieldStyles}
                    value={inputOsId}
                    onChange={handleChange}
                    helperText={<HelperText classes={classes} />}
                    placeholder="Enter the OS ID"
                    variant="outlined"
                    aria-label="Enter the OS ID"
                    InputProps={{
                        classes: {
                            input: classes.searchInputStyles,
                            notchedOutline: classes.notchedOutlineStyles,
                        },
                        inputProps: {
                            maxLength: OS_ID_LENGTH,
                        },
                    }}
                />
                <Button
                    color="secondary"
                    variant="contained"
                    onClick={handleSearch}
                    className={classes.buttonStyles}
                    classes={{
                        label: classes.buttonLabel,
                    }}
                    disabled={!isValidOsId}
                >
                    Search by ID
                </Button>
            </Paper>
        </>
    );
};

export default withStyles(makeSearchByOsIdTabStyles)(SearchByOsIdTab);
