/* eslint-env jest */

import { userHasAcceptedGATracking } from '../../util/analytics/consent';
import {
    GA_EVENTS,
    GA_LINK_PLACEMENT,
    getDestinationParts,
    classifySpotlightSourceByLinkHref,
    sendLocationPartnerProfileLinkClick,
    sendLocationPartnerExternalLinkClick,
    sendContributorExternalWebsiteLinkClick,
} from '../../util/analytics/gaCustomEvents';

jest.mock('../../util/analytics/consent', () => ({
    userHasAcceptedGATracking: jest.fn(),
}));

describe('getDestinationParts', () => {
    it('resolves an absolute https URL and returns href and hostname', () => {
        const result = getDestinationParts('https://partner.example/path?q=1');

        expect(result).toEqual({
            destinationUrl: 'https://partner.example/path?q=1',
            destinationDomain: 'partner.example',
        });
    });

    it('resolves a relative path when baseUrl is provided', () => {
        const result = getDestinationParts('/foo/bar', 'https://app.example/pl/1');

        expect(result.destinationUrl).toBe('https://app.example/foo/bar');
        expect(result.destinationDomain).toBe('app.example');
    });

    it('falls back to raw href and empty domain when URL parsing throws', () => {
        const invalidAbsolute = 'http://';
        const result = getDestinationParts(invalidAbsolute);

        expect(result).toEqual({
            destinationUrl: invalidAbsolute,
            destinationDomain: '',
        });
    });
});

describe('classifySpotlightSourceByLinkHref', () => {
    const base = 'https://app.example/production-locations/abc123';

    beforeEach(() => {
        delete global.window.location;
        global.window.location = new URL(
            'https://app.example/production-locations/abc123',
        );
    });

    it('returns external when origin differs from page origin', () => {
        const result = classifySpotlightSourceByLinkHref(
            'https://other.example/page',
            base,
        );

        expect(result).toEqual({
            kind: 'external',
            destinationUrl: 'https://other.example/page',
        });
    });

    it('returns profile when same origin and path matches /profile/:id', () => {
        const result = classifySpotlightSourceByLinkHref(
            'https://app.example/profile/user-99',
            base,
        );

        expect(result).toEqual({
            kind: 'profile',
            destinationUrl: 'https://app.example/profile/user-99',
            profileUserId: 'user-99',
        });
    });

    it('returns external for same-origin non-profile paths', () => {
        const result = classifySpotlightSourceByLinkHref(
            'https://app.example/some/other/path',
            base,
        );

        expect(result).toEqual({
            kind: 'external',
            destinationUrl: 'https://app.example/some/other/path',
        });
    });

    it('returns invalid when href cannot be parsed', () => {
        expect(classifySpotlightSourceByLinkHref('http://')).toEqual({
            kind: 'invalid',
        });
    });
});

