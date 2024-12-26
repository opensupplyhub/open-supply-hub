import React, { useEffect } from 'react';
import { array, bool, func, object } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import BackToSearchButton from './BackToSearchButton';
import SearchByNameAndAddressSuccessResult from './SearchByNameAndAddressSuccessResult';
import SearchByNameAndAddressNotFoundResult from './SearchByNameAndAddressNotFoundResult';
import { contributeProductionLocationRoute } from '../../util/constants';
import history from '../../util/history';
import { fetchProductionLocations } from '../../actions/contributeProductionLocation';

const makeSearchByNameAndAddressResultStyles = () =>
    Object.freeze({
        circularProgressContainerStyles: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: 'calc(100vh - 116px)',
        }),
        backToSearchButtonContainerStyles: Object.freeze({
            padding: '48px 5% 0 5%',
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

    const count = data?.data?.length || 0;

    if (fetching) {
        return (
            <div className={classes.circularProgressContainerStyles}>
                <CircularProgress />
            </div>
        );
    }

    return (
        <>
            <div className={classes.backToSearchButtonContainerStyles}>
                <BackToSearchButton
                    label="Back to Search"
                    handleBackToSearch={handleBackToSearchByNameAddress}
                />
            </div>
            {count > 0 ? (
                <SearchByNameAndAddressSuccessResult data={data} />
            ) : (
                <SearchByNameAndAddressNotFoundResult />
            )}
        </>
    );
};

SearchByNameAndAddressResult.defaultProps = {
    data: [],
    fetching: false,
};

SearchByNameAndAddressResult.propTypes = {
    data: array,
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
