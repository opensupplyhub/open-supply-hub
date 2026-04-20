import React from 'react';
import { render, screen } from '@testing-library/react';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';

import PartnerFieldLabel from '../../components/PartnerFields/PartnerFieldLabel/PartnerFieldLabel';

const theme = createMuiTheme();

const renderPartnerFieldLabel = (props = {}) =>
    render(
        <MuiThemeProvider theme={theme}>
            <PartnerFieldLabel title="Test Title" {...props} />
        </MuiThemeProvider>,
    );

describe('PartnerFieldLabel', () => {
    test('renders without crashing', () => {
        const { container } = renderPartnerFieldLabel();
        expect(container.querySelector('span')).toBeInTheDocument();
    });

    test('displays the title followed by a colon', () => {
        renderPartnerFieldLabel({ title: 'Country' });
        expect(screen.getByText('Country:')).toBeInTheDocument();
    });

    test('applies the label class from withStyles', () => {
        const { container } = renderPartnerFieldLabel();
        const span = container.querySelector('span');
        expect(span.className).toMatch(/label/);
    });

    test('renders different titles correctly', () => {
        const { rerender } = render(
            <MuiThemeProvider theme={theme}>
                <PartnerFieldLabel title="Address" />
            </MuiThemeProvider>,
        );
        expect(screen.getByText('Address:')).toBeInTheDocument();

        rerender(
            <MuiThemeProvider theme={theme}>
                <PartnerFieldLabel title="Sector" />
            </MuiThemeProvider>,
        );
        expect(screen.getByText('Sector:')).toBeInTheDocument();
    });
});
