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

jest.mock('../../components/Filters/HierarchicalTaxonomySearch', () => ({
    __esModule: true,
    default: () => (
        <div data-testid="facility-processing-search">
            Facility processing search
        </div>
    ),
    TAXONOMY_KINDS: {
        FACILITY_PROCESSING: 'facility_processing',
        ISIC4: 'isic4',
    },
}));

jest.mock('../../components/Filters/StyledSelect', () => ({
    __esModule: true,
    default: ({ label }) => <div>{label}</div>,
}));

const createPreloadedState = ({
    facilityType = [],
    processingType = [],
    isic4 = [],
    combineFacilityProcessingIsic = '',
    embed = false,
    isic4TaxonomyConfig = null,
} = {}) => ({
    filterOptions: {
        contributorTypes: {
            data: [],
            fetching: false,
            error: null,
        },
        taxonomyCounts: {
            facility_processing: { data: null },
            isic4: { data: null },
        },
        numberOfWorkers: {
            data: [],
            fetching: false,
            error: null,
        },
        isic4TaxonomyConfig: {
            data: isic4TaxonomyConfig,
            fetching: false,
            error: null,
        },
        isic4Taxonomy: {
            data: null,
            taxonomyUrl: null,
            fetching: false,
            error: null,
        },
    },
    filters: {
        contributorTypes: [],
        parentCompany: [],
        facilityType,
        processingType,
        isic4,
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
        combineFacilityProcessingIsic,
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

    const renderComponent = (preloadedState = createPreloadedState()) =>
        renderWithProviders(<FilterSidebarExtendedSearch />, {
            preloadedState,
        });

    test('hides the ISIC filter when the taxonomy feature is disabled', () => {
        const { queryByTestId } = renderComponent(
            createPreloadedState({
                isic4TaxonomyConfig: {
                    enabled: false,
                    version: 1,
                    taxonomyUrl: null,
                },
            }),
        );

        expect(queryByTestId('isic-taxonomy-search')).not.toBeInTheDocument();
    });

    test('shows the ISIC filter when the taxonomy feature is enabled', async () => {
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

    test('hides the combine checkbox when the taxonomy feature is disabled', () => {
        const { queryByLabelText } = renderComponent(
            createPreloadedState({
                isic4TaxonomyConfig: {
                    enabled: false,
                    version: 1,
                    taxonomyUrl: null,
                },
                facilityType: [{ value: 'Factory', label: 'Factory' }],
                isic4: [{ value: '0111', label: '0111 - Growing of cereals' }],
            }),
        );

        expect(
            queryByLabelText('Match both facility type and ISIC categories'),
        ).not.toBeInTheDocument();
    });

    test('shows the combine checkbox when enabled and all selections exist', () => {
        const { getByLabelText } = renderComponent(
            createPreloadedState({
                isic4TaxonomyConfig: {
                    enabled: true,
                    version: 1,
                    taxonomyUrl: '/api/taxonomy/isic4/?v=1',
                },
                processingType: [
                    { value: 'Printing', label: 'Printing' },
                ],
                isic4: [{ value: '0111', label: '0111 - Growing of cereals' }],
            }),
        );

        expect(
            getByLabelText('Match both facility type and ISIC categories'),
        ).toBeInTheDocument();
    });
});
