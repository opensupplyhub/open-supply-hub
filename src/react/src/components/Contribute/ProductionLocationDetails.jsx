import React from 'react';
import { string, arrayOf, object } from 'prop-types';
import { Typography } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import PreviousOsIdTooltip from './PreviousOsIdTooltip';
import { makeProductionLocationDetailsStyles } from '../../util/styles';

const ProductionLocationDetails = ({
    osId,
    name,
    address,
    countryName,
    historicalOsIds,
    classes,
}) => {
    const historicalOsIdsNotEmpty =
        Array.isArray(historicalOsIds) && historicalOsIds.length > 0;

    return (
        <div>
            <Typography component="h3" className={classes.locationNameStyles}>
                {name}
            </Typography>
            <Typography
                component="h6"
                className={classes.locationCurrentOsIdStyles}
            >
                {historicalOsIdsNotEmpty ? 'Current OS ID:' : 'OS ID:'} {osId}
            </Typography>
            {historicalOsIdsNotEmpty &&
                historicalOsIds.map(historicalOsId => (
                    <Typography
                        key={historicalOsId}
                        className={classes.locationHistoricalOsIdStyles}
                    >
                        Previous OS ID: {historicalOsId} <PreviousOsIdTooltip />
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
    );
};

ProductionLocationDetails.defaultProps = {
    historicalOsIds: [],
};

ProductionLocationDetails.propTypes = {
    osId: string.isRequired,
    name: string.isRequired,
    address: string.isRequired,
    countryName: string.isRequired,
    historicalOsIds: arrayOf(string),
    classes: object.isRequired,
};

export default withStyles(makeProductionLocationDetailsStyles)(
    ProductionLocationDetails,
);
