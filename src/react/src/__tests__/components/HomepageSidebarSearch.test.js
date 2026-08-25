import React from 'react';
import { fireEvent, render } from '@testing-library/react';

import {
    HomepageSidebarSearch,
    mapDispatchToProps,
} from '../../components/HomepageSidebarSearch';

const mockCommitPendingQuery = jest.fn();

jest.mock('../../components/ShowOnly', () => ({ when, children }) =>
    when ? children : null,
);
jest.mock('../../components/FeatureFlag', () => ({ children }) => children);
jest.mock('../../components/Filters/TextSearchFilter', () => () => null);
jest.mock('../../components/Filters/ContributorFilter', () => () => null);
jest.mock('../../components/Filters/CountryNameFilter', () => () => null);
jest.mock('../../components/Filters/SectorFilter', () => () => null);
jest.mock(
    '../../components/Filters/DataPartnersFilter/DataPartnersFilter',
    () => () => null,
);
jest.mock('../../components/FilterSidebarExtendedSearch', () => {
    const ReactModule = jest.requireActual('react');

    return ReactModule.forwardRef((props, ref) => {
        ReactModule.useImperativeHandle(ref, () => ({
            commitPendingQuery: mockCommitPendingQuery,
        }));
        return <div>Extended search</div>;
    });
});
jest.mock('../../components/TitledDrawer', () => ({
    open,
    onClose,
    children,
}) =>
    open ? (
        <div>
            <button type="button" onClick={onClose}>
                Close drawer
            </button>
            {children}
        </div>
    ) : null);

const defaultProps = {
    resetFilters: jest.fn(),
    facilityFreeTextQuery: '',
    contributors: [],
    contributorTypes: [],
    countries: [],
    sectors: [],
    parentCompany: [],
    facilityType: [],
    processingType: [],
    productType: [],
    numberOfWorkers: [],
    fetchingFacilities: false,
    searchForFacilities: jest.fn(),
    fetchingOptions: false,
    embed: false,
    lists: [],
    classes: {
        font: '',
        searchButton: '',
        reset: '',
        buttonGroup: '',
        controlPanelContentStyles: '',
        headerStyle: '',
    },
    embedExtendedFields: [],
    resetHiddenFilters: jest.fn(),
    partnerContributors: [],
};

describe('HomepageSidebarSearch component', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        mockCommitPendingQuery.mockReturnValue(true);
    });

    test('commits pending processing text before finding facilities', () => {
        const searchForFacilities = jest.fn();
        const { getByRole } = render(
            <HomepageSidebarSearch
                {...defaultProps}
                searchForFacilities={searchForFacilities}
            />,
        );
        fireEvent.click(
            getByRole('button', {
                name: 'More Search Filters',
            }),
        );

        fireEvent.click(
            getByRole('button', {
                name: 'Find Facilities',
            }),
        );

        expect(mockCommitPendingQuery).toHaveBeenCalledTimes(1);
        expect(searchForFacilities).toHaveBeenCalledTimes(1);
    });

    test('keeps the drawer open when pending processing text is invalid', () => {
        const { getByRole } = render(
            <HomepageSidebarSearch {...defaultProps} />,
        );
        fireEvent.click(
            getByRole('button', {
                name: 'More Search Filters',
            }),
        );
        mockCommitPendingQuery.mockReturnValue(false);

        fireEvent.click(getByRole('button', { name: 'Apply Filters' }));
        expect(
            getByRole('button', { name: 'Apply Filters' }),
        ).toBeInTheDocument();

        fireEvent.click(getByRole('button', { name: 'Close drawer' }));
        expect(
            getByRole('button', { name: 'Close drawer' }),
        ).toBeInTheDocument();
        expect(mockCommitPendingQuery).toHaveBeenCalledTimes(2);
    });

    test('blocks navigation when pending processing text is invalid', () => {
        const searchForFacilities = jest.fn();
        mockCommitPendingQuery.mockReturnValue(false);
        const { getByRole } = render(
            <HomepageSidebarSearch
                {...defaultProps}
                searchForFacilities={searchForFacilities}
            />,
        );
        fireEvent.click(
            getByRole('button', {
                name: 'More Search Filters',
            }),
        );

        fireEvent.click(
            getByRole('button', {
                name: 'Find Facilities',
            }),
        );

        expect(searchForFacilities).not.toHaveBeenCalled();
    });

    test('builds navigation from Redux state after pending text commits', () => {
        const replace = jest.fn();
        const getState = () => ({
            filters: {
                processingType: [
                    {
                        value: 'cement mixing',
                        label: 'cement mixing',
                    },
                ],
            },
            embeddedMap: { embed: false },
        });
        const dispatch = action => action(dispatch, getState);
        const { searchForFacilities } = mapDispatchToProps(dispatch, {
            history: { replace },
        });

        searchForFacilities();

        expect(replace).toHaveBeenCalledWith(
            '/facilities?processing_type=cement+mixing',
        );
    });
});
