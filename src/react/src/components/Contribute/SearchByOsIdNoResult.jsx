import React from 'react';
import { useHistory } from 'react-router-dom';
import propTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import ArrowBack from '@material-ui/icons/ArrowBackIos';

import { contributeProductionLocationRoute } from '../../util/constants';
import COLOURS from '../../util/COLOURS';

const makeSearchByOsIdNoResultStyles = theme =>
    Object.freeze({
        backButtonRoot: Object.freeze({
            textTransform: 'none',
            fontSize: '18px',
            fontWeight: '700',
            width: '200px',
            maxHeight: '24px',
            display: 'flex',
            justifyContent: 'flex-start',

            padding: '0',
            '&:hover': {
                backgroundColor: 'initial',
            },
        }),
        backButtonLabel: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
        }),
        titleStyles: Object.freeze({
            fontWeight: theme.typography.fontWeightBold,
            fontSize: '56px',
            lineHeight: '60px',
            margin: '40px 0 48px 0',
        }),
        resultContainerStyles: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            padding: '40px 110px',
            borderRadius: '0',
            boxShadow: 'none',
        }),
        mainTitleStyles: Object.freeze({
            fontSize: '36px',
            fontWeight: '700',
            lineHeight: '44px',
        }),
        subTitleStyles: Object.freeze({
            fontSize: '18px',
            lineHeight: '21px',
            fontWeight: theme.typography.fontWeightSemiBold,
            margin: '8px 0 24px 0',
        }),
        actionsStyles: Object.freeze({
            display: 'flex',
            gap: '24px',
        }),
        buttonLabelStyles: Object.freeze({
            fontSize: '18px',
            lineHeight: '20px',
            fontWeight: theme.typography.fontWeightBold,
        }),
        buttonBaseStyles: {
            width: '265px',
            height: '49px',
            borderRadius: '0',
            textTransform: 'none',
        },
        defaultButtonStyles: {
            borderColor: COLOURS.NEAR_BLACK,
        },
        secondaryButtonStyles: {
            backgroundColor: theme.palette.action.main,
            color: theme.palette.getContrastText(theme.palette.action.main),
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        },
    });

const SearchByOsIdNoResult = ({ classes }) => {
    const history = useHistory();

    const handleBackToSearch = () => {
        history.push(contributeProductionLocationRoute);
    };

    return (
        <>
            <Button
                color="primary"
                // className={classes.backButton}
                classes={{
                    root: classes.backButtonRoot,
                    label: classes.backButtonLabel,
                }}
                onClick={() => {
                    // clearFacility();
                    handleBackToSearch();
                }}
            >
                <ArrowBack />
                Back to ID search
            </Button>
            <Typography
                component="h1"
                variant="h1"
                className={classes.titleStyles}
            >
                Production Location Search
            </Typography>
            <Paper className={classes.resultContainerStyles}>
                <Typography
                    component="h2"
                    variant="h2"
                    className={classes.mainTitleStyles}
                >
                    We didn&apos;t find a production location with that ID.
                </Typography>
                <Typography className={classes.subTitleStyles}>
                    You can try searching by another OS ID or searching by name
                    and address.
                </Typography>
                <div className={classes.actionsStyles}>
                    <Button
                        variant="outlined"
                        classes={{
                            root: `${classes.buttonBaseStyles} ${classes.defaultButtonStyles}`,
                            label: classes.buttonLabelStyles,
                        }}
                    >
                        Search by Name and Address
                    </Button>
                    <Button
                        variant="contained"
                        color="secondary"
                        classes={{
                            root: `${classes.buttonBaseStyles} ${classes.secondaryButtonStyles}`,
                            label: classes.buttonLabelStyles,
                        }}
                        onClick={() => {
                            // clearFacility();
                            handleBackToSearch();
                        }}
                    >
                        Search for another ID
                    </Button>
                </div>
            </Paper>
        </>
    );
};

SearchByOsIdNoResult.propTypes = {
    classes: propTypes.object.isRequired,
};

export default withStyles(makeSearchByOsIdNoResultStyles)(SearchByOsIdNoResult);
