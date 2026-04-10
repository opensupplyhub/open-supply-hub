import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { screen, within } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ProductionLocationDetailsGeneralFields from '../../components/ProductionLocation/ProductionLocationDetailsGeneralFields/ProductionLocationDetailsGeneralFields';

describe('ProductionLocationDetailsGeneralFields component', () => {
    const mockDataWithVisibleFields = {
        id: 'XX2025000000000',
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [0, 0] },
        properties: {
            name: 'Test Facility Name',
            country_code: 'XX',
            os_id: 'XX2025000000000',
            other_names: [],
            contributors: [],
            country_name: 'Test Country',
            claim_info: null,
            other_locations: [],
            is_closed: false,
            activity_reports: [],
            contributor_fields: [],
            new_os_id: null,
            has_inexact_coordinates: false,
            extended_fields: {
                name: [
                    {
                        value: 'Test Facility Name',
                        field_name: 'name',
                        contributor_id: 1,
                        contributor_name: 'Test Contributor',
                        updated_at: '2025-01-01T00:00:00.000Z',
                        created_at: '2025-01-01T00:00:00.000Z',
                    },
                ],
                address: [],
                number_of_workers: [],
                native_language_name: [],
                facility_type: [],
                processing_type: [],
                product_type: [],
                parent_company: [],
                parent_company_os_id: [],
                duns_id: [],
                lei_id: [],
                rba_id: [],
                isic_4: [],
            },
            created_from: {
                created_at: '2025-01-01T00:00:00.000Z',
                contributor: 'Test Contributor',
            },
            sector: [
                {
                    updated_at: '2025-01-01T00:00:00.000Z',
                    contributor_id: 1,
                    contributor_name: 'Test Contributor',
                    values: ['Apparel'],
                    is_from_claim: false,
                    created_at: '2025-01-01T00:00:00.000Z',
                },
                {
                    updated_at: '2025-01-02T00:00:00.000Z',
                    contributor_id: 2,
                    contributor_name: 'Other Contributor',
                    values: ['Apparel'],
                    is_from_claim: false,
                    created_at: '2025-01-02T00:00:00.000Z',
                },
            ],
            is_claimed: false,
        },
    };

    const defaultPreloadedState = {
        featureFlags: {
            fetching: false,
            flags: {},
        },
    };

    const renderComponent = (props = {}, preloadedState = defaultPreloadedState) =>
        renderWithProviders(
            <MemoryRouter>
                <ProductionLocationDetailsGeneralFields
                    data={mockDataWithVisibleFields}
                    {...props}
                />
            </MemoryRouter>,
            { preloadedState },
        );

    test('renders the general fields section', () => {
        renderComponent();
        expect(
            screen.getByTestId('production-location-details-general-fields'),
        ).toBeInTheDocument();
    });

    test('renders at least one data point when data has visible fields', () => {
        renderComponent();
        const dataPoints = screen.getAllByTestId('data-point');
        expect(dataPoints.length).toBeGreaterThanOrEqual(1);
    });

    test('renders data points with labels and values', () => {
        renderComponent();
        const dataPoints = screen.getAllByTestId('data-point');
        const first = dataPoints[0];
        expect(within(first).getByTestId('data-point-label')).toBeInTheDocument();
        expect(within(first).getByTestId('data-point-value')).toBeInTheDocument();
    });

    test('renders the contributions drawer when opened via sources button', () => {
        renderComponent();
        const sourcesButtons = screen.queryAllByTestId('data-point-sources-button');
        expect(sourcesButtons.length).toBeGreaterThan(0);
        sourcesButtons[0].click();
        expect(screen.getByTestId('contributions-drawer')).toBeInTheDocument();
    });

    test('drawer has title and close control when opened', () => {
        renderComponent();
        const sourcesButtons = screen.queryAllByTestId('data-point-sources-button');
        if (sourcesButtons.length > 0) {
            sourcesButtons[0].click();
            expect(screen.getByTestId('contributions-drawer-title')).toBeInTheDocument();
            expect(screen.getByTestId('contributions-drawer-close')).toBeInTheDocument();
        }
    });

    test('opening a field with sources opens the drawer', () => {
        renderComponent();
        const sourcesButtons = screen.queryAllByTestId('data-point-sources-button');
        expect(sourcesButtons.length).toBeGreaterThan(0);
        sourcesButtons[0].click();
        const drawer = screen.getByTestId('contributions-drawer');
        expect(drawer).toBeInTheDocument();
    });

    test('renders no data points when data is null', () => {
        renderComponent({ data: null });
        const container = screen.getByTestId('production-location-details-general-fields');
        const dataPoints = within(container).queryAllByTestId('data-point');
        expect(dataPoints).toHaveLength(0);
    });

    test('renders no data points when data is undefined', () => {
        renderComponent({ data: undefined });
        const container = screen.getByTestId('production-location-details-general-fields');
        const dataPoints = within(container).queryAllByTestId('data-point');
        expect(dataPoints).toHaveLength(0);
    });
});
