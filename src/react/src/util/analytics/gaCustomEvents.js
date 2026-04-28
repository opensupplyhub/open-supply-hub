/*
 * Google Analytics custom events sent via gtag after the user has accepted
 * tracking (see consent.js). Helpers here no-op until consent is granted.
 */

import { userHasAcceptedGATracking } from './consent';
import { GA_EVENTS, GA_LINK_PLACEMENT } from './constants';

export { GA_EVENTS, GA_LINK_PLACEMENT };

export const getDestinationParts = (href, baseUrl) => {
    try {
        const base =
            baseUrl ||
            (typeof window !== 'undefined' ? window.location.href : undefined);
        const url = new URL(href, base);

        return {
            destinationUrl: url.href,
            destinationDomain: url.hostname,
        };
    } catch {
        return { destinationUrl: href, destinationDomain: '' };
    }
};

export const classifySpotlightSourceByLinkHref = (href, baseUrl) => {
    try {
        const base =
            baseUrl ||
            (typeof window !== 'undefined' ? window.location.href : undefined);
        const url = new URL(href, base);
        const pageOrigin =
            typeof window !== 'undefined'
                ? window.location.origin
                : new URL(base).origin;

        if (url.origin !== pageOrigin) {
            return { kind: 'external', destinationUrl: url.href };
        }

        const profileMatch = url.pathname.match(/^\/profile\/([^/]+)\/?$/);
        if (profileMatch) {
            return {
                kind: 'profile',
                destinationUrl: url.href,
                profileUserId: profileMatch[1],
            };
        }

        return { kind: 'external', destinationUrl: url.href };
    } catch {
        return { kind: 'invalid' };
    }
};

const sendGaEvent = (eventName, params) => {
    if (!userHasAcceptedGATracking()) {
        return;
    }
    if (typeof window === 'undefined' || typeof window.gtag !== 'function') {
        return;
    }
    const payload = { ...params };
    delete payload.page_location;
    window.gtag('event', eventName, payload);
};

export const sendLocationPartnerProfileLinkClick = profileLinkPayload => {
    const { destinationUrl, destinationDomain } = getDestinationParts(
        profileLinkPayload.destinationUrl,
    );
    sendGaEvent(GA_EVENTS.LOCATION_PARTNER_PROFILE_LINK_CLICK, {
        contributor_name: profileLinkPayload.contributorName,
        partner_group: profileLinkPayload.partnerGroup,
        link_placement: profileLinkPayload.linkPlacement,
        destination_url: destinationUrl,
        destination_domain: destinationDomain,
        os_id: profileLinkPayload.osId,
        partner_field_name: profileLinkPayload.partnerFieldName.toUpperCase(),
        contributor_user_id: profileLinkPayload.userId,
        viewer_user_id: profileLinkPayload.viewerUserId,
    });
};

export const sendLocationPartnerExternalLinkClick = externalLinkPayload => {
    const { destinationUrl, destinationDomain } = getDestinationParts(
        externalLinkPayload.destinationUrl,
    );
    sendGaEvent(GA_EVENTS.LOCATION_PARTNER_EXTERNAL_LINK_CLICK, {
        contributor_name: externalLinkPayload.contributorName,
        partner_group: externalLinkPayload.partnerGroup,
        link_placement: externalLinkPayload.linkPlacement,
        destination_url: destinationUrl,
        destination_domain: destinationDomain,
        os_id: externalLinkPayload.osId,
        partner_field_name: externalLinkPayload.partnerFieldName.toUpperCase(),
        contributor_user_id: externalLinkPayload.userId,
        viewer_user_id: externalLinkPayload.viewerUserId,
    });
};

export const sendContributorExternalWebsiteLinkClick = contributorWebsitePayload => {
    const { destinationUrl, destinationDomain } = getDestinationParts(
        contributorWebsitePayload.destinationUrl,
    );
    sendGaEvent(GA_EVENTS.CONTRIBUTOR_EXTERNAL_WEBSITE_LINK_CLICK, {
        contributor_name: contributorWebsitePayload.contributorName,
        destination_url: destinationUrl,
        destination_domain: destinationDomain,
        contributor_user_id: contributorWebsitePayload.userId,
        viewer_user_id: contributorWebsitePayload.viewerUserId,
    });
};
