import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';

import ProvenanceAccordion from '../../components/ProductionLocation/ContributionsDrawer/ProvenanceAccordion/ProvenanceAccordion';

const theme = createMuiTheme();

const fullProvenance = {
    source_name: 'US EPA FRS',
    source_link: 'https://example.com/dc?id=1',
    information_source_type: 'air quality permit',
    date_of_source: '2024-06',
    notes: 'inferred operator from website',
    data_collection_methodology: 'downloaded from source',
    ai_usage_notes: 'AI-extracted; human reviewed',
};

const renderProvenanceAccordion = (props = {}) =>
    render(
        <MuiThemeProvider theme={theme}>
            <ProvenanceAccordion
                data-testid="provenance-accordion"
                {...props}
            />
        </MuiThemeProvider>,
    );

describe('ProvenanceAccordion', () => {
    test('renders nothing when provenance is null', () => {
        renderProvenanceAccordion({ provenance: null });

        expect(
            screen.queryByTestId('provenance-accordion'),
        ).not.toBeInTheDocument();
    });

    test('renders nothing when provenance has no known non-empty fields', () => {
        renderProvenanceAccordion({
            provenance: { unknown_key: 'x', source_name: '' },
        });

        expect(
            screen.queryByTestId('provenance-accordion'),
        ).not.toBeInTheDocument();
    });

    test('renders the toggle with the container testid passed through', () => {
        renderProvenanceAccordion({ provenance: fullProvenance });

        expect(
            screen.getByTestId('provenance-accordion'),
        ).toBeInTheDocument();
        expect(
            screen.getByTestId('provenance-accordion-toggle'),
        ).toHaveTextContent('Source details');
    });

    test('is collapsed by default', () => {
        renderProvenanceAccordion({ provenance: fullProvenance });

        expect(
            screen.getByTestId('provenance-accordion-toggle'),
        ).toHaveAttribute('aria-expanded', 'false');
        expect(
            screen.getByTestId('provenance-accordion-expand-more'),
        ).toBeInTheDocument();
    });

    test('toggles open and closed on click', () => {
        renderProvenanceAccordion({ provenance: fullProvenance });
        const toggle = screen.getByTestId('provenance-accordion-toggle');

        fireEvent.click(toggle);
        expect(toggle).toHaveAttribute('aria-expanded', 'true');
        expect(
            screen.getByTestId('provenance-accordion-expand-less'),
        ).toBeInTheDocument();

        fireEvent.click(toggle);
        expect(toggle).toHaveAttribute('aria-expanded', 'false');
        expect(
            screen.getByTestId('provenance-accordion-expand-more'),
        ).toBeInTheDocument();
    });

    test('toggles with keyboard (Enter and Space)', () => {
        renderProvenanceAccordion({ provenance: fullProvenance });
        const toggle = screen.getByTestId('provenance-accordion-toggle');

        fireEvent.keyDown(toggle, { key: 'Enter' });
        expect(toggle).toHaveAttribute('aria-expanded', 'true');

        fireEvent.keyDown(toggle, { key: ' ' });
        expect(toggle).toHaveAttribute('aria-expanded', 'false');
    });

    test('shows all provided provenance fields with their labels when expanded', () => {
        renderProvenanceAccordion({ provenance: fullProvenance });
        fireEvent.click(screen.getByTestId('provenance-accordion-toggle'));

        expect(screen.getByText('Source:')).toBeInTheDocument();
        expect(screen.getByText('US EPA FRS')).toBeInTheDocument();
        expect(screen.getByText('Source type:')).toBeInTheDocument();
        expect(screen.getByText('air quality permit')).toBeInTheDocument();
        expect(screen.getByText('Date of source:')).toBeInTheDocument();
        expect(screen.getByText('2024-06')).toBeInTheDocument();
        expect(screen.getByText('Notes:')).toBeInTheDocument();
        expect(
            screen.getByText('Data collection methodology:'),
        ).toBeInTheDocument();
        expect(screen.getByText('AI usage notes:')).toBeInTheDocument();
        expect(
            screen.getByText('AI-extracted; human reviewed'),
        ).toBeInTheDocument();
    });

    test('omits fields that are not present', () => {
        renderProvenanceAccordion({
            provenance: { source_name: 'US EPA FRS' },
        });
        fireEvent.click(screen.getByTestId('provenance-accordion-toggle'));

        expect(screen.getByText('Source:')).toBeInTheDocument();
        expect(screen.queryByText('Notes:')).not.toBeInTheDocument();
        expect(screen.queryByText('Source link:')).not.toBeInTheDocument();
        expect(screen.queryByText('AI usage notes:')).not.toBeInTheDocument();
    });

    test('renders source_link as a safe external link', () => {
        renderProvenanceAccordion({ provenance: fullProvenance });
        fireEvent.click(screen.getByTestId('provenance-accordion-toggle'));

        const link = screen.getByText('https://example.com/dc?id=1');
        expect(link.tagName).toBe('A');
        expect(link).toHaveAttribute('href', 'https://example.com/dc?id=1');
        expect(link).toHaveAttribute('target', '_blank');
        expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });
});
