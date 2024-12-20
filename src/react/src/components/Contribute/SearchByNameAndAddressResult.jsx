import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { func, object, bool } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';

import BackToSearchButton from './BackToSearchButton';
import { contributeProductionLocationRoute } from '../../util/constants';
import history from '../../util/history';
import { fetchProductionLocations } from '../../actions/contributeProductionLocation';

const makeSearchByNameAndAddressResultStyles = theme =>
    Object.freeze({
        circularProgressContainerStyles: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: 'calc(100vh - 116px)',
        }),
        mainContainerStyles: Object.freeze({
            // backgroundColor: theme.palette.background.grey,
            padding: '48px 5% 120px 5%',
        }),
        mainTitleStyles: Object.freeze({
            fontWeight: theme.typography.fontWeightExtraBold,
            fontSize: '56px',
            lineHeight: '60px',
            margin: '40px 0 48px 0',
        }),
    });

const SearchByNameAndAddressResult = ({
    data,
    fetching,
    fetchLocations,
    classes,
}) => {
    console.log('data >>>', data);
    console.log('fetching >>>', fetching);
    useEffect(() => {
        fetchLocations();
    }, [fetchLocations]);

    const handleBackToSearchByNameAddress = () => {
        // clearProductionLocations();
        history.push(`${contributeProductionLocationRoute}?tab=name-address`);
    };

    if (fetching) {
        return (
            <div className={classes.circularProgressContainerStyles}>
                <CircularProgress />
            </div>
        );
    }

    return (
        <div className={classes.mainContainerStyles}>
            <BackToSearchButton
                label="Back to ID search"
                handleBackToSearch={handleBackToSearchByNameAddress}
            />
            <Typography component="h1" className={classes.mainTitleStyles}>
                Search results
            </Typography>
            <Typography component="h6">
                We found results that closely match your search criteria. Since
                names and addresses on OS Hub are user-provided, there may be
                slight differences between what you entered and what&apos;s
                shown below. Find the best match for the production location you
                are looking for in the list below, click “Select” to edit the
                name, address and country, and to add more information.
            </Typography>
            <Typography component="h3">Locations</Typography>
        </div>
    );
};

SearchByNameAndAddressResult.defaultProps = {
    data: {},
    fetching: false,
};

SearchByNameAndAddressResult.propTypes = {
    data: object,
    fetching: bool,
    fetchLocations: func.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    contributeProductionLocation: {
        productionLocations: { data, fetching },
    },
}) => ({
    data,
    fetching,
});
const mapDispatchToProps = dispatch => ({
    fetchLocations: () => dispatch(fetchProductionLocations()),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(
    withStyles(makeSearchByNameAndAddressResultStyles)(
        SearchByNameAndAddressResult,
    ),
);
