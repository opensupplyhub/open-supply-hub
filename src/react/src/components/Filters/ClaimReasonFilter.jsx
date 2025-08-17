import React, { useCallback } from 'react';
import { func, bool } from 'prop-types';
import { connect } from 'react-redux';

import StyledSelect from './StyledSelect';

import { updateClaimReasonFilter } from '../../actions/filters';

import { filterOptionsPropType } from '../../util/propTypes';

const CLAIM_REASONS = 'CLAIM_REASONS';

function ClaimReasonFilter({
    isDisabled,
    claimReasons,
    claimReasonsOptions,
    updateClaimReason,
    handleClaimReasonUpdate,
}) {
    const onChangeClaimReason = useCallback(
        reasons => {
            handleClaimReasonUpdate(reasons);
            updateClaimReason(reasons);
        },
        [claimReasons, handleClaimReasonUpdate, updateClaimReason],
    );

    return (
        <div className="form__field">
            <StyledSelect
                label="Claim Reason"
                name={CLAIM_REASONS}
                options={claimReasonsOptions?.data || []}
                value={claimReasons}
                onChange={onChangeClaimReason}
                isDisabled={isDisabled}
            />
        </div>
    );
}

ClaimReasonFilter.propTypes = {
    isDisabled: bool.isRequired,
    updateClaimReason: func.isRequired,
    claimReasons: filterOptionsPropType.isRequired,
    claimReasonsOptions: filterOptionsPropType.isRequired,
    handleClaimReasonUpdate: func.isRequired,
};

const mapStateToProps = ({
    filters: { claimReasons },
    filterOptions: { claimReasons: claimReasonsOptions },
}) => ({
    claimReasons,
    claimReasonsOptions,
});

const mapDispatchToProps = dispatch => ({
    updateClaimReason: claimReasons =>
        dispatch(updateClaimReasonFilter(claimReasons)),
});

export default connect(mapStateToProps, mapDispatchToProps)(ClaimReasonFilter);
