import React from 'react';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import { object } from 'prop-types';
import { contributeProductionLocationRoute } from '../../util/constants';
import history from '../../util/history';
import { makeSearchByNameAndAddressNotFoundResultStyles } from '../../util/styles';

const SearchByNameAndAddressNotFoundResult = ({ classes }) => {
    const handleSearchAgain = () => {
        history.push(`${contributeProductionLocationRoute}?tab=name-address`);
    };

    const handleAddNewLocation = () => {};

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
