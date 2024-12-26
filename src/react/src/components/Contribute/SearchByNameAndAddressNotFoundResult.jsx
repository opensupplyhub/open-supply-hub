import React from 'react';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import { object } from 'prop-types';
import history from '../../util/history';
import { contributeProductionLocationRoute } from '../../util/constants';

const makeSearchByNameAndAddressNotFoundResultStyles = theme =>
    Object.freeze({
        contentWrapperStyles: Object.freeze({
            maxWidth: '601px',
            margin: '94px auto 166px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
        }),
        titleStyles: Object.freeze({
            fontWeight: theme.typography.fontWeightExtraBold,
            fontSize: '56px',
            lineHeight: '60px',
            marginBottom: '16px',
            textAlign: 'center',
        }),
        descriptionStyles: Object.freeze({
            fontSize: '18px',
            lineHeight: '21px',
            marginBottom: '32px',
            textAlign: 'center',
        }),
        controlsContainerStyles: Object.freeze({
            display: 'flex',
            gap: '24px',
        }),
        buttonBaseStyles: Object.freeze({
            textTransform: 'none',
            border: 'none',
            height: '49px',
            width: '256px',
        }),
        buttonLabelStyles: Object.freeze({
            fontSize: '18px',
            lineHeight: '22px',
            fontWeight: theme.typography.fontWeightExtraBold,
        }),
        addLocationButtonStyles: Object.freeze({
            backgroundColor: theme.palette.action.main,
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
    });

const SearchByNameAndAddressNotFoundResult = ({ classes }) => {
    const handleSearchAgain = () => {
        // clearProductionLocations();
        history.push(`${contributeProductionLocationRoute}?tab=name-address`);
    };

    const handleAddNewLocation = () => {
        // clearProductionLocations();
        console.log('Add a new location');
    };

    return (
        <div className={classes.contentWrapperStyles}>
            <Typography component="h1" className={classes.titleStyles}>
                Search returned no results
            </Typography>
            <Typography className={classes.descriptionStyles}>
                We could not find any results that match your search criteria.
                If you think the production location you are looking for is
                already on OS Hub, check the information you entered and try
                again. If you still don&apos;t find any results, add a new
                production location.
            </Typography>
            <div className={classes.controlsContainerStyles}>
                <Button
                    variant="contained"
                    color="secondary"
                    classes={{
                        root: classes.buttonBaseStyles,
                        label: classes.buttonLabelStyles,
                    }}
                    onClick={handleSearchAgain}
                >
                    Search again
                </Button>
                <Button
                    variant="outlined"
                    classes={{
                        root: `${classes.buttonBaseStyles} ${classes.addLocationButtonStyles}`,
                        label: classes.buttonLabelStyles,
                    }}
                    onClick={handleAddNewLocation}
                >
                    Add a new Location
                </Button>
            </div>
        </div>
    );
};

SearchByNameAndAddressNotFoundResult.propTypes = {
    classes: object.isRequired,
};

export default withStyles(makeSearchByNameAndAddressNotFoundResultStyles)(
    SearchByNameAndAddressNotFoundResult,
);
