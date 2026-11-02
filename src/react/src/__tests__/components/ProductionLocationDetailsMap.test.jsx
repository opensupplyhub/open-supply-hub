import React from 'react';
import { MemoryRouter, Route } from 'react-router-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { createStore } from 'redux';
import { Provider } from 'react-redux';

import apiRequest from '../../util/apiRequest';
import ProductionLocationDetailsMap from '../../components/ProductionLocation/ProductionLocationDetailsMap/ProductionLocationDetailsMap';

jest.mock('leaflet', () => ({ icon: jest.fn(() => ({})) }));
jest.mock('leaflet/dist/leaflet.css', () => {});

jest.mock('react-leaflet', () => ({
    Map: ({ children }) => <div data-testid="leaflet-map">{children}</div>,
    TileLayer: () => null,
    Marker: ({ position, title }) => (
        <div
            data-testid="map-marker"
            data-position={JSON.stringify(position)}
            data-title={title || ''}
        />
    ),
}));

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { get: jest.fn(), post: jest.fn() },
}));

jest.mock('react-leaflet-control', () => ({ children }) => <>{children}</>);

jest.mock('../../components/VectorTileFacilitiesLayer', () => ({
    __esModule: true,
    default: () => null,
    createMarkerIcon: () => ({}),
}));
jest.mock('../../components/VectorTileFacilityGridLayer', () => () => null);
jest.mock('../../components/VectorTileGridLegend', () => () => null);
jest.mock('../../components/Candidate/CandidatePolygonsLayer', () => ({
    __esModule: true,
    default: () => <div data-testid="candidate-polygons-layer" />,
}));
jest.mock('../../components/Candidate/CandidateValidationPanel', () => ({
    __esModule: true,
    default: () => null,
    PANEL_VARIANTS: { OVERLAY: 'overlay', INLINE: 'inline' },
}));

jest.mock(
    '../../components/ProductionLocation/DataPoint/DataPoint',
    () => ({
        __esModule: true,
        default: ({ label, value, drawerData, onOpenDrawer, renderDrawer }) => {
            const hasContributions =
                Array.isArray(drawerData?.contributions) &&
                drawerData.contributions.length > 0 &&
                !!onOpenDrawer;
            return (
                <div data-testid="data-point">
                    <span data-testid="data-point-label">{label}</span>
                    <span data-testid="data-point-value">{value}</span>
                    {hasContributions && (
                        <button
                            type="button"
                            data-testid="data-point-sources-button"
                            onClick={onOpenDrawer}
                        >
                            {`+${drawerData.contributions.length} data sources`}
                        </button>
                    )}
                    {typeof renderDrawer === 'function' && renderDrawer()}
                </div>
            );
        },
    }),
);

jest.mock(
    '../../components/ProductionLocation/ContributionsDrawer/ContributionsDrawer',
    () => ({
        __esModule: true,
        default: ({ open }) =>
            open ? <div data-testid="contributions-drawer" /> : null,
    }),
);

const FACILITY_ADDRESS = '123 Main St, New York';
const FACILITY_LNG = -73.8314318;
const FACILITY_LAT = 40.762569;
const EXPECTED_COORD_DISPLAY = `${FACILITY_LAT}, ${FACILITY_LNG}`;

const makeFacility = (overrides = {}) => ({
    type: 'Feature',
    geometry: {
        type: 'Point',
        coordinates: [FACILITY_LNG, FACILITY_LAT],
    },
    properties: {
        address: FACILITY_ADDRESS,
        other_locations: [],
        created_from: {
            contributor: 'Test Org',
            created_at: '2023-01-01T00:00:00Z',
        },
        extended_fields: {
            address: [
                {
                    value: FACILITY_ADDRESS,
                    contributor_name: 'Test Org',
                    contributor_id: 1,
                    created_at: '2023-01-01T00:00:00Z',
                    updated_at: '2023-01-01T00:00:00Z',
                    is_from_claim: false,
                },
            ],
        },
    },
    ...overrides,
});

