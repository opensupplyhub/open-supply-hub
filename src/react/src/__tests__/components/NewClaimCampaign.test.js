import React from 'react';
import { Router } from 'react-router-dom';
import { fireEvent, waitFor } from '@testing-library/react';

import history from '../../util/history';
import apiRequest from '../../util/apiRequest';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import NewClaimCampaign from '../../components/ClaimCampaigns/NewClaimCampaign';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: {
        get: jest.fn(),
        post: jest.fn(),
    },
}));

beforeAll(() => {
    window.scrollTo = jest.fn();
});

const lists = [
    {
        id: 7,
        name: 'Research shortlist',
        kind: 'list',
        is_public: false,
        pending: false,
        supplier_count: 3,
    },
    {
        id: 3,
        name: 'Tier 1 suppliers',
        kind: 'list',
        is_public: true,
        pending: false,
        supplier_count: 1,
    },
];

const suppliersByList = {
    7: [
        {
            os_id: 'BD2024199KXPL2M',
            name: 'Green Delta Produce Ltd',
            country_code: 'BD',
            claim_status: 'unclaimed',
        },
        {
            os_id: 'VN2024310ZZL8KD',
            name: 'Hai Phong Packhouse Co',
            country_code: 'VN',
            claim_status: 'pending',
        },
        {
            os_id: 'TR2022310FANR6N',
            name: 'Anatolia Citrus Cooperative',
            country_code: 'TR',
            claim_status: 'claimed',
        },
    ],
    3: [
        {
            os_id: 'IN2023445GHKW2B',
            name: 'Nashik Grape Growers Assn',
            country_code: 'IN',
            claim_status: 'unclaimed',
        },
    ],
};

const mockCandidates = ({ allowed = true } = {}) =>
    apiRequest.get.mockImplementation(url => {
        if (!allowed) {
            return Promise.reject(new Error('404'));
        }
        const match = url.match(/list=(\d+)/);
        if (match) {
            const id = Number(match[1]);
            return Promise.resolve({
                data: { id, suppliers: suppliersByList[id] },
            });
        }
        return Promise.resolve({ data: lists });
    });

const renderComponent = (userHasSignedIn = true) =>
    renderWithProviders(
        <Router history={history}>
            <NewClaimCampaign />
        </Router>,
        {
            preloadedState: {
                auth: { user: { user: { isAnon: !userHasSignedIn } } },
            },
        },
    );

