import React, { useState } from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';

import ContributionsDrawer from '../../components/ProductionLocation/ContributionsDrawer/ContributionsDrawer';

const theme = createMuiTheme();

const renderContributionsDrawer = (props = {}) =>
    render(
        <MemoryRouter>
            <MuiThemeProvider theme={theme}>
                <ContributionsDrawer
                    open
                    onClose={jest.fn()}
                    {...props}
                />
            </MuiThemeProvider>
        </MemoryRouter>,
    );

function DrawerWithTrigger() {
    const [open, setOpen] = useState(false);
    return (
        <MemoryRouter>
            <MuiThemeProvider theme={theme}>
                <button
                    type="button"
                    aria-label="Open drawer"
                    data-testid="open-drawer-trigger"
                    onClick={() => setOpen(true)}
                />
                <ContributionsDrawer
                    open={open}
                    onClose={() => setOpen(false)}
                />
            </MuiThemeProvider>
        </MemoryRouter>
    );
}

describe('ContributionsDrawer', () => {
    test('renders without crashing when open with required props', () => {
        renderContributionsDrawer({ open: true, onClose: () => {} });

        expect(screen.getByTestId('contributions-drawer')).toBeInTheDocument();
    });

    test('drawer content is visible when open is true', () => {
        renderContributionsDrawer({ open: true, onClose: () => {} });

        expect(screen.getByTestId('contributions-drawer')).toBeInTheDocument();
        expect(screen.getByTestId('contributions-drawer-title')).toBeInTheDocument();
    });

    test('calls onClose when close button is clicked', () => {
        const onClose = jest.fn();
        renderContributionsDrawer({ open: true, onClose });

        fireEvent.click(screen.getByTestId('contributions-drawer-close'));

        expect(onClose).toHaveBeenCalledTimes(1);
    });

    test('clicking trigger opens drawer and content is visible', () => {
        render(<DrawerWithTrigger />);

        expect(screen.queryByTestId('contributions-drawer')).not.toBeInTheDocument();

        fireEvent.click(screen.getByTestId('open-drawer-trigger'));

        expect(screen.getByTestId('contributions-drawer')).toBeInTheDocument();
        expect(screen.getByTestId('contributions-drawer-title')).toBeInTheDocument();
    });

    test('does not render contribution list when contributions is empty', () => {
        renderContributionsDrawer({
            open: true,
            onClose: () => {},
            contributions: [],
        });

        expect(
            screen.queryByTestId('contributions-drawer-list'),
        ).not.toBeInTheDocument();
    });

    test('does not render promoted card when promotedContribution is null', () => {
        renderContributionsDrawer({
            open: true,
            onClose: () => {},
            promotedContribution: null,
        });

        expect(
            screen.queryByTestId('contribution-card-promoted'),
        ).not.toBeInTheDocument();
    });

    test('renders contribution list and cards when contributions provided', () => {
        renderContributionsDrawer({
            open: true,
            onClose: () => {},
            contributions: [
                {
                    value: 'Value A',
                    sourceName: 'Source A',
                    date: '2022-01-01',
                    userId: 1,
                },
            ],
        });

        expect(screen.getByTestId('contributions-drawer-list')).toBeInTheDocument();
        expect(screen.getByTestId('contribution-card')).toBeInTheDocument();
    });

    test('does not count null promotedContribution as an anonymous contributor', () => {
        renderContributionsDrawer({
            open: true,
            onClose: () => {},
            fieldName: 'Address',
            promotedContribution: null,
            contributions: [
                {
                    value: '123 Main St',
                    sourceName: 'Source A',
                    date: '2022-01-01',
                    userId: 1,
                },
            ],
        });

        expect(
            screen.getByTestId('contributions-drawer-subtitle'),
        ).toHaveTextContent('1 organization has contributed data for Address');
    });

    test('renders promoted card when promotedContribution provided', () => {
        renderContributionsDrawer({
            open: true,
            onClose: () => {},
            promotedContribution: {
                value: 'Promoted Value',
                sourceName: 'Promoted Source',
                date: '2023-01-01',
                userId: 10,
            },
        });

        expect(
            screen.getByTestId('contribution-card-promoted'),
        ).toBeInTheDocument();
    });

    test('renders provenance block only for contributions that carry it', () => {
        renderContributionsDrawer({
            open: true,
            onClose: () => {},
            contributions: [
                {
                    value: 'Value A',
                    sourceName: 'Source A',
                    date: '2022-01-01',
                    userId: 1,
                    provenance: {
                        source_name: 'US EPA FRS',
                        source_link: 'https://example.com/dc?id=1',
                        information_source_type: 'air quality permit',
                        date_of_source: '2024-06',
                        ai_usage_notes: 'AI-extracted; human reviewed',
                    },
                },
                {
                    value: 'Value B',
                    sourceName: 'Source B',
                    date: '2022-02-01',
                    userId: 2,
                },
            ],
        });

        // Only the first contribution carries provenance.
        expect(
            screen.getAllByTestId('contribution-card-provenance'),
        ).toHaveLength(1);

        // Collapsed by default; expand the accordion to reveal the details.
        const toggle = screen.getByTestId('provenance-accordion-toggle');
        expect(toggle).toHaveAttribute('aria-expanded', 'false');
        fireEvent.click(toggle);
        expect(toggle).toHaveAttribute('aria-expanded', 'true');

        expect(screen.getByText('US EPA FRS')).toBeInTheDocument();
        expect(screen.getByText('air quality permit')).toBeInTheDocument();
        expect(
            screen.getByText('AI-extracted; human reviewed'),
        ).toBeInTheDocument();
        const link = screen.getByText('https://example.com/dc?id=1');
        expect(link).toHaveAttribute('href', 'https://example.com/dc?id=1');
        expect(link).toHaveAttribute('target', '_blank');
    });

    test('does not render provenance block when no contribution carries it', () => {
        renderContributionsDrawer({
            open: true,
            onClose: () => {},
            promotedContribution: {
                value: 'Promoted Value',
                sourceName: 'Promoted Source',
                date: '2023-01-01',
                userId: 10,
            },
            contributions: [
                {
                    value: 'Value A',
                    sourceName: 'Source A',
                    date: '2022-01-01',
                    userId: 1,
                },
            ],
        });

        expect(
            screen.queryByTestId('contribution-card-provenance'),
        ).not.toBeInTheDocument();
    });

    test('renders provenance on the promoted card when present', () => {
        renderContributionsDrawer({
            open: true,
            onClose: () => {},
            promotedContribution: {
                value: 'Promoted Value',
                sourceName: 'Promoted Source',
                date: '2023-01-01',
                userId: 10,
                provenance: { source_name: 'Operator website' },
            },
        });

        expect(
            screen.getByTestId('contribution-card-provenance'),
        ).toBeInTheDocument();
        fireEvent.click(screen.getByTestId('provenance-accordion-toggle'));
        expect(screen.getByText('Operator website')).toBeInTheDocument();
    });

    test('omits the other-sources section when there is a single contribution', () => {
        renderContributionsDrawer({
            open: true,
            onClose: () => {},
            fieldName: 'Operator',
            promotedContribution: {
                value: 'Equinix',
                sourceName: 'Source A',
                date: '2023-01-01',
                userId: 10,
            },
            contributions: [],
        });

        // The promoted contribution is shown on its own.
        expect(
            screen.getByTestId('contribution-card-promoted'),
        ).toBeInTheDocument();
        expect(
            screen.queryByTestId('contributions-drawer-list'),
        ).not.toBeInTheDocument();
        // No empty "Other Data Sources" section or multi-organization copy.
        expect(screen.queryByText('Other Data Sources')).not.toBeInTheDocument();
        // The subtitle reads in the singular.
        expect(
            screen.getByTestId('contributions-drawer-subtitle'),
        ).toHaveTextContent('1 organization has contributed data for Operator');
    });

    test('provenance accordion toggles open and closed', () => {
        renderContributionsDrawer({
            open: true,
            onClose: () => {},
            contributions: [
                {
                    value: 'Value A',
                    sourceName: 'Source A',
                    date: '2022-01-01',
                    userId: 1,
                    provenance: { source_name: 'US EPA FRS' },
                },
            ],
        });

        const toggle = screen.getByTestId('provenance-accordion-toggle');
        expect(toggle).toHaveAttribute('aria-expanded', 'false');
        expect(
            screen.getByTestId('provenance-accordion-expand-more'),
        ).toBeInTheDocument();

        fireEvent.click(toggle);
        expect(toggle).toHaveAttribute('aria-expanded', 'true');
        expect(
            screen.getByTestId('provenance-accordion-expand-less'),
        ).toBeInTheDocument();

        fireEvent.click(toggle);
        expect(toggle).toHaveAttribute('aria-expanded', 'false');
    });
});
