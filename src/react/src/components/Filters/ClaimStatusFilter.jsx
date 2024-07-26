import React, { useCallback } from 'react';
import { func, bool } from 'prop-types';
import { connect } from 'react-redux';

import StyledSelect from './StyledSelect';

import { updateClaimStatusFilter } from '../../actions/filters';

import {
    claimStatusOptionsPropType,
    filterOptionsPropType,
} from '../../util/propTypes';

const CLAIM_STATUSES = 'CLAIM_STATUSES';

function ClaimStatusFilter({
    isDisabled,
    claimStatuses,
    countriesData,
    claimStatusesOptions,
    updateClaimStatus,
    handleClaimStatusUpdate,
}) {
    const onChangeClaimStatus = useCallback(
        status => {
            handleClaimStatusUpdate(status, countriesData);
            updateClaimStatus(status);
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
                isDisabled={isDisabled}
            />
        </div>
    );
}

ClaimStatusFilter.propTypes = {
    isDisabled: bool.isRequired,
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
        updateClaimStatus: claimStatuses =>
            dispatch(updateClaimStatusFilter(claimStatuses)),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(ClaimStatusFilter);
