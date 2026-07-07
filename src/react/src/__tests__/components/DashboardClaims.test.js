import React from 'react';
import { Router, Route } from 'react-router-dom';
import { waitFor } from '@testing-library/react';

import history from '../../util/history';
import apiRequest from '../../util/apiRequest';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import DashboardClaims from '../../components/DashboardClaims';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: {
        get: jest.fn(),
    },
}));

// react-select does not render in jsdom; replace StyledSelect (used by the
// campaign, claim status, and country filters) with its label.
jest.mock('../../components/Filters/StyledSelect', () => {
    // eslint-disable-next-line global-require
    const mockReact = require('react');
    const MockStyledSelect = ({ label, name }) =>
        mockReact.createElement(
            'div',
            { 'data-testid': `select-${name}` },
            label,
        );
    return { __esModule: true, default: MockStyledSelect };
});

const claims = [
    {
        id: 184,
        created_at: '2026-06-14T10:45:53.857805Z',
        updated_at: '2026-06-14T13:25:49.835368Z',
        claim_decision: null,
        contributor_id: 1002,
        os_id: 'TR2024425AKVM2E',
        contributor_name: 'Contributor B',
        facility_name: 'Facility Beta',
        facility_address: '456 Beta Avenue, Beta City, Türkiye',
        facility_country_name: 'Türkiye',
        status: 'PENDING',
        campaign_code: 'EXAMPLE-FRESH-26',
    },
    {
        id: 45,
        created_at: '2026-06-13T05:38:41.859592Z',
        updated_at: '2026-06-13T05:38:41.859607Z',
        claim_decision: null,
        contributor_id: 1003,
        os_id: 'UK2661125AKVMHV',
        contributor_name: 'Contributor C',
        facility_name: 'Facility Gamma',
        facility_address: '789 Gamma Road, Gamma City, United Kingdom',
        facility_country_name: 'United Kingdom',
        status: 'PENDING',
        campaign_code: null,
    },
];

const renderComponent = () =>
    renderWithProviders(
        <Router history={history}>
            <Route path="/dashboard/claims" component={DashboardClaims} />
        </Router>,
    );

describe('DashboardClaims campaign filter', () => {
    beforeAll(() => {
        window.scrollTo = jest.fn();
    });

    beforeEach(() => {
        apiRequest.get.mockImplementation(url =>
            Promise.resolve({
                data: url.includes('facility-claims') ? claims : [],
            }),
        );
    });

    test('shows all claims and the campaign filter without a URL param', async () => {
        history.push('/dashboard/claims');

        const { getByText, getByTestId } = renderComponent();

        await waitFor(() => {
            expect(getByText('Facility Beta')).toBeInTheDocument();
        });

        expect(getByText('Facility Gamma')).toBeInTheDocument();
        expect(getByText('2 results')).toBeInTheDocument();
        expect(getByTestId('select-CAMPAIGNS')).toBeInTheDocument();
    });

    test('filters claims by the campaigns URL parameter', async () => {
        history.push('/dashboard/claims?campaigns=EXAMPLE-FRESH-26');

        const { getByText, queryByText } = renderComponent();

        await waitFor(() => {
            expect(getByText('Facility Beta')).toBeInTheDocument();
        });

        expect(queryByText('Facility Gamma')).not.toBeInTheDocument();
        expect(getByText('1 results')).toBeInTheDocument();
        expect(history.location.search).toContain(
            'campaigns=EXAMPLE-FRESH-26',
        );
    });
});
