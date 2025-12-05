import React from 'react';
import { render, screen } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import UriReferenceProperty from '../../components/PartnerFields/UriReferenceProperty';

const theme = createMuiTheme();

const renderWithTheme = props =>
    render(
        <MuiThemeProvider theme={theme}>
            <UriReferenceProperty {...props} />
        </MuiThemeProvider>,
    );

describe('UriReferenceProperty', () => {
    const schemaProperties = {
        value: {
            type: 'string',
            title: 'Reference',
            description: 'See the partner-managed details.',
        },
        value_text: {
            type: 'string',
        },
    };

    it('renders description and uses partner display text with base url', () => {
        const value = {
            value: 'report-123',
            value_text: 'report-123',
        };
        const partnerConfigFields = {
            baseUrl: 'https://portal.example.com/reports',
            displayText: 'Open report',
        };

        renderWithTheme({
            propertyKey: 'value',
            value,
            schemaProperties,
            partnerConfigFields,
        });

        expect(
            screen.getByText('See the partner-managed details.'),
        ).toBeInTheDocument();

        const link = screen.getByRole('link', { name: 'Open report' });
        expect(link).toHaveAttribute(
            'href',
            'https://portal.example.com/reports/report-123',
        );
        expect(link).toHaveAttribute('target', '_blank');
        expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });

    it('falls back to absolute url text when display text is missing', () => {
        const value = {
            value: 'abc123',
        };
        const partnerConfigFields = {
            baseUrl: 'https://example.com/base/',
        };

        renderWithTheme({
            propertyKey: 'value',
            value,
            schemaProperties,
            partnerConfigFields,
        });

        const expectedHref = 'https://example.com/base/abc123';
        const link = screen.getByRole('link', { name: expectedHref });
        expect(link).toHaveAttribute('href', expectedHref);
    });

    it('ignores display text when base url is not provided and shows raw value', () => {
        const value = {
            value: 'local-id',
        };
        const partnerConfigFields = {
            displayText: 'Should not be used',
        };

        renderWithTheme({
            propertyKey: 'value',
            value,
            schemaProperties: {
                value: { type: 'string' },
                value_text: { type: 'string' },
            },
            partnerConfigFields,
        });

        const link = screen.getByText('local-id');
        expect(link).toHaveTextContent('local-id');
        expect(link).not.toHaveAttribute('href');
    });

    it('shows raw value text when neither base url nor display text are provided', () => {
        const value = {
            value: 'plain-value',
        };

        renderWithTheme({
            propertyKey: 'value',
            value,
            schemaProperties: {
                value: { type: 'string' },
                value_text: { type: 'string' },
            },
            partnerConfigFields: {},
        });

        const link = screen.getByText('plain-value');
        expect(link).toHaveTextContent('plain-value');
        expect(link).not.toHaveAttribute('href');
    });

    it('renders nothing when the field value is missing', () => {
        const { container } = renderWithTheme({
            propertyKey: 'value',
            value: {},
            schemaProperties,
            partnerConfigFields: {},
        });

        expect(container).toBeEmptyDOMElement();
    });
});


