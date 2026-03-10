import React from 'react';
import { MemoryRouter, Route } from 'react-router-dom';
import { screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ProductionLocationDetailsContainer from '../../components/ProductionLocation/ProductionLocationDetailsContainer/ProductionLocationDetailsContainer';

jest.mock(
    '../../components/ProductionLocation/Sidebar/BackToSearch/BackToSearch',
    () => () => <div data-testid="back-to-search" />,
);
jest.mock(
    '../../components/ProductionLocation/Sidebar/NavBar/NavBar',
    () => () => <div data-testid="nav-bar" />,
);
jest.mock(
    '../../components/ProductionLocation/Sidebar/SupplyChain/SupplyChain',
    () => () => <div data-testid="supply-chain" />,
);
jest.mock(
    '../../components/ProductionLocation/Sidebar/ContributeFields/ContributeFields',
    () => () => <div data-testid="contribute-fields" />,
);
jest.mock(
    '../../components/ProductionLocation/ProductionLocationDetailsContent/ProductionLocationDetailsContent',
    () => () => <div data-testid="details-content" />,
);

jest.mock('../../actions/facilities', () => ({
    fetchSingleFacility: () => ({ type: 'noop' }),
    resetSingleFacility: () => ({ type: 'RESET_SINGLE_FACILITY' }),
    fetchFacilities: () => () => {},
}));

jest.mock('../../actions/partnerFieldGroups', () => ({
    startFetchPartnerFieldGroups: () => ({ type: 'noop' }),
    failFetchPartnerFieldGroups: () => ({ type: 'noop' }),
    completeFetchPartnerFieldGroups: () => ({ type: 'noop' }),
    fetchPartnerFieldGroups: () => () => {},
}));

const baseState = {
    facilities: {
        singleFacility: { data: null, fetching: false, error: null },
    },
    filters: { contributors: [] },
    featureFlags: {},
    embeddedMap: { embed: null },
    partnerFieldGroups: { fetching: false, data: { results: [] }, error: null },
};

const renderContainer = (stateOverrides = {}, osID = 'OS12345') => {
    const state = {
        ...baseState,
        ...stateOverrides,
        facilities: {
            ...baseState.facilities,
            ...(stateOverrides.facilities || {}),
            singleFacility: {
                ...baseState.facilities.singleFacility,
                ...(stateOverrides.facilities?.singleFacility || {}),
            },
        },
    };

    return renderWithProviders(
        <MemoryRouter initialEntries={[`/production-locations/${osID}`]}>
            <Route
                path="/production-locations/:osID"
                component={ProductionLocationDetailsContainer}
            />
        </MemoryRouter>,
        { preloadedState: state },
    );
};

describe('ProductionLocationDetailsContainer', () => {
    test('renders a loading spinner when fetching', () => {
        renderContainer({
            facilities: { singleFacility: { fetching: true } },
        });

        expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    test('renders error messages when errors exist', () => {
        renderContainer({
            facilities: {
                singleFacility: {
                    error: ['Something went wrong', 'Try again later'],
                },
            },
        });

        expect(screen.getByText('Something went wrong')).toBeInTheDocument();
        expect(screen.getByText('Try again later')).toBeInTheDocument();
    });

    test('renders main content when data is loaded', () => {
        renderContainer({
            facilities: {
                singleFacility: { data: { id: 'OS12345' } },
            },
        });

        expect(screen.getByTestId('back-to-search')).toBeInTheDocument();
        expect(screen.getByTestId('nav-bar')).toBeInTheDocument();
        expect(screen.getByTestId('supply-chain')).toBeInTheDocument();
        expect(screen.getByTestId('contribute-fields')).toBeInTheDocument();
        expect(screen.getByTestId('details-content')).toBeInTheDocument();
    });

    test('does not render main content while fetching', () => {
        renderContainer({
            facilities: { singleFacility: { fetching: true } },
        });

        expect(screen.queryByTestId('details-content')).not.toBeInTheDocument();
    });
});
