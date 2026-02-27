import get from 'lodash/get';
import includes from 'lodash/includes';

import { facilityClaimStatusChoicesEnum } from '../../../../util/constants';

const shouldShowDisputeClaim = (data, osID, user) => {
    const isPendingClaim =
        get(data, 'properties.claim_info.status') ===
        facilityClaimStatusChoicesEnum.PENDING;
    const isClaimed = !isPendingClaim && !!get(data, 'properties.claim_info');

    const {
        approved: currentUserApprovedClaimedFacilities = [],
        pending: currentUserPendingClaimedFacilities = [],
    } = get(user, 'user.claimed_facility_ids', { approved: [], pending: [] });

    const facilityIsClaimedByCurrentUser = includes(
        currentUserApprovedClaimedFacilities,
        osID,
    );

    const userHasPendingFacilityClaim =
        includes(currentUserPendingClaimedFacilities, osID) &&
        !facilityIsClaimedByCurrentUser;

    return (
        !facilityIsClaimedByCurrentUser &&
        !userHasPendingFacilityClaim &&
        isClaimed
    );
};

export default shouldShowDisputeClaim;
