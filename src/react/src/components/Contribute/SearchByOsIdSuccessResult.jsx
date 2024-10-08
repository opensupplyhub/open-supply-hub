import React from 'react';
import { string, object, func, arrayOf } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import PreviousOsIdTooltip from './PreviousOsIdTooltip';
import SearchByOsIdResultActions from './SearchByOsIdResultActions';
import { makeSearchByOsIdResultStyles } from '../../util/styles';

const SearchByOsIdSuccessResult = ({
    name,
    osId,
    historicalOsIds,
    address,
    countryName,
    handleBackToSearchByNameAddress,
    classes,
}) => {
    const historicalOsIdsNotEmpty =
        Array.isArray(historicalOsIds) && historicalOsIds.length > 0;

    return (
        <>
            <Typography component="h2" className={classes.resultTitleStyles}>
                Is this your production location?
            </Typography>
            <div className={classes.locationDetailsStyles}>
                <Typography
                    component="h3"
                    className={classes.locationNameStyles}
                >
                    {name}
                </Typography>
                <Typography
                    component="h6"
                    className={classes.locationCurrentOsIdStyles}
                >
                    {historicalOsIdsNotEmpty ? 'Current OS ID:' : 'OS ID:'}{' '}
                    {osId}
                </Typography>
                {historicalOsIdsNotEmpty &&
                    historicalOsIds.map(historicalOsId => (
                        <Typography
                            key={historicalOsId}
                            className={classes.locationHistoricalOsIdStyles}
                        >
                            Previous OS ID: {historicalOsId}{' '}
                            <PreviousOsIdTooltip />
                        </Typography>
                    ))}
                <div className={classes.locationAddressContainerStyles}>
                    <Typography className={classes.locationAddressStyles}>
                        {address}
                    </Typography>
                    <Typography className={classes.locationAddressStyles}>
                        {countryName}
                    </Typography>
                </div>
            </div>
            <SearchByOsIdResultActions
                defaultButtonLabel="No, search by name and address"
                defaultButtonAction={handleBackToSearchByNameAddress}
                secondaryButtonLabel="Yes, add data and claim"
                secondaryButtonAction={() => {}}
            />
        </>
    );
};

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
