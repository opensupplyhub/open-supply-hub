/*
 * The organization dashboard page: who gets in, and that the totals,
 * the table and the claimed-data dialog render what the API returns.
 */
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { fireEvent, screen, waitFor, within } from '@testing-library/react';

import apiRequest from '../../util/apiRequest';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import OrganizationDashboard from '../../components/Organization/OrganizationDashboard';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { get: jest.fn() },
}));

const ORGANIZATION_UUID = '11111111-1111-1111-1111-111111111111';
const BASE = `/api/organizations/${ORGANIZATION_UUID}`;

const organization = (overrides = {}) => ({
    uuid: ORGANIZATION_UUID,
    name: 'Brand',
    seat_limit: 5,
    seats_used: 2,
    dashboard_enabled: true,
    role: 'MEMBER',
    ...overrides,
});

const summary = {
    total_facilities: 2,
    total_submissions: 3,
    claimed_facilities: 1,
    unclaimed_facilities: 1,
    pending_moderation: 4,
    by_member: [
        {
            contributor_id: 12,
            contributor_name: 'Brand Sourcing',
            facilities: 2,
            submissions: 2,
        },
    ],
    by_country: [
        { country_code: 'IN', country_name: 'India', facilities: 1 },
    ],
    by_month: [{ month: '2026-11', facilities: 2, submissions: 3 }],
    by_sector: [{ sector: 'Apparel', facilities: 2 }],
    by_source_type: {
        list: { facilities: 2, submissions: 2 },
        single: { facilities: 1, submissions: 1 },
    },
};

const facilityRow = {
    submission_id: 1,
    os_id: 'IN2026316ABCDEF',
    name: 'Solo Mill',
    address: '1 Example Street',
    country_code: 'IN',
    country_name: 'India',
    submitted_at: '2026-11-02T10:00:00Z',
    submitted_by: { contributor_id: 12, contributor_name: 'Brand Sourcing' },
    source_type: 'LIST',
    list: { id: 9, name: 'Autumn suppliers' },
    is_claimed: true,
    claimed_at: '2026-11-05T10:00:00Z',
};

const facilityDetail = {
    os_id: 'IN2026316ABCDEF',
    name: 'Solo Mill',
    address: '1 Example Street',
    country_code: 'IN',
    country_name: 'India',
    sectors: ['Apparel'],
    is_claimed: true,
    claimed_at: '2026-11-05T10:00:00Z',
    claim: {
        claimed_by: 'Solo Mill Ltd',
        facility: { description: 'A mill', workers_count: '120', website: null },
        contact: null,
        office: null,
    },
    submissions: [facilityRow],
};

const listReport = {
    lists: [
        {
            id: 9,
            name: 'Autumn suppliers',
            uploaded_at: '2026-11-02T10:00:00Z',
            status: 'APPROVED',
            is_active: true,
            submitted_by: {
                contributor_id: 12,
                contributor_name: 'Brand Sourcing',
                email: 'member@brand.example',
            },
            total: 1200,
            matched_existing: 900,
            new_locations: 250,
            needs_review: 30,
            failed: 12,
            duplicates: 5,
            removed: 2,
            in_progress: 1,
        },
        {
            id: 8,
            name: 'Spring suppliers',
            uploaded_at: '2026-04-02T10:00:00Z',
            status: 'APPROVED',
            is_active: false,
            submitted_by: {
                contributor_id: 11,
                contributor_name: 'Brand HQ',
                email: 'admin@brand.example',
            },
            total: 10,
            matched_existing: 10,
            new_locations: 0,
            needs_review: 0,
            failed: 0,
            duplicates: 0,
            removed: 0,
            in_progress: 0,
        },
    ],
};

const usage = {
    period_days: 30,
    members: [
        {
            membership_uuid: 'm1',
            email: 'admin@brand.example',
            contributor_name: 'Brand HQ',
            downloads: {
                count: 1,
                records: 10,
                records_this_year: 10,
                free_records_left: null,
                paid_records_left: null,
            },
            api: null,
        },
        {
            membership_uuid: 'm2',
            email: 'member@brand.example',
            contributor_name: 'Brand Sourcing',
            downloads: {
                count: 2,
                records: 140,
                records_this_year: 147,
                free_records_left: 4860,
                paid_records_left: 250,
            },
            api: {
                calls: 45,
                limit: 5000,
                renewal_period: 'MONTHLY',
                calls_this_period: 120,
            },
        },
    ],
    totals: { downloads: 3, downloaded_records: 150, api_calls: 45 },
};

