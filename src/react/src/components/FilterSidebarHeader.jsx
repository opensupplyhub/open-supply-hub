import React from 'react';
import { object, bool, number, string } from 'prop-types';
import { withStyles, Grid } from '@material-ui/core';
import { connect } from 'react-redux';
import { get } from 'lodash';

import FacilityIcon from './FacilityIcon';
import ResultsSortDropdown from './ResultsSortDropdown';
import ShowOnly from './ShowOnly';
import DownloadLimitInfo from './DownloadLimitInfo';
import FeatureFlag from './FeatureFlag';
import { filterSidebarHeaderStyles } from '../util/styles';
import { PRIVATE_INSTANCE } from '../util/constants';
import { userPropType } from '../util/propTypes';

const FilterSidebarHeader = ({
    multiLine,
    facilitiesCount,
    unionLinkedCount,
    classes,
    embed,
    user,
    isSameContributor,
    hasAppliedFilters,
}) => (
    <div className={`${classes.header} results-height-subtract`}>
        <h1 className={classes.headerText}>
            <FacilityIcon /> Facilities
        </h1>
        <Grid container justify="space-between">
            <Grid item className={multiLine ? classes.numberResults : ''}>
                {facilitiesCount} results
                {unionLinkedCount > 0 &&
                    ` (including ${unionLinkedCount} union-linked ${
                        unionLinkedCount === 1 ? 'location' : 'locations'
                    })`}
            </Grid>
            <ShowOnly when={!embed}>
                <Grid item>
                    <ResultsSortDropdown />
                </Grid>
            </ShowOnly>
        </Grid>
        <ShowOnly
            when={
                !embed &&
                !user.isAnon &&
                facilitiesCount > user.allowed_records_number &&
                hasAppliedFilters
            }
        >
            <FeatureFlag
                flag={PRIVATE_INSTANCE}
                isSameContributor={isSameContributor}
                alternative={<DownloadLimitInfo />}
            >
                <></>
            </FeatureFlag>
        </ShowOnly>
    </div>
);

FilterSidebarHeader.defaultProps = {
    hasAppliedFilters: false,
    unionLinkedCount: 0,
};

FilterSidebarHeader.propTypes = {
    multiLine: bool.isRequired,
    facilitiesCount: number.isRequired,
    unionLinkedCount: number,
    embed: string.isRequired,
    classes: object.isRequired,
    user: userPropType.isRequired,
    isSameContributor: bool.isRequired,
    hasAppliedFilters: bool,
};

const mapStateToProps = ({
    embeddedMap: { embed },
    facilities: {
        facilities: { data: facilities, hasAppliedFilters },
    },
    auth: {
        user: { user },
    },
}) => ({
    embed,
    facilitiesCount: get(facilities, 'count', null),
    unionLinkedCount: get(facilities, 'excluded_from_download_count', 0),
    user,
    isSameContributor: get(facilities, 'is_same_contributor', false),
    hasAppliedFilters,
});

export default withStyles(filterSidebarHeaderStyles)(
    connect(mapStateToProps)(FilterSidebarHeader),
);
