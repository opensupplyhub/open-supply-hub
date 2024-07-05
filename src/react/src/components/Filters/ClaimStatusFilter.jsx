import React, { useCallback } from 'react';
import { func } from 'prop-types';
import { connect } from 'react-redux';

import StyledSelect from './StyledSelect';

import { updateClaimStatusFilter } from '../../actions/filters';

import {
    claimStatusOptionsPropType,
    filterOptionsPropType,
} from '../../util/propTypes';

const CLAIM_STATUSES = 'CLAIM_STATUSES';

function ClaimStatusFilter({
    claimStatuses,
    countriesData,
    claimStatusesOptions,
    updateClaimStatus,
    handleClaimStatusUpdate,
}) {
    const onChangeClaimStatus = useCallback(
        s => {
            handleClaimStatusUpdate(s, countriesData);
            updateClaimStatus(s);
        },
        [claimStatuses, countriesData],
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
        updateClaimStatus: v => dispatch(updateClaimStatusFilter(v)),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(ClaimStatusFilter);
