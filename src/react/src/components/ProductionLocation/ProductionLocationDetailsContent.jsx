import React from 'react';
import { Redirect, withRouter } from 'react-router';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';

import {
    makeFacilityDetailLinkOnRedirect,
    shouldUseProductionLocationPage,
} from '../../util/util';

const detailsStyles = () => Object.freeze({});

const ProductionLocationDetailsContent = ({
    classes,
    data,
    error,
    location,
    match: {
        params: { osID },
    },
    useProductionLocationPage,
}) => {
    if (error && error.length) {
        return (
            <div className={classes.root}>
                <ul>
                    {error.map(err => (
                        <li key={err} className={classes.error}>
                            {err}
                        </li>
                    ))}
                </ul>
            </div>
        );
    }

    if (data?.id && data?.id !== osID) {
        // When redirecting to a facility alias from a deleted facility,
        // the OS ID in the url will not match the facility data id;
        // redirect to the appropriate facility URL.

        // TODO: Refactor this logic
        return (
            <Redirect
                to={{
                    pathname: makeFacilityDetailLinkOnRedirect(
                        data.id,
                        location.search,
                        useProductionLocationPage,
                    ),
                }}
            />
        );
    }

    return (
        <div className={classes.root}>Production Location Details Content</div>
    );
};

function mapStateToProps({
    facilities: {
        singleFacility: { data, fetching, error },
    },
    embeddedMap: { embed, config },
    filters: { contributors },
    featureFlags,
}) {
    return {
        data,
        fetching,
        error,
        embed: !!embed,
        embedContributor: config?.contributor_name,
        embedConfig: config,
        contributors,
        hideSectorData: embed ? config.hide_sector_data : false,
        useProductionLocationPage: shouldUseProductionLocationPage(
            featureFlags,
        ),
    };
}

export default withRouter(
    connect(mapStateToProps)(
        withStyles(detailsStyles)(ProductionLocationDetailsContent),
    ),
);
