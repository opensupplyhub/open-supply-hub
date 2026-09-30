import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';

import apiRequest from '../../util/apiRequest';
import ClaimsV2Dashboard from '../../components/ClaimsV2/ClaimsV2Dashboard';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { get: jest.fn(), post: jest.fn() },
}));

const LIST = [
    {
        id: 1,
        facility_name: 'First Facility',
        facility_country_name: 'Latvia',
        contributor_name: 'First Org',
        os_id: 'LV2023146T90PXR',
        created_at: '2026-09-01T09:00:00Z',
        status: 'PENDING',
    },
    {
        id: 2,
        facility_name: 'Second Facility',
        facility_country_name: 'France',
        contributor_name: 'Second Org',
        os_id: 'FR2023146T90AAA',
        created_at: '2026-09-02T09:00:00Z',
        status: 'PENDING',
    },
];

const detail = id => ({
    id,
    created_at: '2026-09-01T09:00:00Z',
    contact_person: 'Person',
    job_title: 'Manager',
    email: 'person@example.com',
    company_name: 'Org',
    status: 'PENDING',
    status_change: {},
    notes: [],
    attachments: [],
    facility: {
        id: 'LV2023146T90PXR',
        properties: {
            name: id === 2 ? 'Second Facility' : 'First Facility',
            address: 'Address',
            country_name: 'Latvia',
        },
    },
});

describe('ClaimsV2Dashboard ?claim deep link', () => {
    beforeEach(() => {
        apiRequest.get.mockReset();
        apiRequest.get.mockImplementation(url => {
            if (url.includes('/facility-claims/2/')) {
                return Promise.resolve({ data: detail(2) });
            }
            if (url.includes('/facility-claims/1/')) {
                return Promise.resolve({ data: detail(1) });
            }
            return Promise.resolve({ data: LIST });
        });
    });

    it('preselects the claim from ?claim across the initial load', async () => {
        // The regression this pins: on the first commit the auto-select
        // effect used to run before the fetch effect's state landed and
        // clobbered the deep-linked selection with an empty list.
        window.history.replaceState(null, '', '/dashboard/claims-v2?claim=2');

        render(<ClaimsV2Dashboard />);

        await waitFor(() =>
            expect(window.location.search).toBe('?claim=2'),
        );
        // The workspace shows the deep-linked claim, not the first one.
        expect(
            await screen.findByText(/Claim #2/),
        ).toBeTruthy();
    });

    it('falls back to the first visible claim without a ?claim param', async () => {
        window.history.replaceState(null, '', '/dashboard/claims-v2');

        render(<ClaimsV2Dashboard />);

        await waitFor(() =>
            expect(window.location.search).toBe('?claim=1'),
        );
    });
});

describe('ClaimsV2Dashboard initial-load failure', () => {
    it('shows the error and Retry instead of an eternal spinner', async () => {
        window.history.replaceState(null, '', '/dashboard/claims-v2');
        apiRequest.get.mockReset();
        apiRequest.get.mockRejectedValue(new Error('network'));

        render(<ClaimsV2Dashboard />);

        // Previously: `loaded` never became true, so initialLoading kept
        // returning the spinner and this branch was unreachable.
        expect(
            await screen.findByText(
                'An error prevented fetching the claims list.',
            ),
        ).toBeTruthy();
        expect(screen.getByRole('button', { name: 'Retry' })).toBeTruthy();
    });
});
