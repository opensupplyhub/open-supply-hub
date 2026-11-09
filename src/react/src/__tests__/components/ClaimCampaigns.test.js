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
        post: jest.fn(),
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

const renderComponent = (
    userHasSignedIn = true,
    props = {},
    { claimInvite = false } = {},
) => {
    const preloadedState = {
        auth: {
            user: {
                user: { isAnon: !userHasSignedIn },
            },
        },
        featureFlags: {
            fetching: false,
            flags: { claim_invite: claimInvite },
        },
    };

    return renderWithProviders(
        <Router history={history}>
            <ClaimCampaigns {...props} />
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

    const mockGetByURL = ({ selfServe }) =>
        apiRequest.get.mockImplementation(url => {
            if (url.startsWith('/api/claim-campaigns/candidates/')) {
                return selfServe
                    ? Promise.resolve({ data: [] })
                    : Promise.reject(new Error('404'));
            }
            return Promise.resolve({ data: mockCampaigns });
        });

    test('shows "New campaign" to brands enabled for self-serve', async () => {
        mockGetByURL({ selfServe: true });

        const { findByText } = renderComponent();

        const button = await findByText('New campaign');
        expect(button.closest('a')).toHaveAttribute(
            'href',
            '/claim-campaigns/new',
        );
    });

    test('hides "New campaign" from other brands', async () => {
        mockGetByURL({ selfServe: false });

        const { findByText, queryByText } = renderComponent();

        await findByText('Fresh Produce Suppliers 2026');
        expect(queryByText('New campaign')).not.toBeInTheDocument();
    });

    test('confirms a campaign that was just created', async () => {
        mockGetByURL({ selfServe: true });

        const { findByRole } = renderComponent(true, {
            location: { search: '?new=1' },
        });

        const banner = await findByRole('status');
        expect(banner).toHaveTextContent(
            'Campaign Fresh Produce Suppliers 2026 created with 2 suppliers.',
        );
    });

    test('without the claim_invite switch, only claim links are offered', async () => {
        apiRequest.get.mockResolvedValue({ data: mockCampaigns });

        const { findByText, queryByText, getAllByText } = renderComponent();

        await findByText('Unique claim link');
        expect(queryByText('Invite by')).not.toBeInTheDocument();
        expect(getAllByText('Copy link')).toHaveLength(2);
    });

    test('emails a supplier its campaign invite', async () => {
        apiRequest.get.mockResolvedValue({ data: mockCampaigns });
        apiRequest.post.mockResolvedValue({
            data: { recipient_email: 'ops@haiphong.example' },
        });

        const { findByText, getByLabelText, getByText } = renderComponent(
            true,
            {},
            { claimInvite: true },
        );

        await findByText('Contact email');
        // The claimed supplier can't be invited again.
        expect(getByText('Already claimed')).toBeInTheDocument();

        fireEvent.change(
            getByLabelText('Email address for Hai Phong Packhouse Co'),
            { target: { value: 'ops@haiphong.example' } },
        );
        fireEvent.click(getByText('Send'));

        await findByText(/Invited ops@haiphong.example/);
        expect(apiRequest.post).toHaveBeenCalledWith(
            '/api/facilities/VN2024310ZZL8KD/claim-invite/',
            {
                recipient_email: 'ops@haiphong.example',
                note: undefined,
                campaign: 'EXAMPLE-FRESH-26',
            },
        );
    });

    test('switches the contact column to claim links', async () => {
        apiRequest.get.mockResolvedValue({ data: mockCampaigns });

        const {
            findByText,
            getByText,
            getAllByText,
            queryByText,
        } = renderComponent(
            true,
            {},
            { claimInvite: true },
        );

        await findByText('Contact email');
        // The CSV of links only goes with the link option.
        expect(queryByText('Download CSV')).not.toBeInTheDocument();
        fireEvent.click(getByText('Link'));

        expect(getByText('Unique claim link')).toBeInTheDocument();
        expect(getAllByText('Copy link')).toHaveLength(2);
        expect(getByText('Download CSV')).toBeInTheDocument();
    });

    test('paginates long supplier lists', async () => {
        const suppliers = Array.from({ length: 30 }, (_, i) => ({
            os_id: `BD2024199SUP${String(i).padStart(3, '0')}`,
            name: `Supplier ${i + 1}`,
            country_code: 'BD',
            claim_status: 'unclaimed',
        }));
        apiRequest.get.mockResolvedValue({
            data: [{ ...mockCampaigns[0], suppliers }],
        });

        const { findByText, queryByText } = renderComponent();

        await findByText('Supplier 1');
        expect(queryByText('Supplier 25')).toBeInTheDocument();
        expect(queryByText('Supplier 26')).not.toBeInTheDocument();
        expect(await findByText('1-25 of 30')).toBeInTheDocument();
    });
});
