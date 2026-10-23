import { STATUS_CLAIMED, STATUS_CROWDSOURCED } from './constants';

const getStatusChipClass = (statusLabel, classes) => {
    if (statusLabel === STATUS_CLAIMED) return classes.claimedChip;
    if (statusLabel === STATUS_CROWDSOURCED) return classes.crowdsourcedChip;
    return null;
};

export default getStatusChipClass;
