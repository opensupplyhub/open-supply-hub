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

// The select-based filters need a browser; the repo's other search tests
// stub them the same way. The text search filter is kept.
jest.mock('../../components/Filters/ContributorFilter', () => () => null);
jest.mock('../../components/Filters/CountryNameFilter', () => () => null);
jest.mock('../../components/Filters/SectorFilter', () => () => null);
jest.mock('../../components/FilterSidebarExtendedSearch', () => {
    const ReactModule = jest.requireActual('react');
    return ReactModule.forwardRef((props, ref) => {
        ReactModule.useImperativeHandle(ref, () => ({
            commitPendingQuery: () => true,
        }));
        return null;
    });
});

beforeAll(() => {
    window.scrollTo = jest.fn();
});

const searchResults = {
    count: 3,
    limit: 500,
    suppliers: [
        {
            os_id: 'VN2024310LOTUS1',
            name: 'Lotus Knitwear',
            country_code: 'VN',
            claim_status: 'unclaimed',
        },
        {
            os_id: 'VN2024310LOTUS2',
            name: 'Lotus Dye House',
            country_code: 'VN',
            claim_status: 'pending',
        },
        {
            os_id: 'VN2024310LOTUS3',
            name: 'Lotus Garments',
            country_code: 'VN',
            claim_status: 'claimed',
        },
    ],
};

const mockAPI = () =>
    apiRequest.get.mockImplementation(url => {
        if (url.startsWith('/api/claim-campaigns/candidates/search/')) {
            return Promise.resolve({ data: searchResults });
        }
        if (url.startsWith('/api/claim-campaigns/candidates/')) {
            return Promise.resolve({ data: [] });
        }
        // Filter options for the search filters.
        return Promise.resolve({ data: [] });
    });

const renderAndChooseSearch = async () => {
    const utils = renderWithProviders(
        <Router history={history}>
            <NewClaimCampaign />
        </Router>,
        {
            preloadedState: {
                auth: { user: { user: { isAnon: false } } },
            },
        },
    );
    fireEvent.click(await utils.findByLabelText('From a search of OS Hub'));
    return utils;
};

const searchFor = async ({ getByPlaceholderText, getByText, findByText }) => {
    fireEvent.change(getByPlaceholderText('e.g. ABC Textiles Limited'), {
        target: { value: 'Lotus' },
    });
    fireEvent.click(getByText('Search'));
    await findByText('Lotus Knitwear');
};

describe('Choosing campaign suppliers from a search', () => {
    beforeEach(() => {
        apiRequest.get.mockReset();
        apiRequest.post.mockReset();
        mockAPI();
    });

    test('lists are the default; search is the second option', async () => {
        const { findByLabelText } = renderWithProviders(
            <Router history={history}>
                <NewClaimCampaign />
            </Router>,
            {
                preloadedState: {
                    auth: { user: { user: { isAnon: false } } },
                },
            },
        );

        expect(await findByLabelText('From one of my lists')).toBeChecked();
        expect(await findByLabelText('From a search of OS Hub')).not.toBeChecked();
    });

    test('asks for a filter before searching', async () => {
        const utils = await renderAndChooseSearch();

        fireEvent.click(utils.getByText('Search'));

        expect(
            await utils.findByText('Add at least one search filter.'),
        ).toBeInTheDocument();
        expect(apiRequest.get).not.toHaveBeenCalledWith(
            expect.stringContaining('/candidates/search/'),
        );
    });

    test('searches with the site filters and adds suppliers one by one', async () => {
        const utils = await renderAndChooseSearch();
        await searchFor(utils);

        expect(apiRequest.get).toHaveBeenCalledWith(
            '/api/claim-campaigns/candidates/search/?q=Lotus',
        );
        // Claimed results can't be added.
        expect(utils.getByLabelText('Add Lotus Garments')).toBeDisabled();

        fireEvent.click(utils.getByLabelText('Add Lotus Knitwear'));

        expect(utils.getByText('Added to this campaign (1)')).toBeInTheDocument();
        expect(utils.getByLabelText('Remove Lotus Knitwear')).toBeInTheDocument();
        expect(utils.getByText('1 supplier will get a claim link')).toBeInTheDocument();
    });

    test('adds all not-claimed results and creates the campaign without a list', async () => {
        apiRequest.post.mockResolvedValue({ data: { id: 12 } });
        const utils = await renderAndChooseSearch();
        await searchFor(utils);

        fireEvent.click(utils.getByText('Add all 2 not yet claimed'));
        expect(utils.getByText('Added to this campaign (2)')).toBeInTheDocument();

        fireEvent.click(utils.getByText('Create campaign'));

        await waitFor(() => {
            expect(apiRequest.post).toHaveBeenCalledTimes(1);
        });
        const [url, payload] = apiRequest.post.mock.calls[0];
        expect(url).toBe('/api/claim-campaigns/');
        expect(payload.list_id).toBeUndefined();
        expect(payload.os_ids).toEqual(['VN2024310LOTUS1', 'VN2024310LOTUS2']);
    });

    test('removing an added supplier lets it be added again', async () => {
        const utils = await renderAndChooseSearch();
        await searchFor(utils);

        fireEvent.click(utils.getByLabelText('Add Lotus Knitwear'));
        fireEvent.click(utils.getByLabelText('Remove Lotus Knitwear'));

        expect(utils.getByText('Added to this campaign (0)')).toBeInTheDocument();
        expect(utils.getByLabelText('Add Lotus Knitwear')).toBeEnabled();
    });
});
