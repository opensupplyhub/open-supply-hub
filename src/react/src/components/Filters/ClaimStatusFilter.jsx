import React from 'react';
import { func } from 'prop-types';
import { connect } from 'react-redux';

import StyledSelect from './StyledSelect';

import { updateClaimStatusFilter } from '../../actions/filters';

import { claimStatusOptionsPropType } from '../../util/propTypes';

import { facilityClaimStatusChoices } from '../../util/constants';

const CLAIM_STATUSES = 'CLAIM_STATUSES';

console.log('claimStatusesOptions: ', facilityClaimStatusChoices);

function ClaimStatusFilter({ claimStatuses, updateClaimStatus }) {
    console.log('claim statuses are: ', claimStatuses);

    return (
        <div className="form__field">
            <StyledSelect
                label="Claim Status"
                name={CLAIM_STATUSES}
                options={facilityClaimStatusChoices}
                value={claimStatuses}
                onChange={updateClaimStatus}
            />
        </div>
    );
}

ClaimStatusFilter.propTypes = {
    updateClaimStatus: func.isRequired,
    claimStatuses: claimStatusOptionsPropType.isRequired,
};

function mapStateToProps({ filters: { claimStatuses } }) {
    return {
        claimStatuses,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateClaimStatus: v => dispatch(updateClaimStatusFilter(v)),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(ClaimStatusFilter);
