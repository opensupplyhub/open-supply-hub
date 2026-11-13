/*
 * The body of the My Organization page: what a non-member, a Member and
 * an Admin each see, and that accepting an invitation and sending one
 * call the right endpoints.
 */
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import {
    fireEvent,
    render,
    screen,
    waitFor,
    within,
} from '@testing-library/react';

import apiRequest from '../../util/apiRequest';
import OrganizationTab from '../../components/Organization/OrganizationTab';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: {
        get: jest.fn(),
        post: jest.fn(),
        patch: jest.fn(),
        delete: jest.fn(),
    },
}));

const ORGANIZATION_UUID = '11111111-1111-1111-1111-111111111111';

const organization = (overrides = {}) => ({
    uuid: ORGANIZATION_UUID,
    name: 'Brand',
    seat_limit: 5,
    seats_used: 2,
    dashboard_enabled: false,
    role: 'MEMBER',
    membership_uuid: 'm2',
    ...overrides,
});

const members = [
    {
        uuid: 'm1',
        role: 'ADMIN',
        status: 'ACTIVE',
        joined_at: '2026-01-10T10:00:00Z',
        user_id: 1,
        email: 'admin@brand.example',
        contributor_id: 11,
        contributor_name: 'Brand HQ',
        is_self: false,
    },
    {
        uuid: 'm2',
        role: 'MEMBER',
        status: 'ACTIVE',
        joined_at: '2026-02-10T10:00:00Z',
        user_id: 2,
        email: 'member@brand.example',
        contributor_id: 12,
        contributor_name: 'Brand Sourcing',
        is_self: true,
    },
];

const notFound = () =>
    Promise.reject(
        Object.assign(new Error('Not Found'), { response: { status: 404 } }),
    );

/* Answers GET requests by URL; anything unexpected fails the test. */
const mockGets = responses => {
    apiRequest.get.mockImplementation(url => {
        const match = Object.keys(responses).find(key => url.startsWith(key));
        if (!match) {
            return Promise.reject(new Error(`Unexpected GET ${url}`));
        }
        const response = responses[match];
        return typeof response === 'function'
            ? response()
            : Promise.resolve({ data: response });
    });
};

const renderTab = () =>
    render(
        <MemoryRouter>
            <OrganizationTab />
        </MemoryRouter>,
    );

