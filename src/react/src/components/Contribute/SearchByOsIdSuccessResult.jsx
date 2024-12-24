import React from 'react';
import { string, object, func, arrayOf } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import SearchByOsIdResultActions from './SearchByOsIdResultActions';
import { makeSearchByOsIdResultStyles } from '../../util/styles';
import ProductionLocationDetails from './ProductionLocationDetails';

const SearchByOsIdSuccessResult = ({
    name,
    osId,
    historicalOsIds,
    address,
    countryName,
    handleBackToSearchByNameAddress,
    classes,
}) => (
    <>
        <Typography component="h2" className={classes.resultTitleStyles}>
            Is this your production location?
        </Typography>
        <ProductionLocationDetails
            osId={osId}
            name={name}
            address={address}
            countryName={countryName}
            historicalOsIds={historicalOsIds}
        />
        <SearchByOsIdResultActions
            defaultButtonLabel="No, search by name and address"
            defaultButtonAction={handleBackToSearchByNameAddress}
            secondaryButtonLabel="Yes, add data and claim"
            secondaryButtonAction={() => {}}
        />
    </>
);

SearchByOsIdSuccessResult.defaultProps = {
    historicalOsIds: [],
};

SearchByOsIdSuccessResult.propTypes = {
    name: string.isRequired,
    osId: string.isRequired,
    historicalOsIds: arrayOf(string),
    address: string.isRequired,
    countryName: string.isRequired,
    handleBackToSearchByNameAddress: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeSearchByOsIdResultStyles)(
    SearchByOsIdSuccessResult,
);
