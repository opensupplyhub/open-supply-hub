import React from 'react';
import { render, screen } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import UriReferenceProperty from '../../components/PartnerFields/FormatComponents/UriReferenceProperty/UriReferenceProperty';

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
        const link = screen.getByRole('link', { name: 'abc123' });
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

        const text = screen.getByText('local-id');
        expect(text).toHaveTextContent('local-id');
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

        const text = screen.getByText('plain-value');
        expect(text).toHaveTextContent('plain-value');
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

describe('UriReferenceProperty showTitle', () => {
    const GLEIF_CONFIG = {
        baseUrl: 'https://search.gleif.org/#/record/',
        displayText: '',
    };

    // Mirrors the live mit_living_wage partner field: a title that is an
    // internal join key, plus a display_text call to action.
    const MIT_CONFIG = {
        baseUrl: 'https://livingwage.mit.edu/counties/',
        displayText: 'View Living Wage Data for this County',
    };

    it('renders the schema title as a label when showTitle is set', () => {
        renderWithTheme({
            propertyKey: 'site_lei',
            value: { site_lei: '9845005AF685DA5C9059' },
            schemaProperties: {
                site_lei: {
                    type: 'string',
                    title: 'Site LEI',
                    format: 'uri-reference',
                    showTitle: true,
                },
            },
            partnerConfigFields: GLEIF_CONFIG,
        });

        expect(screen.getByText(/Site LEI:/)).toBeInTheDocument();

        const link = screen.getByRole('link', {
            name: '9845005AF685DA5C9059',
        });
        expect(link).toHaveAttribute(
            'href',
            'https://search.gleif.org/#/record/9845005AF685DA5C9059',
        );
    });

    it('does not render the title when showTitle is absent', () => {
        renderWithTheme({
            propertyKey: 'county_id',
            value: { county_id: '36001' },
            schemaProperties: {
                county_id: {
                    type: 'string',
                    title: 'County Id',
                    format: 'uri-reference',
                },
            },
            partnerConfigFields: MIT_CONFIG,
        });

        // Regression guard for mit_living_wage: its card must keep showing
        // only the call to action, never the internal join key title.
        expect(screen.queryByText(/County Id/)).not.toBeInTheDocument();

        const link = screen.getByRole('link', {
            name: 'View Living Wage Data for this County',
        });
        expect(link).toHaveAttribute(
            'href',
            'https://livingwage.mit.edu/counties/36001',
        );
    });

    it('does not render the title when showTitle is false', () => {
        renderWithTheme({
            propertyKey: 'site_lei',
            value: { site_lei: '9845005AF685DA5C9059' },
            schemaProperties: {
                site_lei: {
                    type: 'string',
                    title: 'Site LEI',
                    format: 'uri-reference',
                    showTitle: false,
                },
            },
            partnerConfigFields: GLEIF_CONFIG,
        });

        expect(screen.queryByText(/Site LEI:/)).not.toBeInTheDocument();
        expect(
            screen.getByRole('link', { name: '9845005AF685DA5C9059' }),
        ).toBeInTheDocument();
    });

    it('renders no label when showTitle is set but the title is missing', () => {
        renderWithTheme({
            propertyKey: 'site_lei',
            value: { site_lei: '9845005AF685DA5C9059' },
            schemaProperties: {
                site_lei: {
                    type: 'string',
                    format: 'uri-reference',
                    showTitle: true,
                },
            },
            partnerConfigFields: GLEIF_CONFIG,
        });

        expect(screen.queryByText(/:/)).not.toBeInTheDocument();
        expect(
            screen.getByRole('link', { name: '9845005AF685DA5C9059' }),
        ).toBeInTheDocument();
    });

    it('does not double the title when the field has no base url', () => {
        // Without a base url the link text already carries "Title: value",
        // so the label must not be added on top of it.
        renderWithTheme({
            propertyKey: 'site_lei',
            value: { site_lei: '9845005AF685DA5C9059' },
            schemaProperties: {
                site_lei: {
                    type: 'string',
                    title: 'Site LEI',
                    format: 'uri-reference',
                    showTitle: true,
                },
            },
            partnerConfigFields: {},
        });

        expect(
            screen.getByText('Site LEI: 9845005AF685DA5C9059'),
        ).toBeInTheDocument();
        expect(screen.queryAllByText(/Site LEI:/)).toHaveLength(1);
    });

    it('renders both description and label when both are present', () => {
        renderWithTheme({
            propertyKey: 'site_lei',
            value: { site_lei: '9845005AF685DA5C9059' },
            schemaProperties: {
                site_lei: {
                    type: 'string',
                    title: 'Site LEI',
                    description: 'Registered to this site',
                    format: 'uri-reference',
                    showTitle: true,
                },
            },
            partnerConfigFields: GLEIF_CONFIG,
        });

        expect(
            screen.getByText('Registered to this site'),
        ).toBeInTheDocument();
        expect(screen.getByText(/Site LEI:/)).toBeInTheDocument();
    });
});
