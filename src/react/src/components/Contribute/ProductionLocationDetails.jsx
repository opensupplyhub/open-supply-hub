import React from 'react';
import { useLocation } from 'react-router-dom';
import { string, arrayOf, object, number } from 'prop-types';
import { Typography } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import ArrowUpward from '@material-ui/icons/ArrowUpward';
import ArrowForward from '@material-ui/icons/ArrowForward';
import ArrowDownward from '@material-ui/icons/ArrowDownward';
import CallMade from '@material-ui/icons/CallMade';
import PreviousOsIdTooltip from './PreviousOsIdTooltip';
import { makeProductionLocationDetailsStyles } from '../../util/styles';
import { getLastPathParameter } from '../../util/util';

const ProductionLocationDetails = ({
    osId,
    name,
    address,
    countryName,
    confidenceScore,
    historicalOsIds,
    classes,
}) => {
    const { pathname = '' } = useLocation();
    const osIdSearchParameter = pathname ? getLastPathParameter(pathname) : '';

    const previousOsId = historicalOsIds.find(
        historicalOsId => historicalOsId === osIdSearchParameter,
    );

    let confidenceScoreClassName = classes.confidenceScoreContainerLowStyles;
    let confidenceScoreIcon = <ArrowDownward />;

    if (confidenceScore > 0.85) {
        confidenceScoreClassName =
            classes.confidenceScoreContainerHighestStyles;
        confidenceScoreIcon = <ArrowUpward />;
    } else if (confidenceScore > 0.7) {
        confidenceScoreClassName = classes.confidenceScoreContainerHighStyles;
        confidenceScoreIcon = <CallMade />;
    } else if (confidenceScore > 0.5) {
        confidenceScoreClassName =
            classes.confidenceScoreContainerModerateStyles;
        confidenceScoreIcon = <ArrowForward />;
    }

    return (
        <div className="location-details-container">
            <Typography
                component="h3"
                className={`${classes.locationNameStyles} ${confidenceScoreClassName}`}
            >
                {name}
                <div className={classes.confidenceScoreContainerStyles}>
                    {confidenceScoreIcon}
                </div>
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
    confidenceScore: null,
};

ProductionLocationDetails.propTypes = {
    osId: string.isRequired,
    name: string.isRequired,
    address: string.isRequired,
    countryName: string.isRequired,
    confidenceScore: number,
    historicalOsIds: arrayOf(string),
    classes: object.isRequired,
};

export default withStyles(makeProductionLocationDetailsStyles)(
    ProductionLocationDetails,
);
