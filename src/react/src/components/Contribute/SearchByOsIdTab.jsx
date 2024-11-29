/* eslint no-unused-vars: 0 */
import React, { useState } from 'react';
import Grid from '@material-ui/core/Grid';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import { useHistory } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import COLOURS from '../../util/COLOURS';

import { makeSearchByOsIdTabStyles } from '../../util/styles';
import { OS_ID_LENGTH } from '../../util/constants';

const confirmProductionLocationModalStyles = Object.freeze({
    titleContentStyle: Object.freeze({
        textAlign: 'center',
    }),
    icon: Object.freeze({
        color: COLOURS.DARK_GREEN,
        verticalAlign: 'middle',
        marginRight: '10px',
    }),
    separator: Object.freeze({
        color: COLOURS.GREY,
    }),
    dialogContentStyles: Object.freeze({
        textAlign: 'center',
        fontSize: '20px',
    }),
    buttonContentStyle: Object.freeze({
        justifyContent: 'center',
    }),
});

const ProductionLocationDialog = ({ classes }) => (
    <Dialog open>
        <DialogTitle
            style={confirmProductionLocationModalStyles.titleContentStyle}
        >
            Thanks for adding data for this production location!
        </DialogTitle>
        <DialogContent>
            <Typography
                variant="body1"
                style={confirmProductionLocationModalStyles.dialogContentStyles}
            >
                Do you own or manage this location? If so, you can now claim
                your production location to have a complete, credible and
                confirmed profile with a green banner and claimed badge. You’ll
                be able to add more information, like contact details,
                certifications, native language name, and more.
            </Typography>
            <hr style={confirmProductionLocationModalStyles.separator} />
            <Grid container className={classes.contentContainer}>
                <Grid item xs={12} md={6}></Grid>
                <Grid item xs={12} md={6}></Grid>
            </Grid>
        </DialogContent>
        <DialogActions
            style={confirmProductionLocationModalStyles.buttonContentStyle}
        >
            <Button
                variant="outlined"
                color="secondary"
                onClick={() => {
                    console.log('Init click 1');
                }}
            >
                Search OS Hub
            </Button>
            <Button
                variant="outlined"
                color="primary"
                onClick={() => {
                    console.log('Init click 2');
                }}
            >
                Submit another Location
            </Button>
            <Button
                variant="outlined"
                color="primary"
                onClick={() => {
                    console.log('Init click 3');
                }}
            >
                Continue to Claim
            </Button>
        </DialogActions>
    </Dialog>
);

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
            `/contribute/production-location/search/?os_id=${inputOsId}`,
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
                {/** TODO: move this modal somewhere else later */}
                <ProductionLocationDialog />
            </Paper>
        </>
    );
};

export default withStyles(makeSearchByOsIdTabStyles)(SearchByOsIdTab);
