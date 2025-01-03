import React from 'react';
import { func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import SearchByOsIdResultActions from './SearchByOsIdResultActions';
import { makeSearchByOsIdNotFoundResultStyles } from '../../util/styles';

const SearchByOsIdNotFoundResult = ({
    handleBackToSearchByNameAddress,
    handleBackToSearchByOsId,
    classes,
}) => (
    <>
        <Typography component="h2" className={classes.resultTitleStyles}>
            We didn&apos;t find a production location with that ID.
        </Typography>
        <Typography className={classes.resultDescriptionStyles}>
            You can try searching by another OS ID or searching by name and
            address.
        </Typography>
        <SearchByOsIdResultActions
            defaultButtonLabel="Search by Name and Address"
            defaultButtonAction={handleBackToSearchByNameAddress}
            secondaryButtonLabel="Search for another ID"
            secondaryButtonAction={handleBackToSearchByOsId}
        />
    </>
);

SearchByOsIdNotFoundResult.propTypes = {
    handleBackToSearchByNameAddress: func.isRequired,
    handleBackToSearchByOsId: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeSearchByOsIdNotFoundResultStyles)(
    SearchByOsIdNotFoundResult,
);
