import React from 'react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import PartnerFieldItem from '../../components/ProductionLocation/PartnerSection/PartnerSectionItem/PartnerFieldItem';

describe('PartnerFieldItem component', () => {
    const defaultField = {
        fieldName: 'climate_trace',
        formatValue: undefined,
        label: 'Climate Data',
        partnerConfigFields: null,
    };

    const makeFacilityData = (values) => ({
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
        const facilityData = makeFacilityData([
            {
                value: 'Scope 1 emissions: 100',
                created_at: '2025-06-01T00:00:00Z',
                contributor_name: 'Climate TRACE',
                contributor_id: 1,
                is_from_claim: false,
                is_verified: false,
                field_name: 'climate_trace',
                label: null,
                source_by: null,
            },
        ]);

        const { getByText } = renderWithProviders(
            <PartnerFieldItem field={defaultField} facilityData={facilityData} />,
        );

        expect(getByText('Climate Data')).toBeInTheDocument();
        expect(getByText('Scope 1 emissions: 100')).toBeInTheDocument();
    });

    test('uses label from top value when available', () => {
        const facilityData = makeFacilityData([
            {
                value: 'CO2: 500t',
                created_at: '2025-06-01T00:00:00Z',
                contributor_name: 'Partner',
                contributor_id: 2,
                is_from_claim: false,
                is_verified: false,
                field_name: 'climate_trace',
                label: 'Top Value Label',
                source_by: null,
            },
        ]);

        const { getByText } = renderWithProviders(
            <PartnerFieldItem field={defaultField} facilityData={facilityData} />,
        );

        expect(getByText('Top Value Label')).toBeInTheDocument();
    });
});