const selfMember = {
    uuid: 'm2',
    role: 'MEMBER',
    email: 'member@brand.example',
    contributor_id: 12,
    contributor_name: 'Brand Sourcing',
    is_self: true,
};

const signedInState = {
    auth: {
        user: { user: { isAnon: false, id: 2, email: 'member@brand.example' } },
        session: { fetching: false },
    },
};

const mockGets = responses => {
    apiRequest.get.mockImplementation(url => {
        // Longest prefix first, so the facility detail URL is not
        // answered with the facilities list.
        const match = Object.keys(responses)
            .sort((a, b) => b.length - a.length)
            .find(key => url.startsWith(key));
        if (!match) {
            return Promise.reject(new Error(`Unexpected GET ${url}`));
        }
        const response = responses[match];
        return typeof response === 'function'
            ? response()
            : Promise.resolve({ data: response });
    });
};

const renderDashboard = (preloadedState = signedInState) =>
    renderWithProviders(
        <MemoryRouter>
            <OrganizationDashboard />
        </MemoryRouter>,
        { preloadedState },
    );

describe('OrganizationDashboard', () => {
    test('asks an anonymous visitor to log in and fetches nothing', () => {
        renderDashboard({});

        expect(
            screen.getByText("Log in to see your organization's dashboard"),
        ).toBeInTheDocument();
        expect(apiRequest.get).not.toHaveBeenCalled();
    });

    test('explains that the dashboard is a paid add-on when it is off', async () => {
        mockGets({
            '/api/organizations/current/': organization({
                dashboard_enabled: false,
            }),
        });

        renderDashboard();

        expect(
            await screen.findByText(/The dashboard is a paid add-on/),
        ).toBeInTheDocument();
        expect(
            screen.getByText('Back to organization').closest('a'),
        ).toHaveAttribute('href', '/organization');
        const dashboardRequested = apiRequest.get.mock.calls.some(([url]) =>
            url.includes('/dashboard/'),
        );
        expect(dashboardRequested).toBe(false);
    });

    test('tells a user without an organization there is nothing to show', async () => {
        mockGets({
            '/api/organizations/current/': () =>
                Promise.reject(
                    Object.assign(new Error('Not Found'), {
                        response: { status: 404 },
                    }),
                ),
        });

        renderDashboard();

        expect(
            await screen.findByText(/You don't belong to an organization/),
        ).toBeInTheDocument();
    });

    test('shows totals, the submitted locations and their claimed data', async () => {
        mockGets({
            '/api/organizations/current/': organization(),
            [`${BASE}/members/`]: { members: [] },
            [`${BASE}/dashboard/summary/`]: summary,
            [`${BASE}/dashboard/facilities/`]: {
                count: 1,
                results: [facilityRow],
            },
            [`${BASE}/dashboard/facilities/IN2026316ABCDEF/`]: facilityDetail,
        });

        renderDashboard();

        const tiles = await screen.findByTestId('dashboard-tiles');
        expect(
            within(tiles).getByText('Production locations submitted'),
        ).toBeInTheDocument();
        expect(within(tiles).getByText('1 (50%)')).toBeInTheDocument();
        expect(within(tiles).getByText('4')).toBeInTheDocument();
        expect(screen.getByText('Nov 2026')).toBeInTheDocument();

        const table = await screen.findByTestId('dashboard-facilities-table');
        expect(await within(table).findByText('Solo Mill')).toBeInTheDocument();
        expect(within(table).getByText('Autumn suppliers')).toBeInTheDocument();
        expect(within(table).getByText(/^Since /)).toBeInTheDocument();

        fireEvent.click(within(table).getByText('Details'));

        await waitFor(() =>
            expect(apiRequest.get).toHaveBeenCalledWith(
                `${BASE}/dashboard/facilities/IN2026316ABCDEF/`,
            ),
        );
        expect(await screen.findByText('Solo Mill Ltd')).toBeInTheDocument();
        expect(screen.getByText('Number of workers')).toBeInTheDocument();
        // A detail the claimant kept private is simply not listed.
        expect(screen.queryByText('Website')).not.toBeInTheDocument();
    });

    test('shows the match report, linking only the member\'s own list', async () => {
        mockGets({
            '/api/organizations/current/': organization(),
            [`${BASE}/members/`]: { members: [selfMember] },
            [`${BASE}/dashboard/summary/`]: summary,
            [`${BASE}/dashboard/facilities/`]: { count: 0, results: [] },
            [`${BASE}/dashboard/lists/`]: listReport,
            [`${BASE}/dashboard/usage/`]: usage,
        });

        renderDashboard();

        const report = await screen.findByTestId('dashboard-list-match-report');
        const ownList = await within(report).findByText('Autumn suppliers');
        expect(ownList.closest('a')).toHaveAttribute('href', '/lists/9');
        expect(within(report).getByText('1,200')).toBeInTheDocument();
        expect(within(report).getByText('900')).toBeInTheDocument();
        expect(within(report).getByText('250')).toBeInTheDocument();

        // A colleague's list page is not open to this member.
        expect(
            within(report).getByText('Spring suppliers').closest('a'),
        ).toBeNull();
        expect(
            within(report).getByText(/replaced or inactive/),
        ).toBeInTheDocument();
    });

    test('shows download and API usage per member and in total', async () => {
        mockGets({
            '/api/organizations/current/': organization(),
            [`${BASE}/members/`]: { members: [selfMember] },
            [`${BASE}/dashboard/summary/`]: summary,
            [`${BASE}/dashboard/facilities/`]: { count: 0, results: [] },
            [`${BASE}/dashboard/lists/`]: { lists: [] },
            [`${BASE}/dashboard/usage/`]: usage,
        });

        renderDashboard();

        const section = await screen.findByTestId('dashboard-usage');
        const tiles = await within(section).findByTestId(
            'dashboard-usage-tiles',
        );
        expect(within(tiles).getByText('150')).toBeInTheDocument();
        expect(within(tiles).getByText('45')).toBeInTheDocument();
        expect(
            within(section).getByText(/in the last 30 days/),
        ).toBeInTheDocument();
        expect(within(section).getByText('4,860')).toBeInTheDocument();
        expect(
            within(section).getByText('120 of 5,000 monthly'),
        ).toBeInTheDocument();
        expect(within(section).getByText('No API access')).toBeInTheDocument();

        expect(
            await screen.findByText(
                'Your organization has not uploaded a list yet.',
            ),
        ).toBeInTheDocument();
    });

    test('shows the locations this user viewed recently, and clears them', async () => {
        window.localStorage.setItem(
            'oshub.recentlyViewedLocations.2',
            JSON.stringify([
                {
                    os_id: 'IN2026316ABCDEF',
                    name: 'Solo Mill',
                    country_name: 'India',
                    viewed_at: '2026-11-10T10:00:00Z',
                },
            ]),
        );
        mockGets({
            '/api/organizations/current/': organization(),
            [`${BASE}/members/`]: { members: [selfMember] },
            [`${BASE}/dashboard/summary/`]: summary,
            [`${BASE}/dashboard/facilities/`]: { count: 0, results: [] },
            [`${BASE}/dashboard/lists/`]: { lists: [] },
            [`${BASE}/dashboard/usage/`]: usage,
        });

        renderDashboard();

        const section = await screen.findByTestId('dashboard-recently-viewed');
        expect(
            within(section).getByText('Solo Mill').closest('a'),
        ).toHaveAttribute('href', '/facilities/IN2026316ABCDEF');

        fireEvent.click(within(section).getByText('Clear this list'));

        expect(
            within(section).getByText(
                'Production locations you open will appear here.',
            ),
        ).toBeInTheDocument();
        expect(
            window.localStorage.getItem('oshub.recentlyViewedLocations.2'),
        ).toBeNull();
    });
});
