import moment from 'moment';

export const getMainText = (isClaimed, isPending) => {
    if (isClaimed) {
        return 'CLAIMED PROFILE';
    }
    if (isPending) {
        return 'There is a pending claim for this production location';
    }
    return 'This production location has not been claimed';
};

export const formatClaimDate = date => {
    if (date == null || date === '') return null;
    const m = moment(date);
    if (!m.isValid()) return null;
    //  Format claim date for display (e.g. "November 15, 2022").
    return m.format('LL');
};
