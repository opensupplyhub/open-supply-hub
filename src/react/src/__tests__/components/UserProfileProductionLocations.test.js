import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import UserProfileProductionLocations from '../../components/UserProfileProductionLocations/UserProfileProductionLocations';

const makeFacility = (id, name, address, countryCode) => ({
    id,
    properties: { name, address, country_code: countryCode },
});

const buildState = (overrides = {}) => ({
    profile: {
        productionLocations: {
            data: [],
            fetching: false,
            fetchingMore: false,
            nextPageUrl: null,
            error: null,
            ...overrides,
        },
    },
});

const renderComponent = (stateOverrides = {}) =>
    renderWithProviders(
        <MemoryRouter>
            <UserProfileProductionLocations />
        </MemoryRouter>,
        { preloadedState: buildState(stateOverrides) },
    );

describe('UserProfileProductionLocations', () => {
    test('renders nothing when there are no facilities', () => {
        const { container } = renderComponent();
        expect(container.firstChild).toBeNull();
    });

    test('shows a loading spinner when fetching', () => {
        const { getByRole } = renderComponent({ fetching: true });
        expect(getByRole('progressbar')).toBeInTheDocument();
    });

    test('shows an error message', () => {
        const { getByText } = renderComponent({
            error: ['Something went wrong'],
        });
        expect(getByText('Something went wrong')).toBeInTheDocument();
    });

    test('renders facility rows', () => {
        const facilities = [
            makeFacility('OS123', 'Factory A', '123 Main St', 'US'),
            makeFacility('OS456', 'Factory B', '456 Oak Ave', 'GB'),
        ];

        const { getByText } = renderComponent({ data: facilities });

        expect(getByText('OS123')).toBeInTheDocument();
        expect(getByText('Factory A')).toBeInTheDocument();
        expect(getByText('OS456')).toBeInTheDocument();
        expect(getByText('Factory B')).toBeInTheDocument();
    });

    test('shows Load More button when nextPageUrl is set', () => {
        const facilities = [makeFacility('OS1', 'Fac', 'Addr', 'US')];
        const { getByTestId } = renderComponent({
            data: facilities,
            nextPageUrl: '/api/next-page',
        });
        expect(
            getByTestId('production-locations-load-more'),
        ).toBeInTheDocument();
    });

    test('does not show Load More when there is no next page', () => {
        const facilities = [makeFacility('OS1', 'Fac', 'Addr', 'US')];
        const { queryByTestId } = renderComponent({ data: facilities });
        expect(
            queryByTestId('production-locations-load-more'),
        ).not.toBeInTheDocument();
    });
});
