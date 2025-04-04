import React from 'react';
import { useLocation } from 'react-router-dom';
import { string, arrayOf, object } from 'prop-types';
import { Typography } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import PreviousOsIdTooltip from './PreviousOsIdTooltip';
import { makeProductionLocationDetailsStyles } from '../../util/styles';
import { getLastPathParameter } from '../../util/util';

const ProductionLocationDetails = ({
    osId,
    name,
    address,
    countryName,
    historicalOsIds,
    classes,
}) => {
    const { pathname = '' } = useLocation();
    const osIdSearchParameter = pathname ? getLastPathParameter(pathname) : '';

    const previousOsId = historicalOsIds.find(
        historicalOsId => historicalOsId === osIdSearchParameter,
    );

    return (
        <div>
            <Typography component="h3" className={classes.locationNameStyles}>
                {name}
            </Typography>
            <Typography
                component="h6"
                className={classes.locationCurrentOsIdStyles}
            >
                {previousOsId ? 'Current OS ID:' : 'OS ID:'} {osId}
            </Typography>
            {previousOsId && (
                <Typography className={classes.locationHistoricalOsIdStyles}>
                    Previous OS ID: {previousOsId} <PreviousOsIdTooltip />
                </Typography>
            )}
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
