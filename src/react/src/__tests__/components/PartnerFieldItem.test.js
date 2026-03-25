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

    const renderItem = (props = {}) =>
        renderWithProviders(
            <MemoryRouter>
                <PartnerFieldItem field={defaultField} {...props} />
            </MemoryRouter>,
        );

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

    test('renders DataPoint for a single contribution', () => {
        const { getByTestId } = renderItem({
            facilityData: makeFacilityData([makeValue()]),
        });

        expect(getByTestId('data-point')).toBeInTheDocument();
    });

    test('does not show sources button for a single contribution', () => {
        const { queryByTestId } = renderItem({
            facilityData: makeFacilityData([makeValue()]),
        });

        expect(queryByTestId('data-point-sources-button')).not.toBeInTheDocument();
    });

    test('renders the label and value in DataPoint', () => {
        const { getByTestId } = renderItem({
            facilityData: makeFacilityData([makeValue()]),
        });

        expect(getByTestId('data-point-label')).toHaveTextContent('Climate Data');
        expect(getByTestId('data-point-value')).toHaveTextContent(
            'Scope 1 emissions: 100',
        );
    });

    test('uses label from top value when available', () => {
        const { getByTestId } = renderItem({
            facilityData: makeFacilityData([
                makeValue({ label: 'Custom Label' }),
            ]),
        });

        expect(getByTestId('data-point-label')).toHaveTextContent('Custom Label');
    });

    test('renders top contributor name as a profile link', () => {
        const { getByTestId } = renderItem({
            facilityData: makeFacilityData([makeValue({ contributor_id: 42 })]),
        });

        const contributor = getByTestId('data-point-contributor');
        expect(
            contributor.querySelector('a[href="/profile/42"]'),
        ).toBeInTheDocument();
    });

    test('shows the sources button with correct count for multiple contributions', () => {
        const { getByTestId } = renderItem({
            facilityData: makeFacilityData([
                makeValue(),
                makeValue({ contributor_id: 2 }),
                makeValue({ contributor_id: 3 }),
            ]),
        });

        const button = getByTestId('data-point-sources-button');
        expect(button).toBeInTheDocument();
        expect(button).toHaveTextContent('+2 data sources');
    });

    test('opens ContributionsDrawer when sources button is clicked', () => {
        renderItem({
            facilityData: makeFacilityData([
                makeValue(),
                makeValue({ contributor_id: 2 }),
            ]),
        });

        expect(
            screen.queryByTestId('contributions-drawer'),
        ).not.toBeInTheDocument();

        fireEvent.click(screen.getByTestId('data-point-sources-button'));

        expect(
            screen.getByTestId('contributions-drawer'),
        ).toBeInTheDocument();
    });
});
