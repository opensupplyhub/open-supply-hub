import React from 'react';
import { render, screen } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import ProductionLocationDetailsOsIdBadge from '../../components/ProductionLocation/Heading/osIdBadge/OsIdBadge';

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

const renderOsIdBadge = (props = {}) =>
    render(
        <MuiThemeProvider theme={theme}>
            <ProductionLocationDetailsOsIdBadge
                osId="CN2021250D1DTN7"
                {...props}
            />
        </MuiThemeProvider>,
    );

describe('ProductionLocationDetailsOsIdBadge', () => {
    test('renders without crashing', () => {
        renderOsIdBadge({ osId: 'CN2021250D1DTN7' });

        expect(screen.getByRole('heading', { level: 2 })).toBeInTheDocument();
    });

    test('renders OS ID label and value', () => {
        renderOsIdBadge({ osId: 'CN2021250D1DTN7' });

        expect(
            screen.getByRole('heading', { level: 2 }),
        ).toHaveTextContent('OS ID: CN2021250D1DTN7');
    });

    test('renders info button for OS ID tooltip', () => {
        renderOsIdBadge({ osId: 'CN2021250D1DTN7' });

        expect(
            screen.getByRole('button', {
                name: /more information about os id/i,
            }),
        ).toBeInTheDocument();
    });

    test('shows Copy Link and Copy OS ID buttons when osId is present', () => {
        renderOsIdBadge({ osId: 'CN2021250D1DTN7' });

        expect(
            screen.getByRole('button', { name: /copy link/i }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole('button', { name: /copy os id/i }),
        ).toBeInTheDocument();
    });

    test('does not show copy buttons when osId is empty', () => {
        renderOsIdBadge({ osId: '' });

        expect(screen.queryByRole('button', { name: /copy link/i })).not.toBeInTheDocument();
        expect(screen.queryByRole('button', { name: /copy os id/i })).not.toBeInTheDocument();
    });
});
