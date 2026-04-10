import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';

import DataPoint from '../../components/ProductionLocation/DataPoint/DataPoint';
import { STATUS_CLAIMED } from '../../components/ProductionLocation/DataPoint/constants';

const theme = createMuiTheme();

const renderDataPoint = (props = {}) =>
    render(
        <MemoryRouter>
            <MuiThemeProvider theme={theme}>
                <DataPoint
                    label="Test Label"
                    value="Test Value"
                    {...props}
                />
            </MuiThemeProvider>
        </MemoryRouter>,
    );

describe('DataPoint', () => {
    test('renders without crashing with required props', () => {
        renderDataPoint({ label: 'Name', value: 'Facility One' });

        expect(screen.getByTestId('data-point')).toBeInTheDocument();
    });

    test('renders label and value via data-testid', () => {
        renderDataPoint({ label: 'Name', value: 'Facility One' });

        const label = screen.getByTestId('data-point-label');
        const value = screen.getByTestId('data-point-value');
        expect(label).toBeInTheDocument();
        expect(label).toHaveTextContent('Name');
        expect(value).toBeInTheDocument();
        expect(value).toHaveTextContent('Facility One');
    });

    test('renders status chip when statusLabel is provided', () => {
        renderDataPoint({
            label: 'Name',
            value: 'Value',
            statusLabel: STATUS_CLAIMED,
        });

        const chip = screen.getByTestId('data-point-status-chip');
        expect(chip).toBeInTheDocument();
    });

    test('renders contributor as link with correct href when userId is provided', () => {
        renderDataPoint({
            label: 'Name',
            value: 'Value',
            contributorName: 'Acme Corp',
            userId: 42,
        });

        const contributor = screen.getByTestId('data-point-contributor');
        expect(contributor).toBeInTheDocument();
        const link = contributor.querySelector('a[href="/profile/42"]');
        expect(link).toBeInTheDocument();
    });

    test('does not render status chip when statusLabel is null', () => {
        renderDataPoint({ label: 'Name', value: 'Value' });

        expect(screen.queryByTestId('data-point-status-chip')).not.toBeInTheDocument();
    });

    test('does not render contributor section when contributorName is null', () => {
        renderDataPoint({
            label: 'Name',
            value: 'Value',
            userId: 1,
        });

        expect(screen.queryByTestId('data-point-contributor')).not.toBeInTheDocument();
    });

    test('does not render sources button when drawerData has no contributions', () => {
        renderDataPoint({
            label: 'Name',
            value: 'Value',
            drawerData: { contributions: [], title: 'Title', subtitle: null },
            onOpenDrawer: jest.fn(),
        });

        expect(screen.queryByTestId('data-point-sources-button')).not.toBeInTheDocument();
    });
});
