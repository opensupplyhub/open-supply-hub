import React from 'react';
import { MemoryRouter, Route, Switch } from 'react-router-dom';
import { cleanup, screen, waitFor } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ProductionLocationDetailsContainer from '../../components/ProductionLocation/ProductionLocationDetailsContainer/ProductionLocationDetailsContainer';
import { fetchSingleFacility } from '../../actions/facilities';
import apiRequest from '../../util/apiRequest';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: {
        get: jest.fn(),
    },
}));

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

jest.mock('../../actions/facilities', () => {
    const actual = jest.requireActual('../../actions/facilities');
    return {
        ...actual,
        fetchSingleFacility: jest.fn(actual.fetchSingleFacility),
        fetchFacilities: () => () => {},
    };
});

jest.mock('../../actions/filters', () => ({
    setFiltersFromQueryString: () => ({ type: 'noop' }),
    resetAllFilters: () => ({ type: 'RESET_ALL_FILTERS' }),
}));

jest.mock('../../actions/partnerFieldGroups', () => ({
    startFetchPartnerFieldGroups: () => ({ type: 'noop' }),
    failFetchPartnerFieldGroups: () => ({ type: 'noop' }),
    completeFetchPartnerFieldGroups: () => ({ type: 'noop' }),
    fetchPartnerFieldGroups: () => () => {},
}));

const { fetchSingleFacility: realFetchSingleFacility } = jest.requireActual(
    '../../actions/facilities',
);

const defaultFacilitiesState = {
    facilities: {
        data: null,
        fetching: false,
        error: null,
        nextPageURL: null,
        isInfiniteLoading: false,
        hasAppliedFilters: false,
    },
    singleFacility: {
        data: null,
        fetching: false,
        error: null,
        requestedOsId: null,
        requestToken: null,
    },
};

const baseState = {
    facilities: defaultFacilitiesState,
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
            ...defaultFacilitiesState,
            ...(stateOverrides.facilities || {}),
            facilities: {
                ...defaultFacilitiesState.facilities,
                ...(stateOverrides.facilities?.facilities || {}),
            },
            singleFacility: {
                ...defaultFacilitiesState.singleFacility,
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
    beforeEach(() => {
        fetchSingleFacility.mockImplementation(() => () => {});
    });

    afterEach(() => {
        jest.clearAllMocks();
        cleanup();
    });

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
                singleFacility: {
                    data: { id: 'OS12345' },
                    requestedOsId: 'OS12345',
                },
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

    test('redirects when loaded facility id differs from requested alias os id', () => {
        renderWithProviders(
            <MemoryRouter
                initialEntries={['/production-locations/MX2024211WFBSJJ']}
            >
                <Switch>
                    <Route
                        path="/production-locations/MX2024211T0VH2S"
                        render={() => <div data-testid="redirect-target" />}
                    />
                    <Route
                        path="/production-locations/:osID"
                        component={ProductionLocationDetailsContainer}
                    />
                </Switch>
            </MemoryRouter>,
            {
                preloadedState: {
                    facilities: {
                        singleFacility: {
                            data: { id: 'MX2024211T0VH2S' },
                            fetching: false,
                            error: null,
                            requestedOsId: 'MX2024211WFBSJJ',
                        },
                    },
                    filters: { contributors: [] },
                    featureFlags: {
                        flags: { enable_production_location_page: true },
                    },
                    embeddedMap: { embed: null },
                    partnerFieldGroups: {
                        fetching: false,
                        data: { results: [] },
                        error: null,
                    },
                },
            },
        );

        expect(screen.getByTestId('redirect-target')).toBeInTheDocument();
        expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });

    test('shows spinner instead of redirecting when loaded data is stale', () => {
        renderContainer(
            {
                facilities: {
                    singleFacility: {
                        data: { id: 'MX2024211T0VH2S' },
                        fetching: false,
                        error: null,
                        requestedOsId: 'MX2024211WFBSJJ',
                    },
                },
            },
            'MX2024211DIFFERENT',
        );

        expect(screen.getByRole('progressbar')).toBeInTheDocument();
        expect(screen.queryByTestId('details-content')).not.toBeInTheDocument();
    });

    test('redirects when URL casing differs from canonical OS ID', () => {
        renderWithProviders(
            <MemoryRouter
                initialEntries={['/production-locations/mx2024211t0vh2s']}
            >
                <Switch>
                    <Route
                        path="/production-locations/MX2024211T0VH2S"
                        render={() => <div data-testid="redirect-target" />}
                    />
                    <Route
                        path="/production-locations/:osID"
                        component={ProductionLocationDetailsContainer}
                    />
                </Switch>
            </MemoryRouter>,
            {
                preloadedState: {
                    facilities: {
                        singleFacility: {
                            data: { id: 'MX2024211T0VH2S' },
                            fetching: false,
                            error: null,
                            requestedOsId: 'mx2024211t0vh2s',
                        },
                    },
                    filters: { contributors: [] },
                    featureFlags: {
                        flags: { enable_production_location_page: true },
                    },
                    embeddedMap: { embed: null },
                    partnerFieldGroups: {
                        fetching: false,
                        data: { results: [] },
                        error: null,
                    },
                },
            },
        );

        expect(screen.getByTestId('redirect-target')).toBeInTheDocument();
    });

    describe('single facility fetch race condition', () => {
        const OS_ID = 'CN20200165JMYV0';

        const makeFacilityData = name => ({
            id: OS_ID,
            type: 'Feature',
            properties: {
                name,
                os_id: OS_ID,
            },
        });

        const createDeferred = () => {
            let resolve;
            const promise = new Promise(res => {
                resolve = res;
            });
            return { promise, resolve };
        };

        beforeEach(() => {
            apiRequest.get.mockReset();
        });

        test('ignores a stale response when a newer request for the same OS ID completes first', async () => {
            const deferreds = [createDeferred(), createDeferred()];
            let callIndex = 0;

            // Mount with fetch stubbed so we control the two in-flight requests
            // the same way ProductionLocationDetailsContainer would trigger them.
            const { reduxStore } = renderContainer({}, OS_ID);

            fetchSingleFacility.mockImplementation(realFetchSingleFacility);
            apiRequest.get.mockImplementation(() => {
                if (callIndex >= deferreds.length) {
                    throw new Error(
                        `Unexpected apiRequest.get call #${callIndex + 1}`,
                    );
                }
                const deferred = deferreds[callIndex];
                callIndex += 1;
                return deferred.promise;
            });

            const firstRequest = reduxStore.dispatch(
                fetchSingleFacility(OS_ID, 0, null, true),
            );
            const secondRequest = reduxStore.dispatch(
                fetchSingleFacility(OS_ID, 0, null, true),
            );

            expect(apiRequest.get).toHaveBeenCalledTimes(2);

            deferreds[1].resolve({
                data: makeFacilityData('Second response'),
            });
            await secondRequest;

            await waitFor(() => {
                expect(
                    reduxStore.getState().facilities.singleFacility.data
                        ?.properties?.name,
                ).toBe('Second response');
            });
            expect(
                reduxStore.getState().facilities.singleFacility.error,
            ).toBeNull();

            await waitFor(() => {
                expect(screen.getByTestId('details-content')).toBeInTheDocument();
            });

            deferreds[0].resolve({ data: makeFacilityData('Stale response') });
            await firstRequest;

            expect(
                reduxStore.getState().facilities.singleFacility.data.properties
                    .name,
            ).toBe('Second response');
            expect(
                reduxStore.getState().facilities.singleFacility.error,
            ).toBeNull();
            expect(screen.getByTestId('details-content')).toBeInTheDocument();
        });
    });
});
