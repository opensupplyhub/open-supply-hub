import React from 'react';
import { render, screen } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import ProductionLocationDetailsTitle from '../../components/ProductionLocation/Heading/LocationTitle/LocationTitle';

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
        expect(screen.getByText('Location Name')).toBeInTheDocument();
    });

    test('renders location name from data.properties.name', () => {
        const data = {
            properties: {
                name: 'Test Facility Name',
            },
        };

        renderLocationTitle({ data });

        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
            'Test Facility Name',
        );
    });

    test('renders empty heading when data.properties.name is missing', () => {
        const data = {
            properties: {},
        };

        renderLocationTitle({ data });

        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('');
    });
});
