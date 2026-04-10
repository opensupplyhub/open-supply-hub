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

export const sendLocationPartnerProfileLinkClick = p => {
    const { destinationUrl, destinationDomain } = getDestinationParts(
        p.destinationUrl,
    );
    sendGaEvent(GA_EVENTS.LOCATION_PARTNER_PROFILE_LINK_CLICK, {
        contributor_name: p.contributorName,
        partner_group: p.partnerGroup,
        link_placement: p.linkPlacement,
        destination_url: destinationUrl,
        destination_domain: destinationDomain,
        os_id: p.osId,
        partner_field_name: p.partnerFieldName.toUpperCase(),
        user_id: p.userId,
    });
};

export const sendLocationPartnerExternalLinkClick = p => {
    const { destinationUrl, destinationDomain } = getDestinationParts(
        p.destinationUrl,
    );
    sendGaEvent(GA_EVENTS.LOCATION_PARTNER_EXTERNAL_LINK_CLICK, {
        contributor_name: p.contributorName,
        partner_group: p.partnerGroup,
        link_placement: p.linkPlacement,
        destination_url: destinationUrl,
        destination_domain: destinationDomain,
        os_id: p.osId,
        partner_field_name: p.partnerFieldName.toUpperCase(),
        user_id: p.userId,
    });
};

export const sendContributorExternalWebsiteLinkClick = p => {
    const { destinationUrl, destinationDomain } = getDestinationParts(
        p.destinationUrl,
    );
    sendGaEvent(GA_EVENTS.CONTRIBUTOR_EXTERNAL_WEBSITE_LINK_CLICK, {
        contributor_name: p.contributorName,
        destination_url: destinationUrl,
        destination_domain: destinationDomain,
        user_id: p.userId,
    });
};