describe('sendLocationPartnerProfileLinkClick', () => {
    beforeEach(() => {
        userHasAcceptedGATracking.mockReturnValue(true);
        global.window.gtag = jest.fn();
        delete global.window.location;
        global.window.location = new URL(
            'https://app.example/production-locations/os-1',
        );
    });

    it('does not call gtag when tracking consent is not granted', () => {
        userHasAcceptedGATracking.mockReturnValue(false);
        global.window.gtag = jest.fn();

        sendLocationPartnerProfileLinkClick({
            contributorName: 'A',
            partnerGroup: 'G',
            linkPlacement: GA_LINK_PLACEMENT.CONTRIBUTION_LINE,
            destinationUrl: 'https://x.example/p',
            osId: 'os-1',
            partnerFieldName: 'website',
            userId: 'u1',
        });

        expect(global.window.gtag).not.toHaveBeenCalled();
    });

    it('does not call gtag when window.gtag is not a function', () => {
        global.window.gtag = undefined;

        sendLocationPartnerProfileLinkClick({
            contributorName: 'A',
            partnerGroup: 'G',
            linkPlacement: GA_LINK_PLACEMENT.CONTRIBUTION_LINE,
            destinationUrl: 'https://x.example/p',
            osId: 'os-1',
            partnerFieldName: 'website',
            userId: 'u1',
        });

        expect(userHasAcceptedGATracking).toHaveBeenCalled();
    });

    it('sends LOCATION_PARTNER_PROFILE_LINK_CLICK with snake_case params and uppercased partner_field_name', () => {
        sendLocationPartnerProfileLinkClick({
            contributorName: 'Contributor',
            partnerGroup: 'Group',
            linkPlacement: GA_LINK_PLACEMENT.CONTRIBUTIONS_DRAWER,
            destinationUrl: 'https://partner.example/profile/me',
            osId: 'os-42',
            partnerFieldName: 'source_url',
            userId: '99',
        });

        expect(global.window.gtag).toHaveBeenCalledTimes(1);
        expect(global.window.gtag).toHaveBeenCalledWith(
            'event',
            GA_EVENTS.LOCATION_PARTNER_PROFILE_LINK_CLICK,
            {
                contributor_name: 'Contributor',
                partner_group: 'Group',
                link_placement: GA_LINK_PLACEMENT.CONTRIBUTIONS_DRAWER,
                destination_url: 'https://partner.example/profile/me',
                destination_domain: 'partner.example',
                os_id: 'os-42',
                partner_field_name: 'SOURCE_URL',
                user_id: '99',
            },
        );
    });
});

describe('sendLocationPartnerExternalLinkClick', () => {
    beforeEach(() => {
        userHasAcceptedGATracking.mockReturnValue(true);
        global.window.gtag = jest.fn();
        global.window.location = new URL('https://app.example/pl/x');
    });

    it('sends LOCATION_PARTNER_EXTERNAL_LINK_CLICK with expected payload', () => {
        sendLocationPartnerExternalLinkClick({
            contributorName: 'C',
            partnerGroup: 'PG',
            linkPlacement: GA_LINK_PLACEMENT.CONTRIBUTION_LINE,
            destinationUrl: 'https://ext.example',
            osId: 'os-1',
            partnerFieldName: 'doc',
            userId: '1',
        });

        expect(global.window.gtag).toHaveBeenCalledWith(
            'event',
            GA_EVENTS.LOCATION_PARTNER_EXTERNAL_LINK_CLICK,
            {
                contributor_name: 'C',
                partner_group: 'PG',
                link_placement: GA_LINK_PLACEMENT.CONTRIBUTION_LINE,
                destination_url: 'https://ext.example/',
                destination_domain: 'ext.example',
                os_id: 'os-1',
                partner_field_name: 'DOC',
                user_id: '1',
            },
        );
    });
});

describe('sendContributorExternalWebsiteLinkClick', () => {
    beforeEach(() => {
        userHasAcceptedGATracking.mockReturnValue(true);
        global.window.gtag = jest.fn();
        global.window.location = new URL('https://app.example/profile/1');
    });

    it('sends CONTRIBUTOR_EXTERNAL_WEBSITE_LINK_CLICK with contributor params', () => {
        sendContributorExternalWebsiteLinkClick({
            contributorName: 'Name',
            destinationUrl: 'https://site.example',
            userId: '7',
        });

        expect(global.window.gtag).toHaveBeenCalledWith(
            'event',
            GA_EVENTS.CONTRIBUTOR_EXTERNAL_WEBSITE_LINK_CLICK,
            {
                contributor_name: 'Name',
                destination_url: 'https://site.example/',
                destination_domain: 'site.example',
                user_id: '7',
            },
        );
    });
});

describe('exports', () => {
    it('exports GA_EVENTS and GA_LINK_PLACEMENT', () => {
        expect(GA_EVENTS.LOCATION_PARTNER_PROFILE_LINK_CLICK).toBe(
            'LOCATION_PARTNER_PROFILE_LINK_CLICK',
        );
        expect(GA_LINK_PLACEMENT.CONTRIBUTION_LINE).toBe('contribution_line');
    });
});
