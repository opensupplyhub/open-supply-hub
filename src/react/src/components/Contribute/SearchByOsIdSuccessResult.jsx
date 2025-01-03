import React from 'react';
import { object, func } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import SearchByOsIdResultActions from './SearchByOsIdResultActions';
import { makeSearchByOsIdResultStyles } from '../../util/styles';
import { productionLocationPropType } from '../../util/propTypes';
import ProductionLocationDetails from './ProductionLocationDetails';

const SearchByOsIdSuccessResult = ({
    productionLocation,
    handleBackToSearchByNameAddress,
    classes,
}) => {
    const {
        name,
        os_id: osId,
        historical_os_id: historicalOsIds,
        address,
        country: { name: countryName } = {},
    } = productionLocation;

    return (
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
};

SearchByOsIdSuccessResult.propTypes = {
    productionLocation: productionLocationPropType.isRequired,
    handleBackToSearchByNameAddress: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeSearchByOsIdResultStyles)(
    SearchByOsIdSuccessResult,
);
