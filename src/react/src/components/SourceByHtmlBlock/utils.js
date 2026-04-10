import {
    classifySpotlightSourceByLinkHref,
    sendLocationPartnerExternalLinkClick,
    sendLocationPartnerProfileLinkClick,
} from '../../util/analytics/gaCustomEvents';

const handleSourceByHtmlLinkClick = (clickEvent, gaSpotlightAnalytics) => {
    if (!gaSpotlightAnalytics) {
        return;
    }
    const eventTarget = clickEvent.target;
    const element =
        eventTarget instanceof Element
            ? eventTarget
            : eventTarget?.parentElement || null;
    const anchor = element?.closest?.('a');
    if (!anchor) {
        return;
    }
    const href = anchor.getAttribute('href');
    if (!href) {
        return;
    }

    const classified = classifySpotlightSourceByLinkHref(href);
    if (classified.kind === 'invalid') {
        return;
    }

    const common = {
        contributorName: gaSpotlightAnalytics.contributor_name,
        partnerGroup: gaSpotlightAnalytics.partner_group,
        linkPlacement: gaSpotlightAnalytics.link_placement,
        destinationUrl: classified.destinationUrl,
        osId: gaSpotlightAnalytics.os_id,
        partnerFieldName: gaSpotlightAnalytics.partner_field_name,
    };

    if (classified.kind === 'profile') {
        sendLocationPartnerProfileLinkClick({
            ...common,
            userId: classified.profileUserId,
        });
    } else {
        sendLocationPartnerExternalLinkClick({
            ...common,
            userId: gaSpotlightAnalytics.user_id,
        });
    }
};

export default handleSourceByHtmlLinkClick;
