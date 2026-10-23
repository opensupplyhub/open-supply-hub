import {
    STATUS_CLAIMED,
    STATUS_CROWDSOURCED,
    STATUS_MAPPED,
} from './constants';

const getStatusChipClass = (statusLabel, classes) => {
    if (statusLabel === STATUS_CLAIMED) return classes.claimedChip;
    if (statusLabel === STATUS_CROWDSOURCED) return classes.crowdsourcedChip;
    if (statusLabel === STATUS_MAPPED) return classes.mappedChip;
    return null;
};

export default getStatusChipClass;
