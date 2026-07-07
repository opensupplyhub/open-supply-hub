import React from 'react';
import { Router } from 'react-router-dom';
import { fireEvent, waitFor } from '@testing-library/react';
import { saveAs } from 'file-saver';

import history from '../../util/history';
import apiRequest from '../../util/apiRequest';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimCampaigns from '../../components/ClaimCampaigns/ClaimCampaigns';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: {
        get: jest.fn(),
    },
}));

jest.mock('file-saver', () => ({
    saveAs: jest.fn(),
}));

beforeAll(() => {
    window.scrollTo = jest.fn();
    // jsdom in this suite has no Blob; DownloadCSV needs one.
    global.Blob = jest.fn(content => ({ content }));
});

const mockCampaigns = [
    {
        id: 1,
        name: 'Fresh Produce Suppliers 2026',
        code: 'EXAMPLE-FRESH-26',
        status: 'ACTIVE',
        created_at: '2026-05-12T00:00:00Z',
        suppliers: [
            {
                os_id: 'BD2024199KXPL2M',
                name: 'Green Delta Produce Ltd',
                country_code: 'BD',
                claim_status: 'claimed',
            },
            {
                os_id: 'VN2024310ZZL8KD',
                name: 'Hai Phong Packhouse Co',
                country_code: 'VN',
                claim_status: 'unclaimed',
            },
        ],
    },
];

const renderComponent = (userHasSignedIn = true) => {
    const preloadedState = {
        auth: {
            user: {
                user: { isAnon: !userHasSignedIn },
            },
        },
    };

    return renderWithProviders(
        <Router history={history}>
            <ClaimCampaigns />
        </Router>,
        { preloadedState },
    );
};

describe('ClaimCampaigns component', () => {
    beforeEach(() => {
        apiRequest.get.mockClear();
    });

    test('requires login', () => {
        const { getByText } = renderComponent(false);

        expect(
            getByText('Log in to view your claims campaigns'),
        ).toBeInTheDocument();
        expect(apiRequest.get).not.toHaveBeenCalled();
    });

    test('renders campaigns with suppliers and statuses', async () => {
        apiRequest.get.mockResolvedValue({ data: mockCampaigns });

        const { getByText, getAllByText } = renderComponent();

        await waitFor(() => {
            expect(
                getByText('Fresh Produce Suppliers 2026'),
            ).toBeInTheDocument();
        });

        expect(apiRequest.get).toHaveBeenCalledWith('/api/claim-campaigns/');
        expect(getByText('EXAMPLE-FRESH-26')).toBeInTheDocument();
        expect(getByText('Suppliers invited')).toBeInTheDocument();
        expect(getByText('50% of suppliers claimed')).toBeInTheDocument();
        expect(getByText('Claimed (1)')).toBeInTheDocument();
        expect(getByText('Pending review (0)')).toBeInTheDocument();
        expect(getByText('Not started (1)')).toBeInTheDocument();
        expect(getByText('Green Delta Produce Ltd')).toBeInTheDocument();
        // KPI tile label + supplier row chip
        expect(getAllByText('Claimed').length).toBeGreaterThanOrEqual(2);
        expect(getAllByText('Not started').length).toBeGreaterThanOrEqual(2);
    });

    test('downloads the supplier CSV', async () => {
        apiRequest.get.mockResolvedValue({ data: mockCampaigns });

        const { getByText } = renderComponent();

        await waitFor(() => {
            expect(getByText('Download CSV')).toBeInTheDocument();
        });

        fireEvent.click(getByText('Download CSV'));

        await waitFor(() => {
            expect(saveAs).toHaveBeenCalledTimes(1);
        });
        expect(saveAs.mock.calls[0][1]).toBe('EXAMPLE-FRESH-26_suppliers.csv');
    });

    test('shows the empty state when the account has no campaigns', async () => {
        apiRequest.get.mockResolvedValue({ data: [] });

        const { getByText } = renderComponent();

        await waitFor(() => {
            expect(
                getByText(/Your account has no claims campaigns yet/),
            ).toBeInTheDocument();
        });
    });
});
