import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
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
        });
    });

    describe('when useProductionLocationPage is true', () => {
        test('renders FacilityDetailsItem for a single contribution', () => {
            const { queryByTestId } = renderWithProviders(
                <PartnerFieldItem
                    field={defaultField}
                    facilityData={makeFacilityData([makeValue()])}
                    useProductionLocationPage
                />,
            );

            expect(queryByTestId('data-point')).not.toBeInTheDocument();
        });

        test('renders DataPoint for multiple contributions', () => {
            const { getByTestId } = renderWithProviders(
                <PartnerFieldItem
                    field={defaultField}
                    facilityData={makeFacilityData([
                        makeValue(),
                        makeValue({ contributor_id: 2 }),
                    ])}
                    useProductionLocationPage
                />,
            );

            expect(getByTestId('data-point')).toBeInTheDocument();
        });

        test('renders the label and value in DataPoint', () => {
            const { getByTestId } = renderWithProviders(
                <PartnerFieldItem
                    field={defaultField}
                    facilityData={makeFacilityData([
                        makeValue(),
                        makeValue({ contributor_id: 2 }),
                    ])}
                    useProductionLocationPage
                />,
            );

            expect(getByTestId('data-point-label')).toHaveTextContent(
                'Climate Data',
            );
            expect(getByTestId('data-point-value')).toHaveTextContent(
                'Scope 1 emissions: 100',
            );
        });

        test('uses label from top value when available in DataPoint', () => {
            const { getByTestId } = renderWithProviders(
                <PartnerFieldItem
                    field={defaultField}
                    facilityData={makeFacilityData([
                        makeValue({ label: 'Custom Label' }),
                        makeValue({ contributor_id: 2 }),
                    ])}
                    useProductionLocationPage
                />,
            );

            expect(getByTestId('data-point-label')).toHaveTextContent(
                'Custom Label',
            );
        });

        test('shows the sources button with correct label', () => {
            const { getByTestId } = renderWithProviders(
                <PartnerFieldItem
                    field={defaultField}
                    facilityData={makeFacilityData([
                        makeValue(),
                        makeValue({ contributor_id: 2 }),
                        makeValue({ contributor_id: 3 }),
                    ])}
                    useProductionLocationPage
                />,
            );

            const button = getByTestId('data-point-sources-button');
            expect(button).toBeInTheDocument();
            expect(button).toHaveTextContent('+2 data sources');
        });

        test('opens ContributionsDrawer when sources button is clicked', () => {
            renderWithProviders(
                <PartnerFieldItem
                    field={defaultField}
                    facilityData={makeFacilityData([
                        makeValue(),
                        makeValue({ contributor_id: 2 }),
                    ])}
                    useProductionLocationPage
                />,
            );

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
