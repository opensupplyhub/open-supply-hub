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
    classes,
    embed,
    user,
    isSameContributor,
}) => (
    <div className={`${classes.header} results-height-subtract`}>
        <h1 className={classes.headerText}>
            <FacilityIcon /> Facilities
        </h1>
        <Grid container justify="space-between">
            <Grid item className={multiLine ? classes.numberResults : ''}>
                {facilitiesCount} results
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
                facilitiesCount > user.allowed_records_number
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

FilterSidebarHeader.propTypes = {
    multiLine: bool.isRequired,
    facilitiesCount: number.isRequired,
    embed: string.isRequired,
    classes: object.isRequired,
    user: userPropType.isRequired,
    isSameContributor: bool.isRequired,
};

const mapStateToProps = ({
    embeddedMap: { embed },
    facilities: {
        facilities: { data: facilities },
    },
    auth: {
        user: { user },
    },
}) => ({
    embed,
    facilitiesCount: get(facilities, 'count', null),
    user,
    isSameContributor: get(facilities, 'is_same_contributor', false),
});

export default withStyles(filterSidebarHeaderStyles)(
    connect(mapStateToProps)(FilterSidebarHeader),
);
