import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { arrayOf, bool, func, string } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import AppGrid from './AppGrid';
import AppOverflow from './AppOverflow';

import ClaimedFacilitiesListTable from './ClaimedFacilitiesListTable';

import {
    fetchClaimedFacilities,
    clearClaimedFacilities,
} from '../actions/claimedFacilities';

import { facilityClaimsListPropType } from '../util/propTypes';
import checkComponentStatus from '../util/checkComponentStatus';

const styles = Object.freeze({
    searchButton: Object.freeze({
        margin: '10px 0',
    }),
});

function ClaimedFacilitiesList({
    data,
    fetching,
    error,
    getClaimed,
    clearClaimed,
    userHasSignedIn,
}) {
    const TITLE = 'My Claimed Facilities';
    useEffect(() => {
        getClaimed();

        return clearClaimed;
    }, [getClaimed, clearClaimed]);

    const {
        renderIfFetchStatus,
        renderIfNotAuthStatus,
        renderIfErrorsStatus,
    } = checkComponentStatus;

    const fetchStatus = renderIfFetchStatus(fetching, TITLE);
    if (fetchStatus) return fetchStatus;
    const nonAuthStatus = renderIfNotAuthStatus(userHasSignedIn, TITLE);
    if (nonAuthStatus) return nonAuthStatus;
    const errorsStatus = renderIfErrorsStatus(error, TITLE);
    if (errorsStatus) return errorsStatus;

    if (!data) {
        return null;
    }

    if (data.length === 0) {
        window.console.log(fetching, data);
        return (
            <AppOverflow>
                <AppGrid title={TITLE}>
                    <div>
                        <Typography
                            variant="body"
                            style={{ padding: '10px 0' }}
                        >
                            You do not have any approved facility claims. Search
                            for your facility and make a request to claim it.
                            Claiming your facility will enable you to add
                            business information, including production details,
                            certifications, minimum order quantities and lead
                            times.
                        </Typography>
                        <Button
                            variant="contained"
                            color="primary"
                            style={styles.searchButton}
                            to="/"
                            href="/"
                        >
                            Search
                        </Button>
                    </div>
                </AppGrid>
            </AppOverflow>
        );
    }

    return (
        <AppOverflow>
            <AppGrid title={TITLE}>
                <ClaimedFacilitiesListTable data={data} />
            </AppGrid>
        </AppOverflow>
    );
}

ClaimedFacilitiesList.defaultProps = {
    data: null,
    error: null,
};

ClaimedFacilitiesList.propTypes = {
    data: facilityClaimsListPropType,
    fetching: bool.isRequired,
    error: arrayOf(string),
    getClaimed: func.isRequired,
    clearClaimed: func.isRequired,
    userHasSignedIn: bool.isRequired,
};

function mapStateToProps({
    claimedFacilities: { data, fetching, error },
    auth: {
        user: { user },
    },
}) {
    return {
        data,
        fetching,
        error,
        userHasSignedIn: !user.isAnon,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        getClaimed: () => dispatch(fetchClaimedFacilities()),
        clearClaimed: () => dispatch(clearClaimedFacilities()),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(ClaimedFacilitiesList);
