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
    handleBackToSearchByNameAddress,
    classes,
}) => {
    console.log('historicalOsIds >>>', historicalOsIds);
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
                    {historicalOsIds ? 'Current OS ID:' : 'OS ID:'} {osId}
                </Typography>
                {historicalOsIds &&
                    historicalOsIds.map(historicalOsId => (
                        <Typography
                            key={historicalOsId}
                            className={classes.locationHistoricalOsIdStyles}
                        >
                            Previous OS ID: {historicalOsId}{' '}
                            <PreviousOsIdTooltip />
                        </Typography>
                    ))}

                <Typography className={classes.locationAddressStyles}>
                    {address}
                </Typography>
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
    historicalOsIds: null,
};

SearchByOsIdSuccessResult.propTypes = {
    name: string.isRequired,
    osId: string.isRequired,
    historicalOsIds: arrayOf(string),
    address: string.isRequired,
    handleBackToSearchByNameAddress: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeSearchByOsIdResultStyles)(
    SearchByOsIdSuccessResult,
);
