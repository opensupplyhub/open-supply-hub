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

    let confidenceScoreParams = {
        className: classes.confidenceScoreContainerLowStyles,
        icon: <ArrowDownward fontSize="small" />,
        text: 'Low',
    };

    if (confidenceScore > 0.85) {
        confidenceScoreParams = {
            className: classes.confidenceScoreContainerHighestStyles,
            icon: <ArrowUpward fontSize="small" />,
            text: 'Highest',
        };
    } else if (confidenceScore > 0.7) {
        confidenceScoreParams = {
            className: classes.confidenceScoreContainerHighStyles,
            icon: <CallMade fontSize="small" />,
            text: 'High',
        };
    } else if (confidenceScore > 0.6) {
        confidenceScoreParams = {
            className: classes.confidenceScoreContainerModerateStyles,
            icon: <ArrowForward fontSize="small" />,
            text: 'Moderate',
        };
    }

    return (
        <div className="location-details-container">
            <Typography component="h3" className={classes.locationNameStyles}>
                {name}
                <div
                    className={`${classes.confidenceScoreContainerStyles} ${confidenceScoreParams.className}`}
                >
                    {confidenceScoreParams.icon}
                    <Typography
                        component="div"
                        className={classes.confidenceScoreTextStyles}
                    >
                        {confidenceScoreParams.text}
                    </Typography>
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