describe('OrganizationTab', () => {
    test('tells a user without an organization how to get one', async () => {
        mockGets({
            '/api/organizations/current/': notFound,
            '/api/organization-invitations/': [],
        });

        renderTab();

        expect(
            await screen.findByText(/You don't belong to an organization/),
        ).toBeInTheDocument();
        expect(
            screen.queryByTestId('organization-members'),
        ).not.toBeInTheDocument();
    });

    test('shows a pending invitation and accepts it', async () => {
        mockGets({
            '/api/organizations/current/': notFound,
            '/api/organization-invitations/': [
                {
                    uuid: 'inv-1',
                    email: 'me@example.com',
                    role: 'MEMBER',
                    status: 'PENDING',
                    expires_at: '2026-12-01T00:00:00Z',
                    organization_uuid: ORGANIZATION_UUID,
                    organization_name: 'Brand',
                    invited_by_email: 'admin@brand.example',
                },
            ],
        });
        apiRequest.post.mockResolvedValue({ data: {} });

        renderTab();

        const invitations = await screen.findByTestId('pending-invitations');
        expect(
            within(invitations).getByText('admin@brand.example'),
        ).toBeInTheDocument();

        fireEvent.click(within(invitations).getByText('Accept'));

        await waitFor(() =>
            expect(apiRequest.post).toHaveBeenCalledWith(
                '/api/organization-invitations/inv-1/accept/',
            ),
        );
    });

    test('a Member sees the members and contributions but cannot invite', async () => {
        mockGets({
            '/api/organizations/current/': organization(),
            '/api/organization-invitations/': [],
            [`/api/organizations/${ORGANIZATION_UUID}/members/`]: { members },
            [`/api/organizations/${ORGANIZATION_UUID}/contributions/`]: {
                count: 1,
                results: [
                    {
                        id: 7,
                        name: 'Spring suppliers',
                        status: 'APPROVED',
                        is_active: true,
                        created_at: '2026-03-01T10:00:00Z',
                        submitted_by: {
                            contributor_id: 11,
                            contributor_name: 'Brand HQ',
                            email: 'admin@brand.example',
                        },
                    },
                ],
            },
        });

        renderTab();

        expect(await screen.findByText('Brand')).toBeInTheDocument();
        expect(screen.getByText('2 of 5 seats used')).toBeInTheDocument();
        expect(
            await screen.findByText('member@brand.example (you)'),
        ).toBeInTheDocument();
        expect(await screen.findByText('Spring suppliers')).toBeInTheDocument();
        expect(
            screen.getByText('Brand HQ (admin@brand.example)'),
        ).toBeInTheDocument();

        // Inviting and removing others are Admin actions.
        expect(
            screen.queryByTestId('organization-invitations'),
        ).not.toBeInTheDocument();
        expect(screen.queryByText('Remove')).not.toBeInTheDocument();
        expect(screen.getByText('Leave')).toBeInTheDocument();

        // The dashboard is paid and not switched on for this organization.
        expect(
            screen.getByText(/The organization dashboard is a paid add-on/),
        ).toBeInTheDocument();
        expect(screen.queryByText('Open dashboard')).not.toBeInTheDocument();

        // A Member never asks for the invitation list.
        const invitationListRequested = apiRequest.get.mock.calls.some(
            ([url]) => url.endsWith('/invitations/'),
        );
        expect(invitationListRequested).toBe(false);
    });

    test('shows the legal and parent entity names and the first steps', async () => {
        mockGets({
            '/api/organizations/current/': organization({
                legal_name: 'Brand Holdings Ltd',
                parent_entity_name: 'Brand Group',
            }),
            '/api/organization-invitations/': [],
            [`/api/organizations/${ORGANIZATION_UUID}/members/`]: { members },
            [`/api/organizations/${ORGANIZATION_UUID}/onboarding/`]: {
                has_contributions: true,
                has_colleagues: true,
                has_claims: false,
            },
            [`/api/organizations/${ORGANIZATION_UUID}/contributions/`]: {
                count: 0,
                results: [],
            },
        });

        renderTab();

        expect(
            await screen.findByTestId('organization-entity-names'),
        ).toHaveTextContent(
            'Legal name: Brand Holdings Ltd · Part of: Brand Group',
        );

        const checklist = await screen.findByTestId('organization-onboarding');
        expect(
            within(checklist).getByTestId('onboarding-step-contribute'),
        ).toHaveTextContent('(done)');
        expect(
            within(checklist).getByTestId('onboarding-step-claim'),
        ).toHaveTextContent('(to do)');
        expect(
            within(checklist).getByText('Search production locations'),
        ).toHaveAttribute('href', '/facilities');

        // A Member is never offered colleagues to invite.
        const domainAccountsRequested = apiRequest.get.mock.calls.some(
            ([url]) => url.endsWith('/domain-accounts/'),
        );
        expect(domainAccountsRequested).toBe(false);
    });

    test('hides the first steps once all are done', async () => {
        mockGets({
            '/api/organizations/current/': organization(),
            '/api/organization-invitations/': [],
            [`/api/organizations/${ORGANIZATION_UUID}/members/`]: { members },
            [`/api/organizations/${ORGANIZATION_UUID}/onboarding/`]: {
                has_contributions: true,
                has_colleagues: true,
                has_claims: true,
            },
            [`/api/organizations/${ORGANIZATION_UUID}/contributions/`]: {
                count: 0,
                results: [],
            },
        });

        renderTab();

        expect(
            await screen.findByText('member@brand.example (you)'),
        ).toBeInTheDocument();
        await waitFor(() =>
            expect(apiRequest.get).toHaveBeenCalledWith(
                `/api/organizations/${ORGANIZATION_UUID}/onboarding/`,
            ),
        );
        expect(
            screen.queryByTestId('organization-onboarding'),
        ).not.toBeInTheDocument();
        expect(
            screen.queryByTestId('organization-entity-names'),
        ).not.toBeInTheDocument();
    });

    test('an Admin invites a colleague found on their email domain', async () => {
        mockGets({
            '/api/organizations/current/': organization({ role: 'ADMIN' }),
            '/api/organization-invitations/': [],
            [`/api/organizations/${ORGANIZATION_UUID}/members/`]: { members },
            [`/api/organizations/${ORGANIZATION_UUID}/invitations/`]: [],
            [`/api/organizations/${ORGANIZATION_UUID}/onboarding/`]: {
                has_contributions: false,
                has_colleagues: true,
                has_claims: false,
            },
            [`/api/organizations/${ORGANIZATION_UUID}/domain-accounts/`]: {
                domain: 'brand.example',
                accounts: [
                    {
                        email: 'colleague@brand.example',
                        contributor_name: 'Brand Compliance',
                    },
                ],
            },
            [`/api/organizations/${ORGANIZATION_UUID}/contributions/`]: {
                count: 0,
                results: [],
            },
        });
        apiRequest.post.mockResolvedValue({
            data: { uuid: 'inv-9', email: 'colleague@brand.example' },
        });

        renderTab();

        const section = await screen.findByTestId(
            'organization-domain-accounts',
        );
        expect(
            within(section).getByText(/These accounts use an @brand.example/),
        ).toBeInTheDocument();
        expect(
            within(section).getByText('colleague@brand.example'),
        ).toBeInTheDocument();
        expect(
            within(section).getByText('Brand Compliance'),
        ).toBeInTheDocument();

        fireEvent.click(within(section).getByText('Invite'));

        await waitFor(() =>
            expect(apiRequest.post).toHaveBeenCalledWith(
                `/api/organizations/${ORGANIZATION_UUID}/invitations/`,
                { email: 'colleague@brand.example', role: 'MEMBER' },
            ),
        );
        expect(
            await within(section).findByText(
                'Invitation sent to colleague@brand.example.',
            ),
        ).toBeInTheDocument();
    });

    test('an Admin invites an existing account and sees the reason on refusal', async () => {
        mockGets({
            '/api/organizations/current/': organization({
                role: 'ADMIN',
                dashboard_enabled: true,
            }),
            '/api/organization-invitations/': [],
            [`/api/organizations/${ORGANIZATION_UUID}/members/`]: { members },
            [`/api/organizations/${ORGANIZATION_UUID}/invitations/`]: [],
            [`/api/organizations/${ORGANIZATION_UUID}/contributions/`]: {
                count: 0,
                results: [],
            },
        });
        apiRequest.post.mockRejectedValue(
            Object.assign(new Error('Bad Request'), {
                response: {
                    status: 400,
                    data: {
                        email: ['No confirmed OS Hub account uses this email.'],
                    },
                },
            }),
        );

        renderTab();

        const section = await screen.findByTestId('organization-invitations');
        expect(screen.getByText('Open dashboard')).toBeInTheDocument();

        fireEvent.change(within(section).getByLabelText(/Email/), {
            target: { value: 'new@person.example' },
        });
        fireEvent.click(within(section).getByText('Send invitation'));

        await waitFor(() =>
            expect(apiRequest.post).toHaveBeenCalledWith(
                `/api/organizations/${ORGANIZATION_UUID}/invitations/`,
                { email: 'new@person.example', role: 'MEMBER' },
            ),
        );
        expect(
            await screen.findByText(
                'No confirmed OS Hub account uses this email.',
            ),
        ).toBeInTheDocument();
    });
});
