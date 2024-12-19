import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import { func } from 'prop-types';

import { fetchProductionLocations } from '../../actions/contributeProductionLocation';

const makeSearchByNameAndAddressResultStyles = () => ({});

const SearchByNameAndAddressResult = ({ fetchLocations }) => {
    useEffect(() => {
        fetchLocations();
    }, [fetchLocations]);

    return <div>Search by Name and Address Result</div>;
};

SearchByNameAndAddressResult.propTypes = {
    fetchLocations: func.isRequired,
};

const mapStateToProps = () => ({});

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
