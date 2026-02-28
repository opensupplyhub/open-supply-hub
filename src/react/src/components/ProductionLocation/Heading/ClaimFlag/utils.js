import moment from 'moment';

export const getClaimFlagStateClassName = (
    classes,
    isClaimed,
    isPending,
    { base, claimed, pending, unclaimed },
) => {
    const names = [classes[base]];
    if (isClaimed) names.push(classes[claimed]);
    else if (isPending) names.push(classes[pending]);
    else names.push(classes[unclaimed]);
    return names.filter(Boolean).join(' ');
};

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
    if (!moment(date).isValid()) return null;
    return moment(date).format('LL');
};
