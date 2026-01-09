import React from 'react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import PartnerFieldsSection from '../../components/PartnerFields/PartnerFieldsSection/PartnerFieldsSection';

describe('PartnerFieldsSection component', () => {
    const renderComponent = ({ data, ...props }) =>
        renderWithProviders(<PartnerFieldsSection data={data} {...props} />);

    test('renders partner field section with title and learn more link', () => {
        const dataWithPartnerField = {
            properties: {
                partner_fields: {
                    climate_trace: [
                        {
                            value: { raw_value: 'Scope 1 emissions: 123' },
                            created_at: '2025-01-01T00:00:00Z',
                            updated_at: '2025-01-02T00:00:00Z',
                            contributor_name: 'Climate TRACE',
                            contributor_id: 1139,
                            is_from_claim: false,
                            is_verified: false,
                            field_name: 'climate_trace',
                            value_count: 1,
                            label: 'Climate TRACE Data',
                            source_by: '<p>Reported via Climate TRACE platform</p>',
                        },
                    ],
                },
            },
        };

        const { getByText } = renderComponent({
            data: dataWithPartnerField,
        });

        expect(getByText('New Pilot Data Integrations')).toBeInTheDocument();
        expect(getByText('Learn More')).toBeInTheDocument();
    });

    test('uses partner field label from top value when provided', () => {
        const partnerFieldLabel = 'Climate TRACE Data 2024';
        const dataWithPartnerField = {
            properties: {
                partner_fields: {
                    climate_trace: [
                        {
                            value: { raw_value: 'Scope 1 emissions: 123' },
                            created_at: '2025-01-01T00:00:00Z',
                            updated_at: '2025-01-02T00:00:00Z',
                            contributor_name: 'Climate TRACE',
                            contributor_id: 1139,
                            is_from_claim: false,
                            is_verified: false,
                            field_name: 'climate_trace',
                            value_count: 1,
                            label: partnerFieldLabel,
                            source_by: '<p>Reported via Climate TRACE platform</p>',
                        },
                    ],
                },
            },
        };

        const { getByText } = renderComponent({
            data: dataWithPartnerField,
        });

        expect(getByText(partnerFieldLabel)).toBeInTheDocument();
        expect(getByText('Scope 1 emissions: 123')).toBeInTheDocument();
    });

    test('falls back to generated partner field label when top value label missing', () => {
        const dataWithPartnerField = {
            properties: {
                partner_fields: {
                    climate_trace: [
                        {
                            value: { raw_value: 'Scope 2 emissions: 456' },
                            created_at: '2025-01-01T00:00:00Z',
                            updated_at: '2025-01-02T00:00:00Z',
                            contributor_name: 'Climate TRACE',
                            contributor_id: 1139,
                            is_from_claim: false,
                            is_verified: false,
                            field_name: 'climate_trace',
                            value_count: 1,
                            label: null,
                            source_by: null,
                        },
                    ],
                },
            },
        };

        const { getByText } = renderComponent({
            data: dataWithPartnerField,
        });

        expect(getByText('Climate Trace')).toBeInTheDocument();
        expect(getByText('Scope 2 emissions: 456')).toBeInTheDocument();
    });

    test('does not render when partner fields are empty', () => {
        const { container } = renderComponent({
            data: { properties: { partner_fields: {} } },
        });

        expect(container.firstChild).toBeNull();
    });

    test('renders multiple partner fields', () => {
        const dataWithMultiplePartnerFields = {
            properties: {
                partner_fields: {
                    climate_trace: [
                        {
                            value: { raw_value: 'Scope 1 emissions: 123' },
                            created_at: '2025-01-01T00:00:00Z',
                            updated_at: '2025-01-02T00:00:00Z',
                            contributor_name: 'Climate TRACE',
                            contributor_id: 1139,
                            is_from_claim: false,
                            is_verified: false,
                            field_name: 'climate_trace',
                            value_count: 1,
                            label: 'Climate Data',
                            source_by: null,
                        },
                    ],
                    emissions_data: [
                        {
                            value: { raw_value: 'Total emissions: 789' },
                            created_at: '2025-01-01T00:00:00Z',
                            updated_at: '2025-01-02T00:00:00Z',
                            contributor_name: 'Test Partner',
                            contributor_id: 1140,
                            is_from_claim: false,
                            is_verified: false,
                            field_name: 'emissions_data',
                            value_count: 1,
                            label: 'Emissions Info',
                            source_by: null,
                        },
                    ],
                },
            },
        };

        const { getByText } = renderComponent({
            data: dataWithMultiplePartnerFields,
        });

        expect(getByText('Climate Data')).toBeInTheDocument();
        expect(getByText('Scope 1 emissions: 123')).toBeInTheDocument();
        expect(getByText('Emissions Info')).toBeInTheDocument();
        expect(getByText('Total emissions: 789')).toBeInTheDocument();
    });
});
