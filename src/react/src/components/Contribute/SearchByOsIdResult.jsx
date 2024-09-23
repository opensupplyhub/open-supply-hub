import React from 'react';
import { useHistory } from 'react-router-dom';
import { object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import ArrowBack from '@material-ui/icons/ArrowBack';

import SearchByOsIdNoResult from './SearchByOsIdNoResult';
import { contributeProductionLocationRoute } from '../../util/constants';
// import { makeSearchByOsIdResultStyles } from '../../util/styles';

export const makeSearchByOsIdResultStyles = theme =>
    Object.freeze({
        titleStyles: Object.freeze({
            fontSize: '36px',
            fontWeight: '700',
        }),
        resultContainerStyles: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            padding: '40px 110px',
            borderRadius: '0',
            boxShadow: 'none',
        }),
        locationDetailsStyles: Object.freeze({
            fontSize: '18px',
            fontWeight: '600',
            margin: '24px 0',
        }),
        actionsStyles: Object.freeze({
            display: 'flex',
            gap: '16px',
            marginTop: '40px',
        }),
        secondaryButtonStyles: Object.freeze({
            width: '200px',
            borderRadius: '0',
            textTransform: 'none',
            fontWeight: 'bold',
            backgroundColor: theme.palette.action.main,
            color: theme.palette.getContrastText(theme.palette.action.main),
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
        primaryButtonStyles: Object.freeze({
            width: '200px',
            borderRadius: '0',
            textTransform: 'none',
            fontWeight: 'bold',
        }),
    });

const SearchByOsIdResult = ({ data, classes }) => {
    console.log('data in SearchByOsIdResult >>>', data);
    const history = useHistory();

    if (!data || data?.data.length === 0) {
        return <SearchByOsIdNoResult />;
    }

    const { data: newData } = data;
    const { os_id: osId, name, address } = newData[0];

    return (
        <>
            <Button
                color="primary"
                className={classes.backButton}
                onClick={() => {
                    // clearFacility();
                    history.push(contributeProductionLocationRoute);
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
                    className={classes.titleStyles}
                >
                    Is this your production location?
                </Typography>
                <div className={classes.locationDetailsStyles}>
                    <Typography>Location Name: {name}</Typography>
                    <Typography>OS ID: {osId}</Typography>
                    <Typography>Address Line 1: {address}</Typography>
                </div>
                <div className={classes.actionsStyles}>
                    <Button
                        variant="outlined"
                        className={classes.secondaryButtonStyles}
                    >
                        No, search by name and address
                    </Button>
                    <Button
                        variant="contained"
                        color="primary"
                        className={classes.primaryButtonStyles}
                    >
                        Yes, add data and claim
                    </Button>
                </div>
            </Paper>
        </>
    );
};

SearchByOsIdResult.defaultProps = {
    data: {},
};

SearchByOsIdResult.propTypes = {
    data: object,
};

export default withStyles(makeSearchByOsIdResultStyles)(SearchByOsIdResult);
