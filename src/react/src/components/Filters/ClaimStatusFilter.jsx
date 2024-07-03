/* eslint no-unused-vars: 0 */
import React, { useCallback } from 'react';
import { func } from 'prop-types';
import { connect } from 'react-redux';

import StyledSelect from './StyledSelect';

import { updateClaimStatusFilter } from '../../actions/filters';

import {
    claimStatusOptionsPropType,
    filterOptionsPropType,
} from '../../util/propTypes';

import { fetchFacilityClaims } from '../../actions/claimFacilityDashboard';

const CLAIM_STATUSES = 'CLAIM_STATUSES';

function ClaimStatusFilter({
    claimStatuses,
    claimStatusesOptions,
    getClaims,
    updateClaimStatus,
    handleClaimStatusUpdate,
}) {
    const onChangeClaimStatus = useCallback(
        s => {
            handleClaimStatusUpdate(s);
            updateClaimStatus(s);
            getClaims();
        },
        [claimStatuses],
    );

    return (
        <div className="form__field">
            <StyledSelect
                label="Claim Status"
                name={CLAIM_STATUSES}
                options={claimStatusesOptions.data || []}
                value={claimStatuses}
                onChange={onChangeClaimStatus}
            />
        </div>
    );
}

ClaimStatusFilter.propTypes = {
    getClaims: func.isRequired,
    updateClaimStatus: func.isRequired,
    claimStatuses: claimStatusOptionsPropType.isRequired,
    claimStatusesOptions: filterOptionsPropType.isRequired,
};

function mapStateToProps({
    filters: { claimStatuses },
    filterOptions: { claimStatuses: claimStatusesOptions },
}) {
    return {
        claimStatuses,
        claimStatusesOptions,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        getClaims: () => dispatch(fetchFacilityClaims()),
        updateClaimStatus: v => dispatch(updateClaimStatusFilter(v)),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(ClaimStatusFilter);
