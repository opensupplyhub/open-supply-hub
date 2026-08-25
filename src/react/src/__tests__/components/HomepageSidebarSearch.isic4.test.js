import React from 'react';
import { fireEvent } from '@testing-library/react';

import HomepageSidebarSearch from '../../components/HomepageSidebarSearch';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../components/Filters/TextSearchFilter', () => () => null);
jest.mock('../../components/Filters/ContributorFilter', () => () => null);
jest.mock('../../components/Filters/CountryNameFilter', () => () => null);
jest.mock('../../components/Filters/SectorFilter', () => () => null);
jest.mock(
    '../../components/Filters/DataPartnersFilter/DataPartnersFilter',
    () => () => null,
);
jest.mock('../../components/FilterSidebarExtendedSearch', () => () => null);
jest.mock('../../components/FeatureFlag', () => ({ children }) => children);
jest.mock('../../components/ShowOnly', () => ({ when, children }) =>
    when ? children : null,
);
jest.mock('../../components/TitledDrawer', () => ({ children }) => children);
jest.mock('../../actions/ui', () => ({
    recordSearchTabResetButtonClick: () => ({
        type: 'RECORD_SEARCH_TAB_RESET_BUTTON_CLICK',
    }),
}));

const createPreloadedState = () => ({
    filterOptions: {
        contributors: { data: [], fetching: false, error: null },
        countries: { data: [], fetching: false, error: null },
    },
    filters: {
        facilityFreeTextQuery: '',
        contributors: [],
        contributorTypes: [],
        countries: [],
        claimStatuses: [],
        sectors: [],
        sortAlgorithm: '',
        parentCompany: [],
        facilityType: [],
        processingType: [],
        isic4: [{ value: 'section:C', label: 'C Manufacturing' }],
        productType: [],
        numberOfWorkers: [],
        dataSources: [],
        moderationStatuses: [],
        nativeLanguageName: '',
        combineContributors: '',
        boundary: null,
        lists: [],
        partnerContributors: [],
    },
    facilities: {
        facilities: { data: null, fetching: false },
    },
    embeddedMap: {
        embed: false,
        config: {
            text_search_label: '',
            extended_fields: [],
        },
    },
});

describe('HomepageSidebarSearch ISIC reset', () => {
    test('counts ISIC as an active filter and resets it', () => {
        const { getByText, queryByText, reduxStore } = renderWithProviders(
            <HomepageSidebarSearch
                history={{
                    replace: jest.fn(),
                    location: { search: '' },
                }}
            />,
            { preloadedState: createPreloadedState() },
        );

        expect(getByText('1 More Search Filter')).toBeInTheDocument();

        fireEvent.click(getByText('Reset Search'));

        expect(reduxStore.getState().filters.isic4).toEqual([]);
        expect(queryByText('Reset Search')).not.toBeInTheDocument();
    });
});
