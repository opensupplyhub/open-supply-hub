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
});
