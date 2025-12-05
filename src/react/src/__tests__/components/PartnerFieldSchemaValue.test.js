import React from 'react';
import { render, screen } from '@testing-library/react';
import PartnerFieldSchemaValue from '../../components/PartnerFields/PartnerFieldSchemaValue';

describe('PartnerFieldSchemaValue', () => {
    it('renders URI field with _text property as clickable link and skips _text', () => {
        const value = {
            url: 'https://example.com/audit-123',
            url_text: 'View Audit Report',
        };
        const jsonSchema = {
            type: 'object',
            properties: {
                url: {
                    type: 'string',
                    format: 'uri',
                },
                url_text: {
                    type: 'string',
                },
            },
        };

        render(<PartnerFieldSchemaValue value={value} jsonSchema={jsonSchema} />);

        const link = screen.getByRole('link', { name: 'View Audit Report' });
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute('href', 'https://example.com/audit-123');
        expect(link).toHaveAttribute('target', '_blank');
        expect(link).toHaveAttribute('rel', 'noopener noreferrer');

        const urlTextElements = screen.queryAllByText('View Audit Report');
        expect(urlTextElements.length).toBe(1); // Only in the link
    });

    it('renders URI field without _text property, using URI as link text', () => {
        const value = {
            mit_data_url: 'https://livingwage.mit.edu/locations/123',
        };
        const jsonSchema = {
            type: 'object',
            properties: {
                mit_data_url: {
                    type: 'string',
                    format: 'uri',
                },
            },
        };

        render(<PartnerFieldSchemaValue value={value} jsonSchema={jsonSchema} />);

        const link = screen.getByRole('link', {
            name: 'https://livingwage.mit.edu/locations/123',
        });
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute('href', 'https://livingwage.mit.edu/locations/123');
    });

    it('renders non-URI field with title as "Title: value" format', () => {
        const value = {
            internal_id: 'abc-123-xyz',
        };
        const jsonSchema = {
            type: 'object',
            properties: {
                internal_id: {
                    type: 'string',
                    title: 'Internal ID',
                },
            },
        };

        render(<PartnerFieldSchemaValue value={value} jsonSchema={jsonSchema} />);

        const text = screen.getByText('Internal ID: abc-123-xyz');
        expect(text).toBeInTheDocument();
        expect(text.tagName).toBe('SPAN');
    });

    it('renders mixed URI and non-URI fields correctly, skipping _text property', () => {
        const value = {
            url: 'https://example.com/report',
            url_text: 'View Report',
            internal_id: 'ABC-123',
            status: 'active',
        };
        const jsonSchema = {
            type: 'object',
            properties: {
                url: {
                    type: 'string',
                    format: 'uri',
                },
                url_text: {
                    type: 'string',
                },
                internal_id: {
                    type: 'string',
                    title: 'Internal ID',
                },
                status: {
                    type: 'string',
                    title: 'Status',
                },
            },
        };

        render(<PartnerFieldSchemaValue value={value} jsonSchema={jsonSchema} />);

        const link = screen.getByRole('link', { name: 'View Report' });
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute('href', 'https://example.com/report');

        expect(screen.getByText('Internal ID: ABC-123')).toBeInTheDocument();
        expect(screen.getByText('Status: active')).toBeInTheDocument();

        const urlTextElements = screen.queryAllByText('View Report');
        expect(urlTextElements.length).toBe(1);
    });

    it('renders uri-reference fields using partner configuration display text', () => {
        const value = {
            value: 'report-42',
            status: 'active',
        };
        const jsonSchema = {
            type: 'object',
            properties: {
                value: {
                    type: 'string',
                    format: 'uri-reference',
                    title: 'Partner Report',
                    description: 'Latest partner-provided report.',
                },
                value_text: {
                    type: 'string',
                },
                status: {
                    type: 'string',
                    title: 'Status',
                },
            },
        };
        const partnerConfigFields = {
            baseUrl: 'https://portal.example.com/reports',
            displayText: 'Open report',
        };

        render(
            <PartnerFieldSchemaValue
                value={value}
                jsonSchema={jsonSchema}
                partnerConfigFields={partnerConfigFields}
            />,
        );

        const link = screen.getByRole('link', { name: 'Open report' });
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute(
            'href',
            'https://portal.example.com/reports/report-42',
        );
        expect(screen.getByText('Status: active')).toBeInTheDocument();
    });

    it('falls back to default renderer when schema loses uri-reference format', () => {
        const value = {
            partner_field: 'report-42',
        };
        const jsonSchema = {
            type: 'object',
            properties: {
                partner_field: {
                    type: 'string',
                    title: 'Partner field',
                },
            },
        };
        const partnerConfigFields = {
            baseUrl: 'https://portal.example.com/reports',
            displayText: 'Open report',
        };

        render(
            <PartnerFieldSchemaValue
                value={value}
                jsonSchema={jsonSchema}
                partnerConfigFields={partnerConfigFields}
            />,
        );

        const text = screen.getByText('Partner field: report-42');
        expect(text).toBeInTheDocument();
        expect(text.tagName).toBe('SPAN');
    });

    it('returns primitive values when schema or object data is missing', () => {
        const { container } = render(
            <PartnerFieldSchemaValue value="Raw text value" />,
        );

        expect(container).toHaveTextContent('Raw text value');
    });
});
