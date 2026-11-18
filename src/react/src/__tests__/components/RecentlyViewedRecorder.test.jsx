/*
 * The recorder notes a loaded production location for a signed-in
 * member of an organization, and for nobody else.
 */
import React from 'react';

import renderWithProviders from '../../util/testUtils/renderWithProviders';
import RecentlyViewedRecorder from '../../components/Organization/RecentlyViewedRecorder';
import { getRecentlyViewedLocations } from '../../components/Organization/recentlyViewed';

const facility = {
    id: 'IN2026316ABCDEF',
    properties: { name: 'Solo Mill', country_name: 'India' },
};

const state = ({ user, flagOn = true, data = facility } = {}) => ({
    auth: {
        user: { user },
        session: { fetching: false },
    },
    facilities: { singleFacility: { data } },
    featureFlags: {
        fetching: false,
        flags: { organization_level: flagOn },
    },
});

const member = {
    isAnon: false,
    id: 7,
    organization: { uuid: 'u', name: 'Brand', role: 'MEMBER' },
};

describe('RecentlyViewedRecorder', () => {
    beforeEach(() => {
        window.localStorage.clear();
    });

    test('records the loaded location for a member', () => {
        renderWithProviders(<RecentlyViewedRecorder />, {
            preloadedState: state({ user: member }),
        });

        const viewed = getRecentlyViewedLocations(7);
        expect(viewed).toHaveLength(1);
        expect(viewed[0]).toMatchObject({
            os_id: 'IN2026316ABCDEF',
            name: 'Solo Mill',
            country_name: 'India',
        });
    });

    test('records nothing for a user without an organization', () => {
        renderWithProviders(<RecentlyViewedRecorder />, {
            preloadedState: state({
                user: { isAnon: false, id: 7, organization: null },
            }),
        });

        expect(getRecentlyViewedLocations(7)).toEqual([]);
    });

    test('records nothing while the organization level is off', () => {
        renderWithProviders(<RecentlyViewedRecorder />, {
            preloadedState: state({ user: member, flagOn: false }),
        });

        expect(getRecentlyViewedLocations(7)).toEqual([]);
    });

    test('records nothing until a location has loaded', () => {
        renderWithProviders(<RecentlyViewedRecorder />, {
            preloadedState: state({ user: member, data: null }),
        });

        expect(getRecentlyViewedLocations(7)).toEqual([]);
    });
});
