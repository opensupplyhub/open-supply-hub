import React from 'react';
import { waitFor } from '@testing-library/react';

import FilterSidebarExtendedSearch from '../../components/FilterSidebarExtendedSearch';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock(
    '../../components/Filters/HierarchicalTaxonomySearch/IsicTaxonomySearch',
    () => ({
        __esModule: true,
        default: () => (
            <div data-testid="isic-taxonomy-search">ISIC taxonomy search</div>
        ),
    }),
);

jest.mock('../../components/Filters/StyledSelect', () => ({
    __esModule: true,
    default: ({ label }) => <div>{label}</div>,
}));

const createPreloadedState = ({
    embed = false,
    isic4TaxonomyConfig = null,
} = {}) => ({
    filterOptions: {
        contributorTypes: { data: [], fetching: false, error: null },
        facilityProcessingType: { data: [], fetching: false, error: null },
        taxonomyCounts: {
            isic4: { data: null, fetching: false, error: null },
        },
        numberOfWorkers: { data: [], fetching: false, error: null },
        isic4Taxonomy: {
            config: isic4TaxonomyConfig,
            data: null,
            fetching: false,
            error: null,
        },
    },
    filters: {
        contributorTypes: [],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        isic4: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
    },
    facilities: {
        facilities: { data: null, fetching: false },
    },
    embeddedMap: {
        embed,
        config: { extended_fields: [] },
    },
});

describe('FilterSidebarExtendedSearch ISIC gating', () => {
    beforeEach(() => {
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: true,
                json: () =>
                    Promise.resolve({
                        isic4: {
                            enabled: false,
                            version: 1,
                            taxonomyUrl: null,
                        },
                    }),
            }),
        );
    });

    const renderComponent = preloadedState =>
        renderWithProviders(<FilterSidebarExtendedSearch />, {
            preloadedState,
        });

    test('shows ISIC only when its taxonomy is enabled', async () => {
        const { getByTestId } = renderComponent(
            createPreloadedState({
                isic4TaxonomyConfig: {
                    enabled: true,
                    version: 1,
                    taxonomyUrl: '/api/taxonomy/isic4/?v=1',
                },
            }),
        );

        await waitFor(() => {
            expect(getByTestId('isic-taxonomy-search')).toBeInTheDocument();
        });
    });

    test('hides ISIC in embedded maps', () => {
        const { queryByTestId } = renderComponent(
            createPreloadedState({
                embed: true,
                isic4TaxonomyConfig: {
                    enabled: true,
                    version: 1,
                    taxonomyUrl: '/api/taxonomy/isic4/?v=1',
                },
            }),
        );

        expect(queryByTestId('isic-taxonomy-search')).not.toBeInTheDocument();
    });

    test('shows a config error when taxonomy settings fail', async () => {
        global.fetch = jest.fn(() =>
            Promise.resolve({
                ok: false,
                status: 500,
                json: () => Promise.resolve(null),
            }),
        );

        const { getByText } = renderComponent(createPreloadedState());

        await waitFor(() => {
            expect(
                getByText(
                    'Unable to load ISIC taxonomy settings. Try refreshing the page.',
                ),
            ).toBeInTheDocument();
        });
    });
});
