import React, { useCallback } from 'react';
import { array, func } from 'prop-types';
import { connect } from 'react-redux';

import StyledSelect from './StyledSelect';

import { updateClaimStatusFilter } from '../../actions/filters';

import { claimStatusOptionsPropType } from '../../util/propTypes';

const CLAIM_STATUSES = 'CLAIM_STATUSES';

function ClaimStatusFilter({
    claimStatuses,
    claimStatusesOptions,
    updateClaimStatus,
    handleClaimStatusUpdate,
}) {
    const onChangeClaimStatus = useCallback(
        s => {
            console.log('s is ', s);
            handleClaimStatusUpdate(s);
            updateClaimStatus(s);
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
    updateClaimStatus: func.isRequired,
    claimStatuses: claimStatusOptionsPropType.isRequired,
    claimStatusesOptions: array.isRequired,
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
