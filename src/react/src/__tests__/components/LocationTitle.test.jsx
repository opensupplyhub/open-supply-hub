import React from 'react';
import { render, screen } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import ProductionLocationDetailsTitle from '../../components/ProductionLocation/Heading/LocationTitle/LocationTitle';

jest.mock('react-toastify', () => ({
    toast: jest.fn(),
}));

jest.mock('../../components/CopySearch', () => {
    function MockCopySearch({ children }) {
        return <>{children}</>;
    }
    return MockCopySearch;
});

jest.mock('../../components/Contribute/DialogTooltip', () => {
    function MockDialogTooltip({ childComponent }) {
        return <>{childComponent}</>;
    }
    return MockDialogTooltip;
});

const theme = createMuiTheme();

const renderLocationTitle = (props = {}) =>
    render(
        <MuiThemeProvider theme={theme}>
            <ProductionLocationDetailsTitle data={null} {...props} />
        </MuiThemeProvider>,
    );

describe('ProductionLocation LocationTitle', () => {
    test('renders without crashing when data is null', () => {
        renderLocationTitle({ data: null });

        expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
        expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent(/OS ID:/);
    });

    test('renders location name from data.properties.name', () => {
        const data = {
            properties: {
                name: 'Test Facility Name',
                os_id: 'CN2021250D1DTN7',
            },
        };

        renderLocationTitle({ data });

        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Test Facility Name');
    });

    test('renders OS ID from data.properties.os_id', () => {
        const data = {
            properties: {
                name: 'Test Facility',
                os_id: 'CN2021250D1DTN7',
            },
        };

        renderLocationTitle({ data });

        expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('OS ID: CN2021250D1DTN7');
    });

    test('shows Copy Link and Copy OS ID buttons when os_id is present', () => {
        const data = {
            properties: {
                name: 'Test Facility',
                os_id: 'CN2021250D1DTN7',
            },
        };

        renderLocationTitle({ data });

        expect(screen.getByRole('button', { name: /copy link/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /copy os id/i })).toBeInTheDocument();
    });

    test('does not show copy buttons when os_id is missing', () => {
        const data = {
            properties: {
                name: 'Test Facility',
            },
        };

        renderLocationTitle({ data });

        expect(screen.queryByRole('button', { name: /copy link/i })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: /copy os id/i })).not.toBeInTheDocument();
    });

    test('does not show copy buttons when data is null', () => {
        renderLocationTitle({ data: null });

        expect(screen.queryByRole('button', { name: /copy link/i })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: /copy os id/i })).not.toBeInTheDocument();
    });

    test('renders info button for OS ID tooltip', () => {
        const data = {
            properties: {
                name: 'Test',
                os_id: 'US123',
            },
        };

        renderLocationTitle({ data });

        expect(
            screen.getByRole('button', { name: /more information about os id/i }),
        ).toBeInTheDocument();
    });
});
