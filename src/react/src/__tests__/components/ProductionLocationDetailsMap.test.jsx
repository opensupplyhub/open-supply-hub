import React from 'react';
import { MemoryRouter, Route } from 'react-router-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import { createStore } from 'redux';
import { Provider } from 'react-redux';

import ProductionLocationDetailsMap from '../../components/ProductionLocation/ProductionLocationDetailsMap/ProductionLocationDetailsMap';

jest.mock('leaflet', () => ({ icon: jest.fn(() => ({})) }));
jest.mock('leaflet/dist/leaflet.css', () => {});

jest.mock('react-leaflet', () => ({
    Map: ({ children }) => <div data-testid="leaflet-map">{children}</div>,
    TileLayer: () => null,
    Marker: () => null,
}));

jest.mock('react-leaflet-control', () => ({ children }) => <>{children}</>);

jest.mock('../../components/VectorTileFacilitiesLayer', () => ({
    __esModule: true,
    default: () => null,
    createMarkerIcon: () => ({}),
}));
jest.mock('../../components/VectorTileFacilityGridLayer', () => () => null);
jest.mock('../../components/VectorTileGridLegend', () => () => null);

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

const makeStore = facilityData =>
    createStore(() => ({
        facilities: { singleFacility: { data: facilityData } },
        vectorTileLayer: { gridColorRamp: [] },
    }));

const renderMap = (facilityData = null) =>
    render(
        <Provider store={makeStore(facilityData)}>
            <MemoryRouter initialEntries={['/production-locations/OS12345']}>
                <Route
                    path="/production-locations/:osID"
                    component={ProductionLocationDetailsMap}
                />
            </MemoryRouter>
        </Provider>,
    );

describe('ProductionLocationDetailsMap', () => {
    describe('section header', () => {
        it('renders the "Geographic information" section title', () => {
            renderMap(makeFacility());

            expect(
                screen.getByText('Geographic information'),
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
