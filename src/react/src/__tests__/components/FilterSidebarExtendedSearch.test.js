import React from 'react';
import { waitFor } from '@testing-library/react';

import FilterSidebarExtendedSearch from '../../components/FilterSidebarExtendedSearch';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { isIsic4TaxonomyFeatureEnabled } from '../../data/loadIsic4Taxonomy';

jest.mock('../../data/loadIsic4Taxonomy', () => ({
    isIsic4TaxonomyFeatureEnabled: jest.fn(),
    loadIsic4Taxonomy: jest.fn(),
}));

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
        jest.clearAllMocks();
    });

    const renderComponent = (preloadedState = createPreloadedState()) =>
        renderWithProviders(<FilterSidebarExtendedSearch />, {
            preloadedState,
        });

    test('hides the ISIC filter when the taxonomy feature is disabled', () => {
        isIsic4TaxonomyFeatureEnabled.mockReturnValue(false);

        const { queryByTestId } = renderComponent();

        expect(queryByTestId('isic-taxonomy-search')).not.toBeInTheDocument();
    });

    test('shows the ISIC filter when the taxonomy feature is enabled', async () => {
        isIsic4TaxonomyFeatureEnabled.mockReturnValue(true);

        const { getByTestId } = renderComponent();

        await waitFor(() => {
            expect(getByTestId('isic-taxonomy-search')).toBeInTheDocument();
        });
    });

    test('hides the combine checkbox when the taxonomy feature is disabled', () => {
        isIsic4TaxonomyFeatureEnabled.mockReturnValue(false);

        const { queryByLabelText } = renderComponent(
            createPreloadedState({
                facilityType: [{ value: 'Factory', label: 'Factory' }],
                isic4: [{ value: '0111', label: '0111 - Growing of cereals' }],
            }),
        );

        expect(
            queryByLabelText('Match both facility type and ISIC categories'),
        ).not.toBeInTheDocument();
    });

    test('shows the combine checkbox when enabled and all selections exist', () => {
        isIsic4TaxonomyFeatureEnabled.mockReturnValue(true);

        const { getByLabelText } = renderComponent(
            createPreloadedState({
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