describe('NewClaimCampaign component', () => {
    beforeEach(() => {
        apiRequest.get.mockReset();
        apiRequest.post.mockReset();
    });

    test('requires login', () => {
        const { getByText } = renderComponent(false);
        expect(
            getByText('Log in to create a claims campaign'),
        ).toBeInTheDocument();
        expect(apiRequest.get).not.toHaveBeenCalled();
    });

    test('tells brands without self-serve to contact OS Hub', async () => {
        mockCandidates({ allowed: false });
        const { findByText } = renderComponent();
        expect(
            await findByText(/isn't turned on for your account/),
        ).toBeInTheDocument();
    });

    test('lists public and private lists and preselects not-claimed suppliers', async () => {
        mockCandidates();
        const { findByText, getByText, getByLabelText } = renderComponent();

        expect(await findByText('Research shortlist')).toBeInTheDocument();
        expect(getByText('Private')).toBeInTheDocument();
        expect(getByText('Public')).toBeInTheDocument();

        expect(
            await findByText('1 supplier will get a claim link'),
        ).toBeInTheDocument();
        expect(getByLabelText('Select Green Delta Produce Ltd')).toBeChecked();

        fireEvent.click(getByText('All · 3'));
        expect(
            getByLabelText('Select Anatolia Citrus Cooperative'),
        ).toBeDisabled();
        expect(
            getByLabelText('Select Hai Phong Packhouse Co'),
        ).not.toBeChecked();
    });

    test('creates the campaign with the chosen suppliers', async () => {
        mockCandidates();
        apiRequest.post.mockResolvedValue({ data: { id: 42 } });
        const pushSpy = jest.spyOn(history, 'push');

        const { findByText, getByText, getByLabelText } = renderComponent();

        await findByText('1 supplier will get a claim link');
        fireEvent.click(getByText('All · 3'));
        fireEvent.click(getByLabelText('Select Hai Phong Packhouse Co'));
        fireEvent.change(getByLabelText('Campaign name'), {
            target: { value: 'Fresh produce onboarding' },
        });
        fireEvent.click(getByText('Create campaign'));

        await waitFor(() =>
            expect(pushSpy).toHaveBeenCalledWith('/claim-campaigns?new=42'),
        );
        expect(apiRequest.post).toHaveBeenCalledWith('/api/claim-campaigns/', {
            name: 'Fresh produce onboarding',
            list_id: 7,
            os_ids: ['BD2024199KXPL2M', 'VN2024310ZZL8KD'],
        });
        pushSpy.mockRestore();
    });

    test('shows the API error when creation fails', async () => {
        mockCandidates();
        apiRequest.post.mockRejectedValue({
            response: { data: { os_ids: ['These OS IDs are not on the chosen list: X'] } },
        });

        const { findByText, getByText, findByRole } = renderComponent();
        await findByText('1 supplier will get a claim link');
        fireEvent.click(getByText('Create campaign'));

        expect(await findByRole('alert')).toHaveTextContent(
            'These OS IDs are not on the chosen list: X',
        );
    });

    test('switching lists loads that list', async () => {
        mockCandidates();
        const { findByText, getByLabelText } = renderComponent();

        await findByText('Green Delta Produce Ltd');
        fireEvent.click(getByLabelText('Tier 1 suppliers'));

        expect(
            await findByText('Nashik Grape Growers Assn'),
        ).toBeInTheDocument();
        expect(apiRequest.get).toHaveBeenCalledWith(
            '/api/claim-campaigns/candidates/?list=3',
        );
    });

    test('closed suppliers on a list show as closed and cannot be picked', async () => {
        const closedList = [
            {
                os_id: 'BD2024199CLOSED',
                name: 'Shuttered Mill',
                country_code: 'BD',
                claim_status: 'unclaimed',
                is_closed: true,
            },
            ...suppliersByList[7],
        ];
        apiRequest.get.mockImplementation(url =>
            Promise.resolve({
                data: url.includes('list=')
                    ? { id: 7, suppliers: closedList }
                    : lists,
            }),
        );

        const { findByLabelText, getByText } = renderComponent();

        const checkbox = await findByLabelText('Select Shuttered Mill');
        expect(checkbox).toBeDisabled();
        expect(checkbox).not.toBeChecked();
        expect(getByText('Closed')).toBeInTheDocument();
        expect(getByText('1 supplier will get a claim link')).toBeInTheDocument();
    });
});

describe('NewClaimCampaign list sources', () => {
    const apiSuppliers = [
        {
            os_id: 'VN2025001APIAAA',
            name: 'Saigon Knitwear JSC',
            country_code: 'VN',
            claim_status: 'unclaimed',
        },
    ];

    const mockSources = sources =>
        apiRequest.get.mockImplementation(url => {
            const match = url.match(/list=(\w+)/);
            if (match) {
                const id = match[1] === 'api' ? 'api' : Number(match[1]);
                return Promise.resolve({
                    data: {
                        id,
                        suppliers:
                            id === 'api'
                                ? apiSuppliers
                                : suppliersByList[id] || [],
                    },
                });
            }
            return Promise.resolve({ data: sources });
        });

    beforeEach(() => {
        apiRequest.get.mockReset();
        apiRequest.post.mockReset();
    });

    test('a list still in moderation is marked pending and cannot be chosen', async () => {
        mockSources([
            {
                id: 9,
                name: 'New upload',
                kind: 'list',
                is_public: true,
                pending: true,
                supplier_count: 0,
            },
            lists[1],
        ]);
        const { findByText, getByText, getAllByRole } = renderComponent();

        expect(await findByText('New upload')).toBeInTheDocument();
        expect(getByText('Pending')).toBeInTheDocument();
        expect(getByText('No suppliers matched yet')).toBeInTheDocument();
        expect(getByText(/A pending list is still being reviewed/)).toBeInTheDocument();

        const radios = getAllByRole('radio').filter(
            radio => radio.closest('label') && radio.name !== 'source',
        );
        expect(radios.some(radio => radio.disabled)).toBe(true);
        // The first list that has suppliers is chosen instead.
        await waitFor(() =>
            expect(apiRequest.get).toHaveBeenCalledWith(
                '/api/claim-campaigns/candidates/?list=3',
            ),
        );
        expect(apiRequest.get).not.toHaveBeenCalledWith(
            '/api/claim-campaigns/candidates/?list=9',
        );
    });

    test('a list over the size limit is marked too large and cannot be chosen', async () => {
        mockSources([
            {
                id: 9,
                name: 'Everything we buy from',
                kind: 'list',
                is_public: true,
                pending: false,
                supplier_count: 25000,
                too_large: true,
            },
            lists[1],
        ]);
        const { findByText, getByText, getAllByRole } = renderComponent();

        expect(await findByText('Everything we buy from')).toBeInTheDocument();
        expect(
            getByText('25000 suppliers · too large to start a campaign from'),
        ).toBeInTheDocument();
        expect(getByText(/use search to choose its suppliers/)).toBeInTheDocument();

        const radios = getAllByRole('radio').filter(
            radio => radio.closest('label') && radio.name !== 'source',
        );
        expect(radios.some(radio => radio.disabled)).toBe(true);
        // The first list within the limit is chosen instead.
        await waitFor(() =>
            expect(apiRequest.get).toHaveBeenCalledWith(
                '/api/claim-campaigns/candidates/?list=3',
            ),
        );
        expect(apiRequest.get).not.toHaveBeenCalledWith(
            '/api/claim-campaigns/candidates/?list=9',
        );
    });

    test('a brand that only uses the API picks from its API submissions', async () => {
        mockSources([
            {
                id: 'api',
                name: 'Locations added through the API',
                kind: 'api',
                is_public: true,
                pending: false,
                supplier_count: 1,
            },
        ]);
        apiRequest.post.mockResolvedValue({ data: { id: 5 } });
        const { findByText, getByText, getByLabelText } = renderComponent();

        expect(
            await findByText('Locations added through the API'),
        ).toBeInTheDocument();
        expect(getByText('API')).toBeInTheDocument();
        expect(getByText('1 supplier')).toBeInTheDocument();

        expect(
            await findByText('1 supplier will get a claim link'),
        ).toBeInTheDocument();
        fireEvent.change(getByLabelText('Campaign name'), {
            target: { value: 'API onboarding' },
        });
        fireEvent.click(getByText('Create campaign'));

        await waitFor(() =>
            expect(apiRequest.post).toHaveBeenCalledWith(
                '/api/claim-campaigns/',
                expect.objectContaining({
                    list_id: 'api',
                    os_ids: ['VN2025001APIAAA'],
                }),
            ),
        );
    });
});

test('passes the number of suppliers left out on to the dashboard', async () => {
    apiRequest.get.mockReset();
    apiRequest.post.mockReset();
    mockCandidates();
    apiRequest.post.mockResolvedValue({
        data: { id: 42, skipped: [{ os_id: 'X', reason: 'claimed' }] },
    });
    const pushSpy = jest.spyOn(history, 'push');
    const { findByText, getByText, getByLabelText } = renderComponent();

    await findByText('1 supplier will get a claim link');
    fireEvent.change(getByLabelText('Campaign name'), {
        target: { value: 'Left out' },
    });
    fireEvent.click(getByText('Create campaign'));
    await waitFor(() =>
        expect(pushSpy).toHaveBeenCalledWith('/claim-campaigns?new=42&left_out=1'),
    );
});

test('API locations waiting for a confirmed match are counted but not choosable yet', async () => {
    apiRequest.get.mockReset();
    apiRequest.get.mockImplementation(url =>
        Promise.resolve({
            data: url.includes('list=')
                ? { id: 3, suppliers: [] }
                : [
                      {
                          id: 'api',
                          name: 'Locations added through the API',
                          kind: 'api',
                          is_public: true,
                          pending: false,
                          awaiting_confirmation: 2,
                          supplier_count: 0,
                      },
                  ],
        }),
    );
    const { findByText, getByText, getByLabelText } = renderComponent();
    expect(
        await findByText('No suppliers matched yet · 2 waiting for you to confirm a match'),
    ).toBeInTheDocument();
    expect(getByText(/appear here once you confirm it/)).toBeInTheDocument();
    expect(getByLabelText('Locations added through the API')).toBeDisabled();
});

test('the source wording covers API uploads as well as lists', async () => {
    apiRequest.get.mockReset();
    apiRequest.get.mockImplementation(url =>
        Promise.resolve({
            data: url.includes('list=')
                ? { id: 'api', suppliers: [] }
                : [
                      {
                          id: 'api',
                          name: 'Locations added through the API',
                          kind: 'api',
                          is_public: false,
                          pending: false,
                          awaiting_confirmation: 0,
                          supplier_count: 3,
                      },
                  ],
        }),
    );
    const { findByLabelText, getByText } = renderComponent();
    expect(await findByLabelText('From my lists or API uploads')).toBeChecked();
    expect(getByText('Choose a source')).toBeInTheDocument();
    expect(
        getByText(/from a private list or private API uploads/),
    ).toBeInTheDocument();
});

describe('NewClaimCampaign supplier limit', () => {
    // A small limit stands in for the real 5,000.
    const bigList = {
        id: 9,
        name: 'All suppliers',
        kind: 'list',
        is_public: true,
        pending: false,
        supplier_count: 5,
    };
    const bigSuppliers = [1, 2, 3, 4, 5].map(n => ({
        os_id: `OS${n}`,
        name: `Supplier ${n}`,
        country_code: 'BD',
        claim_status: 'unclaimed',
    }));

    beforeEach(() => {
        apiRequest.get.mockReset();
        apiRequest.post.mockReset();
        apiRequest.get.mockImplementation(url =>
            Promise.resolve({
                data: url.includes('list=')
                    ? { id: 9, suppliers: bigSuppliers }
                    : [bigList],
            }),
        );
    });

    const renderWithLimit = () =>
        renderWithProviders(
            <Router history={history}>
                <NewClaimCampaign maxSuppliers={2} />
            </Router>,
            {
                preloadedState: {
                    auth: { user: { user: { isAnon: false } } },
                },
            },
        );

    test('opens a larger list with an allowed selection and explains the limit', async () => {
        const { findByText, getByText, getByLabelText } = renderWithLimit();

        expect(
            await findByText('2 suppliers will get a claim link'),
        ).toBeInTheDocument();
        expect(getByLabelText('Select Supplier 1')).toBeChecked();
        expect(getByLabelText('Select Supplier 2')).toBeChecked();
        expect(getByLabelText('Select Supplier 3')).not.toBeChecked();
        // At the limit, more can't be ticked by hand.
        expect(getByLabelText('Select Supplier 3')).toBeDisabled();

        expect(
            getByText(/A campaign can invite up to 2 suppliers, and this list has 5/),
        ).toBeInTheDocument();
        expect(getByText(/the most one campaign can invite/)).toBeInTheDocument();
        expect(getByText('Select first 2 not started')).toBeInTheDocument();
        expect(getByText('Create campaign')).not.toBeDisabled();
    });

    test('a batch selects the next allowed subset, which is what gets created', async () => {
        apiRequest.post.mockResolvedValue({ data: { id: 50 } });
        const { findByText, getByText, getByLabelText } = renderWithLimit();
        await findByText('2 suppliers will get a claim link');

        fireEvent.click(getByText('Select a batch'));
        fireEvent.click(await findByText('3–4'));

        expect(getByLabelText('Select Supplier 1')).not.toBeChecked();
        expect(getByLabelText('Select Supplier 3')).toBeChecked();
        expect(getByLabelText('Select Supplier 4')).toBeChecked();

        fireEvent.click(getByText('Create campaign'));
        await waitFor(() =>
            expect(apiRequest.post).toHaveBeenCalledWith(
                '/api/claim-campaigns/',
                expect.objectContaining({ os_ids: ['OS3', 'OS4'] }),
            ),
        );
    });

    test('the last batch holds the remainder', async () => {
        const { findByText, getByText, getByLabelText } = renderWithLimit();
        await findByText('2 suppliers will get a claim link');

        fireEvent.click(getByText('Select a batch'));
        fireEvent.click(await findByText('5–5'));

        expect(getByLabelText('Select Supplier 5')).toBeChecked();
        expect(
            await findByText('1 supplier will get a claim link'),
        ).toBeInTheDocument();
    });

    test('selecting all shown stops at the limit', async () => {
        const { findByText, getByText, getByLabelText } = renderWithLimit();
        await findByText('2 suppliers will get a claim link');

        fireEvent.click(getByText('Clear'));
        expect(
            await findByText('0 suppliers will get a claim link'),
        ).toBeInTheDocument();

        fireEvent.click(getByLabelText('Select all shown'));
        expect(
            await findByText('2 suppliers will get a claim link'),
        ).toBeInTheDocument();
        expect(getByLabelText('Select Supplier 3')).not.toBeChecked();
    });
});

