import React from 'react';

import FilterSidebarExtendedSearch from '../../components/FilterSidebarExtendedSearch';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../components/Filters/IsicSearch', () => ({
    __esModule: true,
    default: () => <div>Industry Classification</div>,
}));

jest.mock('../../components/Filters/StyledSelect', () => ({
    __esModule: true,
    default: ({ label }) => <div>{label}</div>,
}));

const createPreloadedState = ({ embed = false, isicSwitch = false } = {}) => ({
    filterOptions: {
        contributorTypes: { data: [], fetching: false, error: null },
        facilityProcessingType: { data: [], fetching: false, error: null },
        numberOfWorkers: { data: [], fetching: false, error: null },
    },
    filters: {
        contributorTypes: [],
        parentCompany: [],
        facilityType: [],
        processingType: [],
        productType: [],
        numberOfWorkers: [],
        nativeLanguageName: '',
    },
    facilities: { facilities: { data: null, fetching: false } },
    embeddedMap: { embed, config: { extended_fields: [] } },
    featureFlags: { flags: { enable_isic_taxonomy: isicSwitch } },
});

describe('FilterSidebarExtendedSearch Industry Classification', () => {
    const render = options =>
        renderWithProviders(<FilterSidebarExtendedSearch />, {
            preloadedState: createPreloadedState(options),
        });

    test('shows the field when the enable_isic_taxonomy switch is on', () => {
        const { queryByText } = render({ isicSwitch: true });
        expect(queryByText('Industry Classification')).toBeTruthy();
    });

    test('hides it when the switch is off', () => {
        const { queryByText } = render({ isicSwitch: false });
        expect(queryByText('Industry Classification')).toBeNull();
    });

    test('hides it on embedded maps', () => {
        const { queryByText } = render({ isicSwitch: true, embed: true });
        expect(queryByText('Industry Classification')).toBeNull();
    });
});
