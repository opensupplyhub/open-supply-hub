import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import PartnerFieldItem from '../../components/ProductionLocation/PartnerSection/PartnerSectionItem/PartnerFieldItem';

describe('PartnerFieldItem component', () => {
    const defaultField = {
        fieldName: 'climate_trace',
        formatValue: undefined,
        label: 'Climate Data',
        partnerConfigFields: null,
    };

    const makeValue = (overrides = {}) => ({
        value: 'Scope 1 emissions: 100',
        created_at: '2025-06-01T00:00:00Z',
        contributor_name: 'Climate TRACE',
        contributor_id: 1,
        is_from_claim: false,
        is_verified: false,
        field_name: 'climate_trace',
        label: null,
        source_by: null,
        ...overrides,
    });

    const makeFacilityData = values => ({
        properties: {
            partner_fields: {
                climate_trace: values,
            },
        },
    });

    test('renders nothing when values array is empty', () => {
        const { container } = renderWithProviders(
            <PartnerFieldItem
                field={defaultField}
                facilityData={makeFacilityData([])}
            />,
        );
        expect(container.firstChild).toBeNull();
    });

    test('renders nothing when first value is falsy', () => {
        const { container } = renderWithProviders(
            <PartnerFieldItem
                field={defaultField}
                facilityData={makeFacilityData([null])}
            />,
        );
        expect(container.firstChild).toBeNull();
    });

    test('renders the primary value and label', () => {
        const { getByText } = renderWithProviders(
            <PartnerFieldItem
                field={defaultField}
                facilityData={makeFacilityData([makeValue()])}
            />,
        );

        expect(getByText('Climate Data')).toBeInTheDocument();
        expect(getByText('Scope 1 emissions: 100')).toBeInTheDocument();
    });

    test('uses label from top value when available', () => {
        const { getByText } = renderWithProviders(
            <PartnerFieldItem
                field={defaultField}
                facilityData={makeFacilityData([
                    makeValue({ value: 'CO2: 500t', label: 'Top Value Label' }),
                ])}
            />,
        );

        expect(getByText('Top Value Label')).toBeInTheDocument();
    });

    describe('when useProductionLocationPage is false', () => {
        test('renders FacilityDetailsItem even for multiple contributions', () => {
            const { queryByTestId } = renderWithProviders(
                <PartnerFieldItem
                    field={defaultField}
                    facilityData={makeFacilityData([
                        makeValue(),
                        makeValue({ contributor_id: 2 }),
                    ])}
                    useProductionLocationPage={false}
                />,
            );

            expect(queryByTestId('data-point')).not.toBeInTheDocument();
            expect(
                queryByTestId('contributions-drawer'),
            ).not.toBeInTheDocument();
        });
    });

    describe('when useProductionLocationPage is true', () => {
        const renderNewPage = (props = {}) =>
            renderWithProviders(
                <MemoryRouter>
                    <PartnerFieldItem
                        field={defaultField}
                        useProductionLocationPage
                        {...props}
                    />
                </MemoryRouter>,
            );

        test('renders FacilityDetailsItem for a single contribution', () => {
            const { queryByTestId } = renderNewPage({
                facilityData: makeFacilityData([makeValue()]),
            });

            expect(queryByTestId('data-point')).not.toBeInTheDocument();
            expect(
                queryByTestId('facility-details-detail'),
            ).toBeInTheDocument();
        });

        test('opens ContributionsDrawer when the more-entries button is clicked', () => {
            renderNewPage({
                facilityData: makeFacilityData([
                    makeValue(),
                    makeValue({ contributor_id: 2 }),
                ]),
            });

            expect(
                screen.queryByTestId('contributions-drawer'),
            ).not.toBeInTheDocument();

            fireEvent.click(
                screen.getByRole('button', { name: /1 more entry/i }),
            );

            expect(
                screen.getByTestId('contributions-drawer'),
            ).toBeInTheDocument();
        });

        test('shows the correct count on the more-entries button', () => {
            renderNewPage({
                facilityData: makeFacilityData([
                    makeValue(),
                    makeValue({ contributor_id: 2 }),
                    makeValue({ contributor_id: 3 }),
                ]),
            });

            expect(
                screen.getByRole('button', { name: /2 more entries/i }),
            ).toBeInTheDocument();
        });
    });
});
