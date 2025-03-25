import React, { Component } from 'react';
import { arrayOf, bool, func, string } from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';

import AppGrid from './AppGrid';
import AppOverflow from './AppOverflow';
import FacilityListsEmpty from './FacilityListsEmpty';
import FacilityListsTable from './FacilityListsTable';
import ShowOnly from './ShowOnly';

import {
    fetchUserFacilityLists,
    resetUserFacilityLists,
} from '../actions/facilityLists';

import { claimedFacilitiesRoute, InfoLink, InfoPaths } from '../util/constants';
import { facilityListPropType } from '../util/propTypes';
import {
    LoadingIndicator,
    AuthNotice,
    ErrorsList,
} from './CheckComponentStatus';

class FacilityLists extends Component {
    componentDidMount() {
        return this.props.fetchLists();
    }

    componentWillUnmount() {
        return this.props.resetLists();
    }

    render() {
        const {
            facilityLists,
            fetching,
            errors,
            userHasSignedIn,
            fetchingSessionSignIn,
            myFacilitiesRoute,
        } = this.props;
        const TITLE = 'My Lists';

        if (fetching || fetchingSessionSignIn) {
            return <LoadingIndicator title={TITLE} />;
        }

        if (!userHasSignedIn) {
            return (
                <AuthNotice
                    title={TITLE}
                    text="Sign in to view your Open Supply Hub lists"
                />
            );
        }

        if (errors && errors.length > 0) {
            return <ErrorsList title={TITLE} errors={errors} />;
        }

        const tableComponent =
            facilityLists && facilityLists.length ? (
                <FacilityListsTable facilityLists={facilityLists} />
            ) : (
                <FacilityListsEmpty />
            );

        return (
            <AppOverflow>
                <AppGrid title="My Lists" style={{ marginBottom: '100px' }}>
                    <ShowOnly
                        when={!!myFacilitiesRoute && !!facilityLists.length}
                    >
                        <Link
                            to={claimedFacilitiesRoute}
                            href={claimedFacilitiesRoute}
                            style={{ paddingBottom: '20px' }}
                        >
                            View my facilities
                        </Link>
                    </ShowOnly>
                    <p>
                        Data points submitted beyond facility name and address
                        are processing, even if they do not appear on this page.
                        Once your list has processed, you will be able to view
                        and search these data points on facility profiles, as
                        well as in downloads from the platform. Read about how
                        your facility data is{' '}
                        <a
                            href={`${InfoLink}/${InfoPaths.dataQuality}`}
                            target="_blank"
                            rel="noreferrer"
                        >
                            processed and matched
                        </a>
                        .
                    </p>
                    {tableComponent}
                </AppGrid>
            </AppOverflow>
        );
    }
}

FacilityLists.defaultProps = {
    errors: null,
};

FacilityLists.propTypes = {
    facilityLists: arrayOf(facilityListPropType).isRequired,
    fetching: bool.isRequired,
    errors: arrayOf(string),
    fetchLists: func.isRequired,
    resetLists: func.isRequired,
    userHasSignedIn: bool.isRequired,
    fetchingSessionSignIn: bool.isRequired,
};

function mapStateToProps({
    facilityLists: { facilityLists, fetching, error },
    auth: {
        user: { user },
        session: { fetching: fetchingSessionSignIn },
    },
}) {
    return {
        facilityLists,
        fetching,
        errors: error,
        userHasSignedIn: !user.isAnon,
        fetchingSessionSignIn,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        fetchLists: () => dispatch(fetchUserFacilityLists()),
        resetLists: () => dispatch(resetUserFacilityLists()),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(FacilityLists);
