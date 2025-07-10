import React from 'react';

import {
    FREE_FACILITIES_DOWNLOAD_LIMIT,
    FACILITIES_DOWNLOAD_LIMIT,
} from '../util/constants';

const getTooltipForFacilitiesDownload = ({
    user,
    userAllowedRecords,
    isEmbedded,
    isPrivateInstance,
    upgrade,
    classes,
    facilitiesCount,
}) => {
    const tooltipTexts = {
        availableDownloads: `Registered users can download up to ${FREE_FACILITIES_DOWNLOAD_LIMIT} production
        locations annually for free. This account has ${userAllowedRecords} production locations available to
        download. Additional downloads are available for purchase.`,
        outOfDownloads: `You've reached your annual download limit of ${FREE_FACILITIES_DOWNLOAD_LIMIT} production
        locations. Purchase additional downloads to download more data.`,
        limitExceededByResults: `You are trying to download ${facilitiesCount} production locations but this account only has
        ${userAllowedRecords} production locations available to download. Purchase additional downloads to
        continue.`,
        anonymousUser: 'Log in or sign up to download this dataset.',
        embeddedOrPrivateInstance: `Downloads are supported for searches resulting in ${FACILITIES_DOWNLOAD_LIMIT} production locations or less.`,
    };

    // Determine base tooltip.
    let tooltipText;

    if (isEmbedded || isPrivateInstance) {
        tooltipText = tooltipTexts.embeddedOrPrivateInstance;
    } else if (upgrade) {
        tooltipText =
            userAllowedRecords === 0
                ? tooltipTexts.outOfDownloads
                : tooltipTexts.limitExceededByResults;
    } else {
        tooltipText = tooltipTexts.availableDownloads;
    }

    // Adjust for anonymous users.
    let finalTooltip;

    if (user.isAnon && !isEmbedded && !isPrivateInstance) {
        finalTooltip = tooltipTexts.anonymousUser;
    } else if (user.isAnon && isPrivateInstance) {
        finalTooltip = `${tooltipText} ${tooltipTexts.anonymousUser}`;
    } else {
        finalTooltip = tooltipText;
    }

    return <p className={classes.downloadTooltip}>{finalTooltip}</p>;
};

export default getTooltipForFacilitiesDownload;
