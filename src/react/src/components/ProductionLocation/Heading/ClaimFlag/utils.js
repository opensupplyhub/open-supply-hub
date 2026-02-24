export const getBackgroundColorClass = (isClaimed, isPending) => {
    if (isClaimed) return 'rootClaimed';
    if (isPending) return 'rootPending';
    return 'rootUnclaimed';
};

export const getMainText = (isClaimed, isPending) => {
    if (isClaimed) {
        return 'This production location has been claimed by an owner or manager';
    }
    if (isPending) {
        return 'There is a pending claim for this production location';
    }
    return 'This production location has not been claimed';
};