const makeStore = (facilityData, { pilotEnabled = true } = {}) =>
    createStore(() => ({
        facilities: { singleFacility: { data: facilityData } },
        vectorTileLayer: { gridColorRamp: [] },
        // OSDEV-3627: the candidate footprint layer sits behind the
        // earth_genome_candidates switch (read via /api-feature-flags/).
        featureFlags: {
            fetching: false,
            flags: { earth_genome_candidates: pilotEnabled },
        },
        embeddedMap: { embed: false },
    }));

const renderMap = (facilityData = null, storeOptions = {}) =>
    render(
        <Provider store={makeStore(facilityData, storeOptions)}>
            <MemoryRouter initialEntries={['/production-locations/OS12345']}>
                <Route
                    path="/production-locations/:osID"
                    component={ProductionLocationDetailsMap}
                />
            </MemoryRouter>
        </Provider>,
    );

describe('ProductionLocationDetailsMap', () => {
    describe('pilot switch (OSDEV-3627)', () => {
        it('draws the candidate footprint layer while the switch is on', () => {
            renderMap(makeFacility());

            expect(
                screen.getByTestId('candidate-polygons-layer'),
            ).toBeInTheDocument();
        });

        it('leaves the candidate footprint layer out while the switch is off', () => {
            renderMap(makeFacility(), { pilotEnabled: false });

            expect(
                screen.queryByTestId('candidate-polygons-layer'),
            ).not.toBeInTheDocument();
        });
    });

    describe('suggested match marker (OSDEV-3247)', () => {
        it('draws the chosen match as a second marker from its facility detail', async () => {
            apiRequest.get.mockResolvedValue({
                data: {
                    geometry: { coordinates: [-87.003, 34.213] },
                    properties: { name: 'Riverside Poultry Plant' },
                },
            });
            render(
                <Provider store={makeStore(makeFacility())}>
                    <MemoryRouter initialEntries={['/production-locations/OS12345']}>
                        <Route
                            path="/production-locations/:osID"
                            render={props => (
                                <ProductionLocationDetailsMap
                                    {...props}
                                    highlightedMatchOsId="US2026MATCH0001"
                                />
                            )}
                        />
                    </MemoryRouter>
                </Provider>,
            );

            await waitFor(() =>
                expect(
                    screen
                        .getAllByTestId('map-marker')
                        .map(el => el.getAttribute('data-title')),
                ).toContain('Riverside Poultry Plant'),
            );
            const match = screen
                .getAllByTestId('map-marker')
                .find(el => el.getAttribute('data-title') === 'Riverside Poultry Plant');
            expect(JSON.parse(match.getAttribute('data-position'))).toEqual([
                34.213,
                -87.003,
            ]);
            expect(apiRequest.get).toHaveBeenCalledWith(
                expect.stringContaining('/api/facilities/US2026MATCH0001/'),
            );
        });
    });

    describe('section header', () => {
        it('renders the "Geographic Information" section title', () => {
            renderMap(makeFacility());

            expect(
                screen.getByText('Geographic Information'),
            ).toBeInTheDocument();
        });
    });

    describe('info grid', () => {
        it('renders the info grid container', () => {
            renderMap(makeFacility());

            expect(
                screen.getByTestId('production-location-info-grid'),
            ).toBeInTheDocument();
        });

        it('renders an address row and a coordinates row', () => {
            renderMap(makeFacility());

            expect(
                screen.getByTestId('production-location-address-row'),
            ).toBeInTheDocument();
            expect(
                screen.getByTestId('production-location-coordinates-row'),
            ).toBeInTheDocument();
        });
    });

    describe('address DataPoint', () => {
        it('renders the "Address" label', () => {
            renderMap(makeFacility());

            const addressRow = screen.getByTestId(
                'production-location-address-row',
            );
            expect(addressRow).toHaveTextContent('Address');
        });

        it('displays the facility address', () => {
            renderMap(makeFacility());

            const addressRow = screen.getByTestId(
                'production-location-address-row',
            );
            expect(addressRow).toHaveTextContent(FACILITY_ADDRESS);
        });

        it('appends " - {country_name}" to the displayed address when country_name is present', () => {
            const facility = makeFacility();
            facility.properties.country_name = 'United States';
            renderMap(facility);

            const addressRow = screen.getByTestId(
                'production-location-address-row',
            );
            expect(addressRow).toHaveTextContent(
                `${FACILITY_ADDRESS} - United States`,
            );
        });

        it('does not append a country suffix when country_name is absent', () => {
            renderMap(makeFacility());

            const addressRow = screen.getByTestId(
                'production-location-address-row',
            );
            const valueSpan = addressRow.querySelector(
                '[data-testid="data-point-value"]',
            );
            expect(valueSpan.textContent).toBe(FACILITY_ADDRESS);
        });

        it('shows "—" when properties.address is empty', () => {
            const facility = makeFacility();
            facility.properties.address = '';
            facility.properties.extended_fields.address = [];
            renderMap(facility);

            const addressRow = screen.getByTestId(
                'production-location-address-row',
            );
            expect(addressRow).toHaveTextContent('—');
        });
    });

    describe('coordinates DataPoint', () => {
        it('renders the "Coordinates" label', () => {
            renderMap(makeFacility());

            const coordRow = screen.getByTestId(
                'production-location-coordinates-row',
            );
            expect(coordRow).toHaveTextContent('Coordinates');
        });

        it('displays coordinates formatted as "lat, lng"', () => {
            renderMap(makeFacility());

            const coordRow = screen.getByTestId(
                'production-location-coordinates-row',
            );
            expect(coordRow).toHaveTextContent(EXPECTED_COORD_DISPLAY);
        });

        it('shows "—" when geometry.coordinates is absent', () => {
            const facility = makeFacility({ geometry: null });
            renderMap(facility);

            const coordRow = screen.getByTestId(
                'production-location-coordinates-row',
            );
            expect(coordRow).toHaveTextContent('—');
        });
    });

    describe('sources button and drawer', () => {
        const facilityWithMultipleAddresses = makeFacility({
            properties: {
                address: FACILITY_ADDRESS,
                other_locations: [],
                created_from: {
                    contributor: 'Test Org',
                    created_at: '2023-01-01T00:00:00Z',
                },
                extended_fields: {
                    address: [
                        {
                            value: FACILITY_ADDRESS,
                            contributor_name: 'Test Org',
                            contributor_id: 1,
                            created_at: '2023-01-01T00:00:00Z',
                            updated_at: '2023-01-01T00:00:00Z',
                            is_from_claim: false,
                        },
                        {
                            value: '456 Second Ave',
                            contributor_name: 'Second Org',
                            contributor_id: 2,
                            created_at: '2023-03-01T00:00:00Z',
                            updated_at: '2023-03-01T00:00:00Z',
                            is_from_claim: false,
                        },
                    ],
                },
            },
        });

        it('shows the sources button when there are address contributions', () => {
            renderMap(facilityWithMultipleAddresses);

            expect(
                screen.getByTestId('data-point-sources-button'),
            ).toBeInTheDocument();
        });

        it('does not show the sources button when there is only one address entry', () => {
            renderMap(makeFacility());

            expect(
                screen.queryByTestId('data-point-sources-button'),
            ).not.toBeInTheDocument();
        });

        it('opens the ContributionsDrawer when the sources button is clicked', () => {
            renderMap(facilityWithMultipleAddresses);

            expect(
                screen.queryByTestId('contributions-drawer'),
            ).not.toBeInTheDocument();

            fireEvent.click(screen.getByTestId('data-point-sources-button'));

            expect(
                screen.getByTestId('contributions-drawer'),
            ).toBeInTheDocument();
        });
    });
});
