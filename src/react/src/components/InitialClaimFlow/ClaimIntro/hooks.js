import { useEffect } from 'react';

/**
 * Hook to manage OS ID tracking and form reset logic.
 * Updates the OS ID to claim in Redux and resets the form when
 * the user accesses the claim intro from a different OS ID.
 */
const useClaimIntroOsIdTracking = (
    osID,
    osIdToClaim,
    updateOsId,
    resetForm,
) => {
    useEffect(() => {
        // Update the OS ID to claim in Redux for further checking whether
        // form needs to be reset when user accesses the form from a
        // different OS ID.
        if (!osIdToClaim) {
            updateOsId(osID);
        }

        if (osIdToClaim && osIdToClaim !== osID) {
            resetForm();
        }
    }, [osID, osIdToClaim, updateOsId, resetForm]);
};

export default useClaimIntroOsIdTracking;
