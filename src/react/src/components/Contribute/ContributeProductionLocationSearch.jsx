import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { useLocation } from 'react-router-dom';
import { object, func, bool } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import SearchByOsIdResult from './SearchByOsIdResult';
import { fetchProductionLocationByOsId } from '../../actions/contributeProductionLocation';

const makeContributeProductionLocationSearchStyles = theme => ({
    container: {
        backgroundColor: theme.palette.background.grey,
        padding: '48px 5% 120px 5%',
    },
});

const ContributeProductionLocationSearch = ({
    data,
    fetching,
    fetchProductionLocation,
    classes,
}) => {
    const location = useLocation();
    console.log('location >>>', location);

    const getQueryParams = search => new URLSearchParams(search);

    useEffect(() => {
        const queryParams = getQueryParams(location.search);
        const osId = queryParams.get('os_id');

        if (osId) {
            fetchProductionLocation(osId);
        }
    }, [location.search, fetchProductionLocation]);

    if (fetching) {
        return (
            <div
                styles={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    height: '100vh',
                }}
            >
                <CircularProgress />
            </div>
        );
    }

    return (
        <div className={classes.container}>
            <SearchByOsIdResult data={data} />
        </div>
    );
};

ContributeProductionLocationSearch.propTypes = {
    data: object.isRequired,
    fetching: bool.isRequired,
    fetchProductionLocation: func.isRequired,
};

const mapStateToProps = ({
    contributeProductionLocation: {
        singleProductionLocation: { data, fetching },
    },
}) => ({
    data,
    fetching,
});

const mapDispatchToProps = {
    fetchProductionLocation: fetchProductionLocationByOsId,
};

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(
    withStyles(makeContributeProductionLocationSearchStyles)(
        ContributeProductionLocationSearch,
    ),
);
